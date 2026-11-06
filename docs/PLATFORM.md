# Platform notes: PlayStation (PS1)

Pitfalls learned on earlier PS1 projects. Add to this file (and to the kit's copy) as you learn more.

## Disc
- Images are single-track MODE2/2352 `.bin` + `.cue` (Redump). Every rewritten Form 1 sector needs
  its EDC/ECC regenerated (`tools/disc.py` does it); emulators may accept bad ECC, real hardware
  and ODEs don't.
- Files are usually found by name through the ISO9660 directory, so a file that outgrows its slot
  can move into free sectors. XA audio (`.XA`, Form 2 sectors) is often addressed by LBA: never
  move it. Check for hard-coded LBAs in the EXE before relocating anything.
- Archives often have no slack; appending a grown entry at the end of the archive is usually fine
  when the loader reads the offset table.

## Code
- CPU: MIPS R3000A. **Branch and load delay slots**: the instruction after a branch always runs;
  a loaded value isn't visible to the very next instruction. `tools/mipsim.py` models both.
- The main EXE is a PS-X EXE (header 0x800 bytes, load address at +0x18). Overlays load at a fixed
  address; find the largest overlay's end and the heap start before letting overlays grow
  (`tools/bss_scan.py`).
- Debugging: **DuckStation is the debugger of record** - `tools/duck.py` attaches to your running DuckStation
  over its GDB server (Settings > Advanced; port 2345): break, watch write/read, step, regs, RAM. Accurate CD
  and timing, and you play to the screen first. It is the only one to trust when a result matters.
  `tools/redux.py` (headless PCSX-Redux) also has breakpoints, watchpoints and savestates, handy for boot
  and menu code without you, but its CD emulation fails some games (Virtual Pro Wrestling in a match):
  confirm the game plays in it before relying on it, and re-check anything surprising in DuckStation.
  `tools/emu.py` (ReARMed) is the fast headless player and has **no debugger**. A Linux DuckStation under
  WSLg hung at start-up and takes no input: not used. Leave no breakpoints behind (duck.py removes its own).
  Games load overlays over the same RAM (VPW: MOV.EXE, RESULT.EXE and the main code all at 0x80040000):
  check which overlay is resident before trusting an address.

## Text
- Text is often Shift-JIS drawn with the BIOS kanji ROM or a custom font. **Check whether ASCII is
  drawn at all**: many games only step two bytes per character, so English has to be stored as
  full-width SJIS (or the renderer hooked for a variable-width font).
- Memory-card save titles are shown by the BIOS: full-width SJIS, at most 64 bytes.
- Much menu text is images (TIM, or a game-specific container wrapping 4/8bpp images with CLUTs).

## Images
- TIM: 4bpp (16 colours) / 8bpp (256) with CLUTs in VRAM; colours are 15-bit BGR with an STP bit.
  Colour 0x0000 is transparent; keep transparent pixels transparent.

## Screenshots
- Take them at 1x internal resolution (DuckStation: resolution scale 1x), or scale upscaled shots
  down with `<kit>/release/shots.py --size WxH`. romhacking.net wants the platform's native resolution;
  record the PS1 list in `<kit>/release/shots.py` SIZES and here when a project first submits.
