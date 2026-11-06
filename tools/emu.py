#!/usr/bin/env python3
"""Headless PlayStation 1 runner: the PCSX ReARMed libretro core driven from Python.

  emu.py run <cue|bin|exe|iso> [--out DIR] [--states DIR] [--frames N] [--state-in F] [--state-out F]
             [--shot PNG] [--file STEPS.txt] [STEP...]
  emu.py setup                 where the core and the BIOS go, and whether they are there

No window, no compiler: ctypes loads the core, runs frames, presses buttons, saves screenshots
and savestates, and reads and writes the 2 MB of main RAM live. Software video, so it needs no GPU.

Files (outside every git repository - a BIOS is never committed):
  ~/.local/share/kit-emu/cores/pcsx_rearmed_libretro.so   from the libretro buildbot
      (https://buildbot.libretro.com/nightly/linux/x86_64/latest/pcsx_rearmed_libretro.so.zip)
  ~/.local/share/kit-emu/system/psx/scph5500.bin   optional (also scph5501.bin / scph5502.bin; they are
      linked into system/ for the core); without one the core uses its built-in HLE BIOS, which boots most games
      but skips the boot logo, shows no BIOS memory-card manager and can differ on odd titles.
      Set KIT_PS1_BIOS=hle to force HLE.

The core's dynarec crashes under ctypes, so the interpreter is the default (about real-time speed or
better on a desktop CPU); override with options={'pcsx_rearmed_drc': 'enabled'} in the library.

Steps - one per argument, or one per line in --file (# comments); the same words as the other
platforms' runners, so testing/drive.py step files work on all of them:
  wait N                      run N frames
  press BUTTONS [N] [xK]      hold buttons (CROSS CIRCLE SQUARE TRIANGLE L1 R1 L2 R2 L3 R3 START SELECT
                              UP DOWN LEFT RIGHT, joined by +; also A = CROSS, B = CIRCLE) for N frames
                              (default 4), then release for 12; xK: K times
  mash BUTTONS FRAMES [EVERY] press for 4 frames every EVERY (default 12), for FRAMES frames
  shot NAME                   screenshot -> OUT/NAME.png (a NAME ending .png is a path)
  save NAME / load NAME       savestate -> / <- STATES/NAME.state (a NAME ending .state is a path)
  peek ADDR [LEN]             print LEN bytes (default 1) of main RAM, also -> OUT/peek.txt
  poke ADDR BYTE[,BYTE...]    write bytes                          poke 8009A000 1 / poke 8009A000 0,0,$25
  dump REGION START LEN NAME  memory -> OUT/NAME.bin; REGION ram (2 MB), START an offset in it (hex)
  until ADDR BYTE [LIMIT]     run until the byte at ADDR is BYTE (at most LIMIT frames, default 600)
Addresses are hex CPU addresses (80010000, 0x80010000, $80010000; KSEG0/KSEG1 bits are ignored, so
80010000, A0010000 and 00010000 are the same byte); byte values, LEN and frame counts are DECIMAL
unless written $xx or 0x..

As a library: PS1(path) -> .run(frames), .press(...), .screenshot(path), .read(addr, n), .write(addr,
bytes), .memory('ram'), .save_state(), .load_state(bytes); run_steps(emu, steps, out, states) runs steps.
"""
import argparse
import ctypes as C
import os
import struct
import sys
import zlib
from pathlib import Path

HOME = Path(os.environ.get('KIT_EMU', Path.home() / '.local/share/kit-emu'))
CORE = HOME / 'cores' / 'pcsx_rearmed_libretro.so'
SYSTEM = HOME / 'system'
SAVES = HOME / 'saves'

# PlayStation pad button -> libretro joypad id
BUTTONS = {'CROSS': 0, 'A': 0, 'SQUARE': 1, 'SELECT': 2, 'START': 3, 'UP': 4, 'DOWN': 5, 'LEFT': 6,
           'RIGHT': 7, 'CIRCLE': 8, 'B': 8, 'TRIANGLE': 9, 'L1': 10, 'R1': 11, 'L2': 12, 'R2': 13, 'L3': 14,
           'R3': 15}

ENV_CB = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO_CB = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO_CB = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDIO_BATCH_CB = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_CB = C.CFUNCTYPE(None)
INPUT_CB = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG_CB = C.CFUNCTYPE(None, C.c_int, C.c_char_p)

RAM_SIZE = 0x200000           # main RAM, libretro memory id 2


class GameInfo(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]


class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]


class PS1:
    def __init__(self, cue, core=CORE, options=None):
        self._stage_bios()
        if not Path(core).exists():
            raise SystemExit(f'no core at {core} - run `emu.py setup` for where to get it')
        SAVES.mkdir(parents=True, exist_ok=True)
        self.lib = C.CDLL(str(core))
        # the dynarec segfaults under ctypes (no JIT memory map); the interpreter is fast enough headless
        self.opts = {'pcsx_rearmed_drc': 'disabled', **(options or {})}
        self.held = set()
        self.frame = None            # (bytes, width, height, pitch)
        self.fmt = 0                 # 0 0RGB1555, 1 XRGB8888, 2 RGB565
        self._sysdir = C.c_char_p(str(SYSTEM).encode())
        self._savedir = C.c_char_p(str(SAVES).encode())
        self._optvals = {k.encode(): C.c_char_p(v.encode()) for k, v in self.opts.items()}
        self._log = LOG_CB(lambda level, fmt: None)      # the core calls through this; it must exist
        cbs = [ENV_CB(self._env), VIDEO_CB(self._video), AUDIO_CB(lambda l, r: None),
               AUDIO_BATCH_CB(lambda d, n: n), POLL_CB(lambda: None), INPUT_CB(self._input)]
        self._keep = cbs
        self.lib.retro_set_environment(cbs[0])
        self.lib.retro_set_video_refresh(cbs[1])
        self.lib.retro_set_audio_sample(cbs[2])
        self.lib.retro_set_audio_sample_batch(cbs[3])
        self.lib.retro_set_input_poll(cbs[4])
        self.lib.retro_set_input_state(cbs[5])
        self.lib.retro_init()
        self.lib.retro_set_controller_port_device(0, 1)       # a plain digital pad
        info = GameInfo(str(cue).encode(), None, 0, None)
        self.lib.retro_load_game.restype = C.c_bool
        if not self.lib.retro_load_game(C.byref(info)):
            raise SystemExit(f'the core could not load {cue} (`emu.py setup`)')
        self.lib.retro_serialize_size.restype = C.c_size_t
        self.lib.retro_serialize.restype = C.c_bool
        self.lib.retro_unserialize.restype = C.c_bool
        self.lib.retro_get_memory_data.restype = C.c_void_p
        self.lib.retro_get_memory_size.restype = C.c_size_t

    # ---- callbacks
    def _env(self, cmd, data):
        if cmd == 27:                                  # GET_LOG_INTERFACE (the core crashes without it)
            C.cast(data, C.POINTER(C.c_void_p))[0] = C.cast(self._log, C.c_void_p).value
            return True
        if cmd == 9 or cmd == 31:                      # GET_SYSTEM_DIRECTORY / GET_SAVE_DIRECTORY
            C.cast(data, C.POINTER(C.c_char_p))[0] = (self._sysdir if cmd == 9 else self._savedir).value
            return True
        if cmd == 10:                                  # SET_PIXEL_FORMAT
            self.fmt = C.cast(data, C.POINTER(C.c_int))[0]
            return True
        if cmd == 15:                                  # GET_VARIABLE
            v = C.cast(data, C.POINTER(Variable))[0]
            val = self._optvals.get(v.key)
            if val is None:
                return False
            C.cast(data, C.POINTER(Variable))[0].value = val.value
            return True
        if cmd == 3:                                   # GET_CAN_DUPE
            C.cast(data, C.POINTER(C.c_bool))[0] = True
            return True
        if cmd == 17:                                  # GET_VARIABLE_UPDATE
            C.cast(data, C.POINTER(C.c_bool))[0] = False
            return True
        if cmd == 52:                                  # GET_CORE_OPTIONS_VERSION
            C.cast(data, C.POINTER(C.c_uint))[0] = 0
            return True
        return False

    def _video(self, data, w, h, pitch):
        if data:
            self.frame = (C.string_at(data, pitch * h), w, h, pitch)

    def _input(self, port, device, index, button):
        return 1 if port == 0 and device == 1 and button in self.held else 0

    # ---- control
    def run(self, frames=1):
        for _ in range(frames):
            self.lib.retro_run()

    def press(self, buttons, frames=4, release=4):
        self.held = {BUTTONS[b.upper()] for b in buttons.split('+') if b}
        self.run(frames)
        self.held = set()
        self.run(release)

    def save_state(self):
        n = self.lib.retro_serialize_size()
        buf = C.create_string_buffer(n)
        if not self.lib.retro_serialize(buf, C.c_size_t(n)):
            raise SystemExit('savestate failed')
        return buf.raw

    def load_state(self, data):
        buf = C.create_string_buffer(data, len(data))
        if not self.lib.retro_unserialize(buf, C.c_size_t(len(data))):
            raise SystemExit('loading the savestate failed')

    def rgb(self):
        """The current frame as (width, height, rows of (r, g, b))."""
        if not self.frame:
            raise SystemExit('no frame yet - run some frames first')
        data, w, h, pitch = self.frame
        rows = []
        for y in range(h):
            line = data[y * pitch:y * pitch + pitch]
            if self.fmt == 1:
                rows.append([(line[4 * x + 2], line[4 * x + 1], line[4 * x]) for x in range(w)])
            else:
                px = struct.unpack_from(f'<{w}H', line)
                if self.fmt == 2:
                    rows.append([((p >> 11) << 3, ((p >> 5) & 63) << 2, (p & 31) << 3) for p in px])
                else:
                    rows.append([(((p >> 10) & 31) << 3, ((p >> 5) & 31) << 3, (p & 31) << 3) for p in px])
        return w, h, rows

    def screenshot(self, path):
        w, h, rows = self.rgb()
        raw = b''.join(b'\0' + bytes(c for px in r for c in px) for r in rows)

        def chunk(t, d):
            return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                               + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
        return w, h

    # ---- memory
    def _stage_bios(self):
        """The core looks for scph5500/5501/5502.bin in the system directory; link the ones found in
        system/psx/ (or system/) there. Without any the core falls back to its HLE BIOS."""
        if os.environ.get('KIT_PS1_BIOS', '').lower() == 'hle':
            return
        for want in ('scph5500.bin', 'scph5501.bin', 'scph5502.bin'):
            link = SYSTEM / want
            src = SYSTEM / 'psx' / want
            if src.is_file() and not link.exists():
                link.symlink_to(Path('psx') / want)

    def _ram(self):
        p, n = self.lib.retro_get_memory_data(2), self.lib.retro_get_memory_size(2)
        if not p or n < RAM_SIZE:
            raise SystemExit(f'the core gives no main RAM (got {n:#x} bytes)')
        return (C.c_ubyte * n).from_address(p)

    def locate(self, addr, n=1):
        """(memory array, index) of CPU address `addr`; the KSEG bits (top 3) are ignored."""
        o = addr & 0x1FFFFFFF
        if o + n > RAM_SIZE:
            raise SystemExit(f'{addr:08X}+{n}: not main RAM (00000000-001FFFFF, or the same at 80000000/A0000000)')
        return self._ram(), o

    def read(self, addr, n=1):
        mem, o = self.locate(addr, n)
        return bytes(mem[o:o + n])

    def write(self, addr, data):
        mem, o = self.locate(addr, len(data))
        for k, b in enumerate(data):
            mem[o + k] = b

    def memory(self, region):
        """ram: the 2 MB of main RAM."""
        if region == 'ram':
            return bytes(self._ram()[:RAM_SIZE])
        raise SystemExit(f'unknown region {region!r} (ram)')


def num(s):
    """A decimal number, or hex written $xx / 0x.."""
    return int(s[1:], 16) if s.startswith('$') else int(s, 0)


def addr(s):
    """A hex address: 80010000, 0x80010000, $80010000."""
    return int(s.lstrip('$').removeprefix('0x').removeprefix('0X'), 16)


def clean_steps(steps):
    return [s.split('#')[0].strip() for s in steps if s.split('#')[0].strip()]


def run_steps(emu, steps, out, states=None, log=print):
    """Run steps (see the module help) on a PS1; screenshots, dumps and peek.txt go to `out`,
    savestates to `states` (default out/states)."""
    out = Path(out)
    states = Path(states) if states else out / 'states'
    for line in clean_steps(steps):
        cmd, *a = line.split()
        cmd = cmd.lower()
        try:
            if cmd == 'wait':
                emu.run(num(a[0]))
            elif cmd == 'press':
                k = num(a.pop()[1:]) if a[-1][:1] in 'xX' and a[-1][1:].isdigit() else 1
                for _ in range(k):
                    emu.press(a[0], num(a[1]) if len(a) > 1 else 4, 12)
            elif cmd == 'mash':
                frames, every = num(a[1]), num(a[2]) if len(a) > 2 else 12
                for _ in range(max(1, frames // every)):
                    emu.press(a[0], 4, max(0, every - 4))
            elif cmd == 'shot':
                f = Path(a[0]) if a[0].endswith('.png') else out / f'{a[0]}.png'
                emu.screenshot(f)
            elif cmd in ('save', 'load'):
                f = Path(a[0]) if a[0].endswith('.state') else states / f'{a[0]}.state'
                if cmd == 'save':
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_bytes(emu.save_state())
                else:
                    emu.load_state(f.read_bytes())
                    emu.run(2)
            elif cmd == 'peek':
                n = num(a[1]) if len(a) > 1 else 1
                text = f'peek {addr(a[0]):08X}: {emu.read(addr(a[0]), n).hex(" ")}'
                log(text)
                out.mkdir(parents=True, exist_ok=True)
                with open(out / 'peek.txt', 'a') as f:
                    f.write(text + '\n')
            elif cmd == 'poke':
                emu.write(addr(a[0]), bytes(num(v) for v in ','.join(a[1:]).split(',') if v))
            elif cmd == 'dump':
                m, start, n = emu.memory(a[0].lower()), addr(a[1]), num(a[2])
                out.mkdir(parents=True, exist_ok=True)
                (out / f'{a[3]}.bin').write_bytes(m[start:start + n])
            elif cmd == 'until':
                at, want, limit = addr(a[0]), num(a[1]), num(a[2]) if len(a) > 2 else 600
                while emu.read(at)[0] != want and limit > 0:
                    emu.run(1)
                    limit -= 1
                if limit <= 0:
                    log(f'until {at:08X} {want}: not reached')
            else:
                raise SystemExit(f'unknown step {line!r} (see emu.py --help)')
        except (IndexError, ValueError) as e:
            raise SystemExit(f'step {line!r}: {e} (see emu.py --help)')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run')
    p.add_argument('cue')
    p.add_argument('steps', nargs='*')
    p.add_argument('--file', '--script', dest='file')
    p.add_argument('--out', default='.')
    p.add_argument('--states')
    p.add_argument('--frames', type=int, default=0)
    p.add_argument('--shot')
    p.add_argument('--state-in')
    p.add_argument('--state-out')
    sub.add_parser('setup')
    a, rest = ap.parse_known_args(argv)       # steps may come after the options
    if any(r.startswith('-') for r in rest):
        ap.error(f'unrecognized arguments: {" ".join(rest)}')
    if a.cmd == 'setup':
        print(('ok      ' if CORE.exists() else 'MISSING ') + str(CORE))
        bios = [f for d in (SYSTEM / 'psx', SYSTEM) if d.is_dir() for f in d.glob('*')
                if f.name.lower().startswith('scph') and f.suffix.lower() == '.bin' and f.stat().st_size == 512 * 1024]
        print('ok      BIOS ' + ', '.join(f.name for f in bios) if bios else
              'none    no PS1 BIOS in ' + str(SYSTEM / 'psx') + ' - the core\'s HLE BIOS is used (scph5501.bin = US)')
        return
    emu = PS1(a.cue)
    if a.state_in:
        emu.load_state(Path(a.state_in).read_bytes())
    emu.run(a.frames)
    steps = (Path(a.file).read_text().splitlines() if a.file else []) + a.steps + rest
    run_steps(emu, steps, a.out, a.states)
    if a.shot:
        print(a.shot, emu.screenshot(a.shot))
    if a.state_out:
        Path(a.state_out).write_bytes(emu.save_state())


if __name__ == '__main__':
    main()
