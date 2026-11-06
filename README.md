# Virtual Pro Wrestling — English Translation

An English translation patch for **Virtual Pro Wrestling**, (1996, PlayStation, released only in Japan).

Everything the player reads is in English: all menus and options, the seven modes (Official Match,
Seven-Bout Blaze, Exhibition, Elimination, Tournament, League, Double Title Match), match banners,
tournament and league screens, belt screens, Memory Card prompts, the 60 wrestlers' name tiles, bio
boxes and move lists, and the champion lines. The hardest part was the text path: the game draws
Japanese from the console's BIOS font, so the patch adds an English half-width text routine and
redraws the text-in-picture graphics by hand. Wrestler names come in two variants, real names or the
game's own parody names.

**[See screenshots](docs/SCREENSHOTS.md)** of the patched game.

**[Player's guide](https://kactusken.github.io/Virtual-Pro-Wrestling-PSX-English/guide/)** - how to play, rules, all 60 wrestlers with stats and moves, and the secrets.

> **Status: v1.0.** Everything the player reads is translated and has been played through by the
> author, apart from a few screens never seen in game (listed under [Notes for players](#notes-for-players)).
> Please [report problems](#reporting-problems). [CHANGELOG.md](CHANGELOG.md) lists what's in each release.

## Downloads

Get the latest zip from the [Releases](../../releases) page. It contains four patches. Pick one:

| Patch | What you get |
|---|---|
| **Virtual Pro Wrestling (English) (Real Names)** | The translation with the real wrestlers' names. |
| **Virtual Pro Wrestling (English) (Parody Names)** | The translation with the game's own parody names. |
| **... (All Wrestlers Unlocked)**, either names | The same, with the eight secret wrestlers selectable from the start (Exhibition, Elimination, Tournament, League and Double Title modes). |

## How to patch

**[Follow the step-by-step guide](docs/HOW_TO_PATCH.md).** You patch the game with
[Delta Patcher](https://github.com/marco-calautti/DeltaPatcher/releases), then open the disc's
original `.cue`. Nothing needs renaming.

You need your own copy of the original Japanese disc. Disc images are not provided here.

- Game: *Virtual Pro Wrestling* (Japan), serial SLPS-00449.
- The image must match: `Virtual Pro Wrestling (Japan) (Track 01).bin`, 149998800 bytes, CRC32 `bcdc83c9`,
  SHA-1 `7431095ef7713e440a7e080bf92881eeaa9dc819`.

Other xdelta tools work too, such as [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) in a web browser (CD images;
it may not cope with a multi-GB DVD image) or `xdelta3` on the command line, but the patched files
must end up with the original file names. To keep several versions in one folder, use the patch's
`.cue` and name the patched files as it does.

Tested in [DuckStation](https://www.duckstation.org/).

## Notes for players

- **Names.** Choose the real-names or the parody-names patch. The parody romanisations are the translator's own readings of the game's Japanese parody names.
- **What's still in Japanese.** The staff credits, and decorative art that doesn't affect play (such as text on a wrestler's shirt). A few translated screens were never seen in game: the loading-screen headline rows and some rarely reached banners.
- **Saves.** Not tested against saves from the Japanese original; start a fresh save to be safe.
- **Hidden content.** See [docs/HIDDEN_CONTENT.md](docs/HIDDEN_CONTENT.md).

## Reporting problems

Open an [issue](../../issues) with:

- a screenshot,
- which patch you used,
- where you were: the mode and menu, or roughly what had just happened.

Text that is cut off, overlaps, or still shows Japanese is especially helpful.

## For ROM hackers and contributors

Everything needed to rebuild the patches from the original disc is in this repository: the
translated text, the patching code (Python 3, no dependencies for the build) and documentation of
the game's formats.

| Document | What's in it |
|---|---|
| [docs/HOW_TO_PATCH.md](docs/HOW_TO_PATCH.md) | The simplest way to patch your game, with no renaming |
| [docs/BUILDING.md](docs/BUILDING.md) | Setting up, building, making patches, and the checking tools |
| [docs/TRANSLATION.md](docs/TRANSLATION.md) | Text file formats, scope, style guide, glossary, and naming decisions |
| [docs/EDITING.md](docs/EDITING.md) | Editing the in-game text graphics |
| [docs/PATCHES.md](docs/PATCHES.md) | How each code patch works |
| [docs/TECHNICAL.md](docs/TECHNICAL.md) | The game's disc layout, archives, compression, data formats, and memory map |
| [docs/PLATFORM.md](docs/PLATFORM.md) | PS1 pitfalls for this kind of work |
| [docs/guide/](docs/guide/index.html) | The player's guide: how to play, controls, rules, all 60 wrestlers with stats and moves, secrets (GitHub Pages: `guide/`) |
| [docs/HIDDEN_CONTENT.md](docs/HIDDEN_CONTENT.md) | Unlockables, debug features, and unused and cut content |
| [tools/README.md](tools/README.md) | Every tool, what it's for and how to run it |

Quick start:

```sh
python3 tools/extract.py                 # unpack the disc in rom/ into extracted/
python3 build.py                         # -> build/Virtual Pro Wrestling (English).bin
python3 make_patches.py --version v1.0   # -> release/*.xdelta and a zip (needs xdelta3)
```

## AI disclosure

AI assisted with the translation.

## Legal

This is a non-commercial fan translation, not affiliated with or endorsed by the game's developers
or publishers. It contains no copyrighted game data that would let
anyone play without owning the game. The patches only work on your own copy of the disc.
Virtual Pro Wrestling and its contents belong to their respective owners. The Japanese text in this
repository is included for translation and reference.

The code in this repository is released under the [MIT License](LICENSE).
