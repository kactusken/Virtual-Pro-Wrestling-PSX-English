#!/usr/bin/env python3
"""Headless PlayStation 1 debugger runner: PCSX-Redux (-cli) driven by a Lua step runner.

  redux.py run <cue|exe> [--out DIR] [--states DIR] [--speed N] [--timeout SECS] [--file STEPS.txt]
                         [--stall SECS] [--no-debug] [--gdb [PORT]] [STEP...]
  redux.py setup               download and check the pinned PCSX-Redux build; show what is installed

emu.py (PCSX ReARMed) is the fast player for screenshots and play-tests; this one is the debugger:
exec / read / write breakpoints, registers, main RAM and VRAM, savestates, all from step files.
It boots with Redux's own OpenBIOS, so it needs no BIOS dump - but OpenBIOS is incomplete: Virtual Pro
Wrestling reads the disc fine at first, then its CD library fails (`CdlSetmode: DiskError`) and the game
resets itself in a loop after ~2000 frames. A real BIOS dump in ~/.local/share/kit-emu/system/ (any
scph*.bin, 512 KB; the folder system/psx/ too, scph5500 = Japan first) is passed with -bios automatically; KIT_PS1_BIOS=openbios forces OpenBIOS. No window,
no GPU (software renderer).

Files (outside every git repository):
  ~/.local/share/kit-emu/redux/    the pinned build (the AppImage, unpacked once into squashfs-root/)
  ~/.local/share/kit-emu/system/psx/scph5500.bin ...   optional BIOS dumps, never committed
  ~/.local/share/kit-emu/saves/redux-mc1.mcd, redux-mc2.mcd    its memory cards (not ~/.config)

Steps - one per argument, or one per line in --file (# comments); the same words as emu.py, so the
same step files drive both, plus the debugger steps below. The emulator runs only during waits and
runs; between steps it is paused, so what you read is exact.
  wait N                      run N frames
  press BUTTONS [N] [xK]      hold buttons (CROSS CIRCLE SQUARE TRIANGLE L1 R1 L2 R2 START SELECT UP DOWN
                              LEFT RIGHT, joined by +; A = CROSS, B = CIRCLE) N frames (default 4), then
                              release for 12; xK: K times.   No L3/R3.
  mash BUTTONS FRAMES [EVERY] press for 4 frames every EVERY (default 12), for FRAMES frames
  shot NAME                   the display as the GPU shows it -> OUT/NAME.png
  vshot NAME X Y W H [24]     a rectangle of VRAM (X, W in 16-bit pixels; W = pixels, or with 24: 24-bit pixels
                              starting at X) -> OUT/NAME.png.  FMV and 24-bit screens: vshot f 0 0 320 240 24
  vram NAME                   all of VRAM (2 MB, 1024 x 1024 16-bit words) -> OUT/NAME.bin
  save NAME / load NAME       savestate -> / <- STATES/NAME.state (about 22 MB; a NAME ending .state is a path)
  peek ADDR [LEN]             print LEN bytes (default 1) of main RAM, also -> OUT/peek.txt
  poke ADDR BYTE[,BYTE...]    write bytes                          poke 8009A000 1 / poke 8009A000 0,0,$25
  dump ram START LEN NAME     main RAM -> OUT/NAME.bin
  until ADDR BYTE [LIMIT]     run until the byte at ADDR is BYTE (at most LIMIT frames, default 600)
  break exec|read|write ADDR [LEN]
                              set a breakpoint (LEN bytes, default 4); any break ends the current wait/run
  clear                       remove all breakpoints
  run [FRAMES]                run until a breakpoint hits (at most FRAMES frames, default 600); prints
                              `BREAK <kind> at <addr> pc=<pc> frame=<n>`; the emulator stays paused there
  regs                        all registers (pc, r0..ra, lo, hi)
  reg NAME [VALUE]            read, or set, one register (pc, v0, a0, sp, ra ...)
Addresses are hex CPU addresses (80010000, 0x80010000, $80010000; KSEG bits ignored); byte values, LEN
and frame counts are DECIMAL unless written $xx or 0x.. Not available: single-stepping (Redux's Lua has
no step call - use `break exec` on the next instruction instead), a trace of every instruction.

Breakpoints need the interpreter and the debugger, which this runner turns on (about 5x slower than the
dynarec, still hundreds of frames per second at --speed 20). --no-debug runs the dynarec and ignores
break steps. --speed N is Redux's emulation speed (default 20; 1 = real time). Redux's own log goes to
OUT/redux.log; the `@@` result lines are what this prints. A Lua error ends the run with exit code 1.

--gdb [PORT] also starts Redux's GDB server (default port 3333) for gdbrsp.py; it only makes sense with
a long --timeout and a final `wait` step, since the run ends when the steps do.
"""
import argparse
import hashlib
import os
import threading
import time
import struct
import subprocess
import sys
import urllib.request
import zlib
from pathlib import Path

HOME = Path(os.environ.get('KIT_EMU', Path.home() / '.local/share/kit-emu'))
DIR = HOME / 'redux'
SAVES = HOME / 'saves'
LUA = Path(__file__).resolve().parent / 'redux_run.lua'

# The pinned build (distrib.app, "Linux x64 :: dev channel", build 526, changeset bc75bf66)
BUILD = 'bc75bf66d79b62bc5dbbee9953a0743996f41d6c'
URL = ('https://distrib.app/storage/assets/ad1/a5d/a6c/cb250637cda10dd55460bc0c31fe40690d732e5ff3fc7a56c80efad/'
       'PCSX-Redux-bc75bf66-linux-x86_64.zip')
ZIP_MD5 = '4862f084c2fe4e8f93f89a69cf9711df'
APPIMAGE = DIR / 'PCSX-Redux-HEAD-x86_64.AppImage'
ROOT = DIR / 'squashfs-root'
APPRUN = ROOT / 'AppRun'


def installed():
    return APPRUN.exists()


def setup(download=True):
    """Make sure the pinned build is downloaded, checked and unpacked; return True when it is ready."""
    if installed():
        return True
    if not download:
        return False
    DIR.mkdir(parents=True, exist_ok=True)
    zp = DIR / 'r.zip'
    if not zp.exists() or hashlib.md5(zp.read_bytes()).hexdigest() != ZIP_MD5:
        print(f'downloading PCSX-Redux {BUILD[:8]} (91 MB) from distrib.app ...', file=sys.stderr)
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        zp.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    if hashlib.md5(zp.read_bytes()).hexdigest() != ZIP_MD5:
        raise SystemExit(f'{zp}: checksum does not match the pinned build - not using it')
    import zipfile
    with zipfile.ZipFile(zp) as z:
        z.extract(APPIMAGE.name, DIR)
    APPIMAGE.chmod(0o755)
    subprocess.run([str(APPIMAGE), '--appimage-extract'], cwd=DIR, capture_output=True, check=True)
    return installed()


def png(path, w, h, rgb):
    raw = b''.join(b'\0' + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def convert_shots(out):
    """OUT/NAME.raw + NAME.meta (written by the Lua side) -> NAME.png; 16-bit data is the GPU's 15-bit BGR."""
    for meta in sorted(Path(out).glob('*.meta')):
        w, h, bpp = map(int, meta.read_text().split())
        raw = meta.with_suffix('.raw').read_bytes()
        if bpp == 24:
            rgb = raw[:w * h * 3]
        else:
            px = struct.unpack(f'<{w * h}H', raw[:w * h * 2])
            rgb = bytes(c for p in px for c in ((p & 31) << 3, ((p >> 5) & 31) << 3, ((p >> 10) & 31) << 3))
        png(meta.with_suffix('.png'), w, h, rgb)
        meta.unlink()
        meta.with_suffix('.raw').unlink()


def bios_file():
    """A PS1 BIOS dump (scph*.bin, 512 KB) in kit-emu/system/psx or system/, or None: Redux then uses OpenBIOS.
    The Japanese one (scph5500) first - the games this kit translates are Japanese."""
    if os.environ.get('KIT_PS1_BIOS', '').lower() == 'openbios':
        return None
    found = {f.name.lower(): f for d in (HOME / 'system' / 'psx', HOME / 'system') if d.is_dir() for f in d.glob('*')
             if f.name.lower().startswith('scph') and f.suffix.lower() == '.bin' and f.stat().st_size == 512 * 1024}
    for name in ('scph5500.bin', 'scph5501.bin', 'scph5502.bin'):
        if name in found:
            return found[name]
    return found[sorted(found)[0]] if found else None


def run(image, steps, out='.', states=None, speed=20, timeout=600, debug=True, gdb=None, stall=60, log=print):
    """Run `steps` (a list of step lines) on `image` in Redux; returns (exit code, the @@ lines)."""
    if not setup():
        raise SystemExit('PCSX-Redux is not installed - run `redux.py setup`')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    SAVES.mkdir(parents=True, exist_ok=True)
    script = out / 'redux-steps.txt'
    script.write_text('\n'.join(steps) + '\n')
    image = Path(image).resolve()
    cmd = [str(APPRUN), '-cli', '-testmode', '-softgpu', '-run',
           '-interpreter' if debug else '-dynarec'] + (['-debugger'] if debug else [])
    cmd += [f'-memcard1={SAVES / "redux-mc1.mcd"}', f'-memcard2={SAVES / "redux-mc2.mcd"}']
    bios = bios_file()
    cmd += ([f'-bios={bios}'] if bios else [])
    cmd += (['-gdb', f'-gdb-port={gdb}'] if gdb else [])
    cmd += ['-loadexe' if image.suffix.lower() == '.exe' else '-iso', str(image), f'-dofile={LUA}']
    env = dict(os.environ, KIT_STEPS=str(script), KIT_OUT=str(out), KIT_SPEED=str(speed),
               KIT_STATES=str(states or out / 'states'))
    p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    lines = []
    why = []
    t0 = last = time.monotonic()
    done = threading.Event()

    def watch():                  # a hard limit, and a stall limit: the Lua side prints a heartbeat every 300 frames
        while not done.wait(1):
            now = time.monotonic()
            if now - t0 > timeout:
                why.append(f'killed after {timeout} s')
            elif stall and now - last > stall:
                why.append(f'no frames for {stall} s: the game is stuck without vsync (interrupts off?)')
            if why:
                p.kill()
                return
    threading.Thread(target=watch, daemon=True).start()
    with open(out / 'redux.log', 'w') as lf:
        for line in p.stdout:
            lf.write(line)
            if line.startswith('@@'):
                last = time.monotonic()
                if line.startswith('@@ '):
                    lines.append(line[3:].rstrip())
                    log(lines[-1])
    p.wait()
    done.set()
    if why:
        raise SystemExit(f'redux: {why[0]} (see {out / "redux.log"})')
    convert_shots(out)
    script.unlink(missing_ok=True)
    code = p.returncode
    if code not in (0, 1) or not any(l.startswith('done') or l.startswith('ERROR') for l in lines):
        log(f'redux: ended without finishing the steps (exit {code}); see {out / "redux.log"}')
        code = code or 2
    return code, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run')
    p.add_argument('image')
    p.add_argument('steps', nargs='*')
    p.add_argument('--file', '--script', dest='file')
    p.add_argument('--out', default='.')
    p.add_argument('--states')
    p.add_argument('--speed', type=int, default=20)
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('--stall', type=int, default=60, help='give up after this many seconds without a frame (0: never)')
    p.add_argument('--no-debug', action='store_true')
    p.add_argument('--gdb', nargs='?', const=3333, type=int)
    sub.add_parser('setup')
    a, rest = ap.parse_known_args(argv)
    if any(r.startswith('-') for r in rest):
        ap.error(f'unrecognized arguments: {" ".join(rest)}')
    if a.cmd == 'setup':
        ok = setup()
        print(('ok      ' if ok else 'MISSING ') + str(APPRUN) + f'   (pinned build {BUILD[:8]})')
        b = bios_file()
        print(f'ok      BIOS {b.name}' if b else 'none    no PS1 BIOS in ' + str(HOME / 'system' / 'psx') + ' - OpenBIOS is used (incomplete)')
        return 0 if ok else 1
    steps = (Path(a.file).read_text().splitlines() if a.file else []) + a.steps + rest
    steps = [s.split('#')[0].strip() for s in steps if s.split('#')[0].strip()]
    code, _ = run(a.image, steps, a.out, a.states, a.speed, a.timeout, not a.no_debug, a.gdb, a.stall)
    return code


if __name__ == '__main__':
    sys.exit(main())
