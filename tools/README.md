# Tools

Everything is Python 3 and runs from the project folder or anywhere else; every tool has `--help`
(or prints its usage). Folder locations come from [paths.py](paths.py) and can be moved with the
folder options. `build.py`, `make_patches.py` and everything they import use only the standard
library; the tools marked *Pillow* or *capstone* need `.venv` (`pip install -r requirements.txt`).

Set up from the translation kit (version 50b7b18). Tools marked *game* are stubs to fill in.

## Used by the build

| Tool | What it does |
|---|---|
| [../build.py](../build.py) | builds the translated image (text steps, code patches, images, write-back) |
| [paths.py](paths.py) | every folder location and the folder options |
| [image.py](image.py) | the output image: fresh copy or fast restore from a journal; checksums |
| [disc.py](disc.py) | reads and writes files in the image (PS1; a cartridge ROM is one file - docs/PLATFORM.md) |
| [codepatch.py](codepatch.py) | applies code patch tables, checking the original bytes first |
| [catalog.py](catalog.py) | the image catalogue: which file the build uses, fingerprints, stale renders |
| [gfx.py](gfx.py) | *game*: exports the original images, imports the English ones |
| [pngio.py](pngio.py) | PNG reading and indexed PNG writing without dependencies |
| [blocks.py](blocks.py), [textdb.py](textdb.py) | message block files (`blocks.merge()` for dump tools: keeps English and hand comments); every translatable string as one list |
| [tim.py](tim.py) | PS1 TIM images: reading and PNG export |
| [mips_asm.py](mips_asm.py) | a small MIPS assembler for hooks (mind the delay slots) |

## Checking

| Tool | What it does |
|---|---|
| [check.py](check.py) | runs every check (`--quick` for the pre-commit hook, `--control` for a lossless-build proof) |
| [lint.py](lint.py) | text: leftover source text, control codes, line/char/byte limits, glossary |
| [status.py](status.py) | how far along the text and images are |
| [probe.py](probe.py) | the text areas on screen and their room, for the kit's `testing/drive.py` sweeps (stub: fill in per game) |
| [records.py](records.py) | fixed-record text tables (names, items, menus of records): `dump` the CSV, `verify` the layout, `measure` unknown data, build step - configure `TABLES` |
| [stepcheck.py](stepcheck.py) | run one build text step against `extracted/` (no image, nothing written) and list what it changed - for testing a step while the image is busy |

## Translating

| Tool | What it does |
|---|---|
| [fill_text.py](fill_text.py) | fills repeated strings from a source → English table |
| [render.py](render.py) | *Pillow*: automatic English renders, only redrawing what changed |
| [edit.py](edit.py) | *Pillow*: hand-edit workflow - start, check, approve, reset, sheets |
| [letter.py](letter.py) | *Pillow*: letters English into pictures `render.py` can't do (tinted or gradient lettering) from specs in `translation/letters/`, keeping the original palette; fonts in `fonts/` |
| [compare.py](compare.py) | *Pillow*: original \| English sheets |
| [contact.py](contact.py) | *Pillow*: every original image on labelled sheets |
| [rawview.py](rawview.py) | *Pillow*: raw data as pictures before its format is known - `view` one blob (depth, width or auto, tiles, palette), `scan` files and folders onto contact sheets |
| [pairs.py](pairs.py) | *game*: two-letter glyphs for games that count room in glyphs - choose the pairs that save most, stats, bitmap sheet (fill in the font hooks) |

## Releasing

| Tool | What it does |
|---|---|
| [../make_patches.py](../make_patches.py) | builds every variant, makes and re-verifies the patches, README.txt and the zip |

## Research

| Tool | What it does |
|---|---|
| [extract.py](extract.py) | unpacks the disc into `extracted/` and exports the images (*game*: `unpack()`) |
| [sjisscan.py](sjisscan.py) | finds Shift-JIS text in binary files |
| [vwffont.py](vwffont.py) | makes a variable-width bitmap font from a TTF as an editable text file (*Pillow*); its loader and pixel word wrap are standard library, for the build |
| [fontid.py](fontid.py) | *Pillow, numpy*: guesses a font's characters from a PNG sheet of its glyphs (per glyph, or the best JIS-ordered assignment) - a start for the table |
| [parts.py](parts.py) | bulk translation: `split` the untranslated text into part files for parallel translators, `check` a part (lint against the real limits), `status`, `merge` back (duplicates filled, blocks with errors skipped) |
| [asciiscan.py](asciiscan.py) | finds names the game keeps as plain ASCII (a HUD table) and spells differently from the names CSV (`LYGER` for Liger); run it on the original and on every build |
| [pagecheck.py](pagecheck.py) | reads guide pages as a player does: hedging ("not tested"), fact markers, author notes, template placeholders, empty brackets, bad `alt`, doubled headings; runs in `check.py` (`--allow-markers` or `private/guide.json` `{"fact_markers": true}` for an owner who wants markings) |
| [pagedata.py](pagedata.py) | fills the JSON data block of a reference page in `docs/` (`--check`); a game's data tool calls `pagedata.write()` |
| [guidedata.py](guidedata.py) | builds the wrestler guide's data (stats, dives, specials, moves by input group, heights/weights, promotions, select cells, unlocks, rings, music) from `extracted/` and `translation/names.json`, `guide_roster.json`, `guide_moves.tsv`, and fills `docs/guide/wrestlers/index.html` (`--check`, in `check.py`; with no page yet writes `build/work/guide_data.json`) |
| [emu.py](emu.py) | headless runner: PCSX ReARMed core via ctypes, steps (press, poke, until, shot, save/load, dump) and live main-RAM access; HLE BIOS unless an SCPH BIOS is installed; `emu.py setup` |
| [mipsdis.py](mipsdis.py) | *capstone*: disassembler with reference and call search |
| [mipsim.py](mipsim.py) | a small R3000 interpreter for offline hook tests (delay slots honoured) |
| [bss_scan.py](bss_scan.py) | estimates how far past its end a code module's memory use reaches |
| [gdbrsp.py](gdbrsp.py) | minimal GDB remote client for DuckStation: RAM, registers, run to an address |
