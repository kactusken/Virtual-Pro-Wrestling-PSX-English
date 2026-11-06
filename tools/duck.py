#!/usr/bin/env python3
"""Step files for your running DuckStation, over its GDB server: breakpoints, watchpoints, registers, RAM.

  duck.py run [--port N] [--hold] [--file STEPS.txt] [STEP...]     attach, run the steps, let the game go again
  duck.py status [--port N]                                       is DuckStation's GDB server answering?

This is the kit's PS1 debugger for accurate behaviour: you run DuckStation (Windows) and play to the screen
you want; this attaches, runs the steps and detaches. (emu.py = ReARMed, a fast headless player;
redux.py = PCSX-Redux, headless with real breakpoints, but its CD emulation fails Virtual Pro Wrestling in a
match. A Linux DuckStation under WSLg was tried and dropped: it hung at start-up and has no way to press
buttons.)

Set up once, in DuckStation: Settings > Advanced > enable the GDB server (port 2345). It only listens on
Windows' 127.0.0.1, so from WSL this script re-runs itself with the Windows Python (python.exe) - nothing to
do by hand. While attached the game is paused; the end of the run resumes it. Leftover breakpoints freeze a
game, so every break / watch removes its breakpoint when it stops. After rebuilding the disc image, close and
reopen the .cue in DuckStation (a reset reloads the old image).

Steps - one per argument, or one per line in --file (# comments). The same words as redux.py where they exist.
  wait SECONDS                run for SECONDS of real time, then pause again
  peek ADDR [LEN]             hex dump of RAM (default 64 bytes)         peek 80044868 16
  poke ADDR HEXBYTES          write RAM                                  poke 80070000 0102
  regs                        all registers and pc
  break ADDR [SECONDS]        run until pc == ADDR (default limit 60 s), print the registers; stays paused
  watch w|r|a ADDR [LEN] [SECONDS]
                              run until ADDR is written / read / accessed, print the registers (pc is just
                              past the instruction that did it)
  step [N]                    execute N instructions (default 1), print the registers
Addresses are hex CPU addresses (80010000, A0010000, 0x...); byte counts are decimal unless 0x.
A `break` on the very address the game is sitting at (an idle wait loop) did not re-trigger in testing: break
on a different address, or on the code that runs after it.
--hold leaves the game paused at the end (for the next `gdbrsp.py` command); the default resumes it.
A step that fails or times out ends the run with exit code 1 (and still resumes the game).
"""
import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gdbrsp  # noqa: E402


def port_open(port):
    try:
        socket.create_connection(('127.0.0.1', port), timeout=1).close()
        return True
    except OSError:
        return False


def in_wsl():
    try:
        return 'microsoft' in Path('/proc/version').read_text().lower()
    except OSError:
        return False


def via_windows(argv):
    """Re-run this script with the Windows Python (DuckStation's GDB server is on Windows' localhost)."""
    def win(p):
        return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True, check=True).stdout.strip()
    args = []
    it = iter(argv)
    for a in it:
        args.append(a)
        if a in ('--file', '--script'):
            args.append(win(Path(next(it)).resolve()))
    cmd = ['python.exe', win(Path(__file__).resolve())] + args
    return subprocess.run(cmd, cwd='/mnt/c', env=dict(os.environ, KIT_DUCK_WINDOWS='1')).returncode


def hexaddr(s):
    return int(s.lower().removeprefix('0x').lstrip('$'), 16)


def run_steps(steps, port=2345, hold=False, log=print):
    """Attach to the GDB server on `port` and run step lines; returns the output lines. SystemExit on a bad step."""
    g = gdbrsp.Gdb(port=port)
    out = []

    def say(text):
        out.append(text)
        log(text)

    def regs():
        say('regs ' + ' '.join(f'{n}={v:08x}' for n, v in g.regs().items()))
    try:
        for line in steps:
            a = line.split()
            op = a[0].lower()
            try:
                if op == 'wait':
                    g.resume_nowait()
                    time.sleep(float(a[1]))
                    g.interrupt()
                elif op == 'peek':
                    n = int(a[2], 0) if len(a) > 2 else 64
                    d = g.read(hexaddr(a[1]), n)
                    for i in range(0, len(d), 16):
                        say(f'peek {hexaddr(a[1]) + i:08x}: {d[i:i + 16].hex(" ")}')
                elif op == 'poke':
                    g.write(hexaddr(a[1]), bytes.fromhex(a[2]))
                elif op == 'regs':
                    regs()
                elif op == 'break':
                    say('BREAK ' + g.run_to(hexaddr(a[1]), float(a[2]) if len(a) > 2 else 60))
                    regs()
                elif op == 'watch':
                    n = int(a[3], 0) if len(a) > 3 else 4
                    say('WATCH ' + g.watch(a[1], hexaddr(a[2]), n, float(a[4]) if len(a) > 4 else 60))
                    regs()
                elif op == 'step':
                    for _ in range(int(a[1]) if len(a) > 1 else 1):
                        g.step()
                    regs()
                else:
                    raise SystemExit(f'unknown step {line!r} (see duck.py --help)')
            except (IndexError, ValueError, KeyError) as e:
                raise SystemExit(f'step {line!r}: {e!r} (see duck.py --help)')
            except socket.timeout:
                raise SystemExit(f'step {line!r}: no stop within the time limit (the breakpoint was removed)')
    finally:
        if hold:
            g.s.close()
        else:
            g.detach()
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run')
    p.add_argument('steps', nargs='*')
    p.add_argument('--file', '--script', dest='file')
    p.add_argument('--port', type=int, default=int(os.environ.get('KIT_GDB_PORT', 2345)))
    p.add_argument('--hold', action='store_true')
    p = sub.add_parser('status')
    p.add_argument('--port', type=int, default=int(os.environ.get('KIT_GDB_PORT', 2345)))
    a, rest = ap.parse_known_args(argv)
    if any(r.startswith('-') for r in rest):
        ap.error(f'unrecognized arguments: {" ".join(rest)}')
    if in_wsl() and not os.environ.get('KIT_DUCK_WINDOWS') and not port_open(a.port):
        return via_windows(argv)
    if a.cmd == 'status':
        print('DuckStation GDB server answering on port %d' % a.port if port_open(a.port) else
              'nothing on port %d - enable the GDB server in DuckStation (Settings > Advanced)' % a.port)
        return 0 if port_open(a.port) else 1
    steps = (Path(a.file).read_text().splitlines() if a.file else []) + a.steps + rest
    steps = [s.split('#')[0].strip() for s in steps if s.split('#')[0].strip()]
    if not port_open(a.port):
        print(f'nothing on port {a.port}: start DuckStation and enable its GDB server (Settings > Advanced)', file=sys.stderr)
        return 1
    try:
        run_steps(steps, a.port, a.hold)
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
