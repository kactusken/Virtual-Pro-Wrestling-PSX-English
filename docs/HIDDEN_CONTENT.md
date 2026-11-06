# Hidden content

Unlockables, debug features, button codes, cut and unused content. Every find says how sure it
is:

- *verified in game* - seen in an emulator (with the date, and the build or code used to get there)
- *from the code* - read in the disassembly, not seen running
- *from the data* - in the game's files or tables, whether or not the code uses it
- *from a guide* / *from fans* - a published source, not yet matched with the code

Addresses are PlayStation RAM addresses of the original Japanese disc (SLPS-00449). The
SHINKOU.EXE overlay loads at 0x8001d000 (file offset = address - 0x8001d000 + 0x800); MAIN.EXE
addresses are as loaded. "Seen headless" means seen in the project's headless emulator with a
RAM poke, not played through. Marked *verified in game* where the owner played it.

**Prior art (2026-11-05).** Japanese Wikipedia and one fan blog list the eight hidden
wrestlers and a rough unlock path (below). No cheat codes, button codes, debug menu or test
mode for SLPS-00449 were found online; The Cutting Room Floor's page could not be fetched
automatically and has not been read. The Western sibling, WCW vs. the World, has a cheat-database
"Enable All Characters" code that writes 0xFFFF to a progress word, the same kind of flag found
here. Everything else below is new.

## Contents
- [Secret wrestlers](#secret-wrestlers) · [Debug display](#debug-display) · [Costume select](#costume-select) · [Rings](#rings) · [Ring set](#ring-set-d0617dat) · [Shared animation bank](#shared-animation-bank-ks0704bin) · [Staff roll](#staff-roll) · [Dead scratch-pad viewer](#dead-scratch-pad-viewer) · [Unused intro cut](#unused-intro-cut) · [Unused music and sound](#unused-music-and-sound) · [Smaller leftovers](#smaller-leftovers) · [Searched and not found](#searched-and-not-found) · [How to see it yourself](#how-to-see-it-yourself)

## Secret wrestlers
*verified in game (2026-11-06: all wrestlers selectable with `build.py --unlocks all-wrestlers`; the owner also confirmed the unlock path below); the code addresses are from the code, the names and rough path from fans*

The game has 60 wrestlers; the select screen shows 52 at the start. The other eight (ids 53-60)
are hidden: Strongest Toki (ストロンゲスト闘魂), Monster Bull Dog, Mr. God, Teddy Lang, The
Masquerade, Shotgun Boy, Super Jaguar and Andy the Gigant (names as listed by the fans; the
id-to-name order is still to be matched).

- **Grid.** The select grid is a table at SHINKOU 0x8005d73c, 8 bytes per row. Normal cells hold
  ids 1-52. The extra cells (row 14, columns 1-6, and row 1, columns 1 and 6) hold 0x80, and the
  cursor skips them.
- **Reveal.** The routine at 0x8002e070 fills those cells from bit *i* of the progress word at
  0x800a3974. Bits 0-7 reveal ids 56, 58, 57, 55, 54, 53, 59, 60. It only does so when the mode id
  (0x8006d86c) is 2 or more, so the secret wrestlers never show in Official Match or Seven-Bout
  Blaze.
- **Only writer.** 0x80025214, called by 0x80024fc0 after an Official Match challenge is won.
  It sets the bit for that organisation in the progress word and in the beaten wrestler's record
  byte at 0x800a390c[id-1]. The word is saved to the Memory Card.
- **How to unlock.** Win the Official Match challenge for each of the six organisations: they give
  ids 56, 58, 57, 55, 54, 53 in that order of organisation. Once one wrestler's record byte shows
  all six cleared (0x3f), a seventh opponent, SUPER HEAVY or SUPER Jr. (class table at 0x8005d664),
  is added at 0x80029b18. Beating the heavyweight one unlocks id 60, the junior one id 59.
- **Headless proof.** Poking the progress word to 0xFF filled the table; moving the cursor onto row 14
  showed a new portrait and selected id 0x38; poking the record bytes made SUPER HEAVY and SUPER Jr.
  appear.
- Fans describe the same path in rougher terms (a hidden wrestler appears as the sixth opponent,
  which one depends on your organisation; clearing every organisation opens a hidden one).

## Debug display
*seen headless (2026-11-05, RAM poke)*

A debug flag at MAIN 0x80074d6c is cleared at start and never set by the game. Set it, and the
match draws the camera values (VPX/VPY/VPZ) and each wrestler's PAT, ANGLE, FRAME, HP, MP, HIT_B and
BODY0-5 values over the screen, and skips two HUD draws. It has to be written every frame through
the match load. Not reachable in the original game, and not in any release patch.

## Costume select
*verified in game (2026-11-06: START on the wrestler select gives the other costume); the mechanism is from the code, the texture comparison from the data*

Picking a wrestler with START instead of Circle on the select screen sets a flag on the slot; the id
gets 0x80 ORed in (SHINKOU 0x8002470c), and MAIN strips it (0x8001f8d0) and loads the second texture set
(`TEX/T30_2` or `T60_2`, `TAnn_2.DAT`, table at MAIN 0x8006af7c) instead of `TAnn_1` (table 0x8006a9dc).

Every one of the 60 wrestlers has a second set. Each `TAnn_k.DAT` is nine TIMs: five 256x256 body pages (VRAM x 640-896), a
256x192 face page, then the name banner, move list and name tag (the first image block's length field has garbage in its
high bits, so a plain TIM scanner skips it). Each page has two 16-colour palettes. All 240 wrestler models
(`TMD/TMD30|60_1-4`, 60 wrestlers x 4) use exactly 24 page/palette combinations, 12 per set (set 1 at CLUT x 0, set 2 at
y 256 with CLUT x 16), so **no texture page or palette on the disc is unused by the models**; the `_2` set differs from `_1`
for every wrestler in at least one palette. How much, over the six model pages (share of pixels that differ):
- **13 full alternate costumes with their own select portrait** (SHINKOU_129-141, id list at SHINKOU 0x8005d704):
  ids 1, 9, 35, 38, 39, 40, 42, 43, 45, 49, 51, 52, 54. Of these, 1, 9, 39, 40, 42, 45, 49 and 54 change 50-95% of the
  pixels; 38, 43, 51 and 52 change 19-39%; 35 changes only 4% (a palette change of the mask: red to green). Different mask
  colours and designs, face paint, sunglasses (38), a headband reading "LEAGUN" (49), a hiragana poem on the face (42).
- **Wrestlers with a real change but no new portrait**, judged on the face page: 6, 53, 16, 15, 5, 14 and 22 (51-99% of
  that page: different tights or trunks, skin tone, or face; 22's face differs).
- **Palette-only or minor changes** (2-5% of the pixels over all pages): ids 3, 18, 35 (above), 56 and others.
Sheets: `private/work/hidden/img/tex_pairs_sheet.png`, `tex_more.png` (face page only; not published, game art).

## Shared animation bank (KS0704.BIN)
*from the code; decoder checked against emulator RAM (2026-11-06): 1,117 of 1,200 sampled frames matched exactly on all 19 parts*

`KS0704.BIN` is not hidden content but the shared animation set. MAIN loads it to 0x80102000: 101 pointers, then 101 animations
(ids 0-100); ids from 0x100 up come from each wrestler's own `DAnn.DAT`. Both use one format: a 16-bit frame count, a bias
mask, a table of per-part bit widths, a full first frame (19 skeleton parts, 12-bit angles) and a stream of bit-packed deltas.
(Decoder, format notes and the id table are in `private/work/hidden/`, not published.)

**11 of the 101 animations are never started by any code**: ids 2, 17, 29, 30, 42, 65, 67, 90, 91, 92, 93 (constant ids only; a
run-time computed id would not be seen). Played back in the engine they are: 91 thrown backwards, flips and lands on the mat;
42 a jump; 29 both arms reaching forward; 30 one arm raised; 17 a short lunge; 65 and 67 walking toward the ropes (their
neighbours 64 and 66 are used); 90, 92 and 93 small steps; 2 a stance-like loop. The other 90 are used, for example 0 = stance,
0x30-0x33 and 0x3A = stance variants (0x3A special), 22/23 = Circle tap close/far, 12 = top-rope climb.

## Ring set (D0617.DAT)
*from the code, cross-checked headless (2026-11-06)*

`D0617.DAT` (0xEFF0 bytes, loaded by MAIN to 0x800F1000) is the match's ring set, and every byte is accounted for: four rope models
(one per side, 3 ropes each, identical grey), 12 rope "push" records of 232 bytes (which vertices move when a wrestler hits the
ropes; chosen by where he hits: centre or near either end), corner posts with red pads, the arena (stands, back wall, barriers),
the ring (mat, apron, skirt), a script that builds the 19-part wrestler skeleton, and 20 flat floor quads (likely body-part shadows).
Unused parts: a 6-vertex wall panel (1382 x 144, using the arena texture; nothing references it, probably a dropped near-side
barrier or backdrop), floor quads 16-19 (listed in both tables, but the draw loops stop at 16), and some dead script data (the 19
starting part positions, a camera and a projection entry). Nothing to patch.

## Staff roll
*from the code*

The staff credits (STAFF.EXE) play only after the last bout of the SUPER HEAVY / SUPER Jr.
challenge (MAIN 0x8002ac78 -> 0x8001f024).

## Dead scratch-pad viewer
*from the code*

MAIN 0x8001f1d8 is a debug viewer ("scratch pad data": pad_id, mode, winner, HP, the 1p/2p slots)
that nothing calls.

## Unused intro cut
*from the data, seen headless (2026-11-05, file name swapped in RAM)*

`MOV/VPW10SON.STR` is an earlier cut of the intro movie that MOV.EXE never plays (it plays
VPW12SON). It has a shot the final cut dropped: a spinning ring whose mat carries the Asmik logo and
"VIRTUAL PRO-WRESTLING", and a different arena sign. Some frames decode as stripes through MOV.EXE.
WCW vs. the World carries the same file. `VPW12OUT.STR` is a second encode of the final intro that
is also never played.

## Unused music and sound
*from the code / from the data*

- Two CD tracks are never requested: track 8 (71 s) and track 11 (11 s). Tracks 2 and 18 are
  byte-identical to track 6. (The code plays track n+3 for sound number n.)
- Wrestler DA22 (the Giant Baba parody) has his own match music, track 9.
- 19 of the 87 samples in `SE_MAIN.VB` are used by no sound program; `SE_MAIN.SEP` is never loaded.

## Smaller leftovers
*from the data*

- `MOV/4BGM06.DA`: a 33.9 MB copy of music track 5 inside the data track, named by no code.
- 54 wrestler files carry 4224 identical bytes of a throw-8 animation template that no animation uses.
- SHINKOU_008, the 開発中 ("in development") placeholder portrait, is portrait 0; no wrestler has id 0.

## Rings
*from the code (MAIN ring loader 0x8001f8a0, table at 0x8006b9cc, 25 entries of 20 bytes), run in the simulator for every counter value and Mat Select setting (2026-11-06); the Mat Select list and its stored value seen headless; Random giving different mats verified in game (2026-11-06); that it never gives the SUPER mats, and the odds, are from the code and simulator only*

All 25 `RING/*.DAT` mats can be loaded, but not all from the Mat Select screen:
- **The six named mats** (NSW, EWF, WOU, DAW, ILW, IAWA) each pick a mat; for all but ILW the game chooses randomly between two
  files (`rand & 1`): NEW01/02, EWF01/02, WOU01/02, DAW01/02, IAW01/02. ILW has one file, ILW01. That is 11 files.
- **Random** (Mat Select value 0; the list is Random, NSW, EWF, WOU, DAW, ILW, IAWA = low nibble 0-6 of the rule word at
  0x800a397c) takes the low 5 bits of a hardware counter read, uses them as a table index if below 25 (otherwise the low 4 bits),
  then moves indices 11-14 (JR_01, JR_02, HV_01, HV_03) up by five to 16-19. So the random pick **never** gives the SUPER Jr.
  or SUPER Heavy mats. Running the game's own loader instructions in the simulator for every counter value gives these odds
  (out of 32): ASM03, RND00, RND01, RND02 3 each; IAW01, IAW02, ASM01 2 each; NEW01, NEW02, EWF01, EWF02, WOU01, WOU02, DAW01,
  DAW02, ILW01, RND04-08 1 each. That is 21 of the 25 mats; ten of them (ASM01, ASM03, RND00-02, RND04-08) cannot be chosen
  by name. The counter itself (function 0x80054344, a root-counter read) was not run on hardware, so the odds assume its low bits
  are evenly spread.
- **JR_01, JR_02, HV_01, HV_03** load only through the override at 0x80074d68 (values 6 and 7), which the Official Match SUPER Jr. /
  SUPER Heavy challenge sets (see Secret wrestlers). Nothing else sets it.
- No ring file is orphaned. The numbering gaps (no ASM02, HV_02, ILW02, RND03) are files missing from the disc.

## Searched and not found
- Button codes: no Konami-style sequence table in any executable, no button held at boot. Name
  entry compares only against its kana grid; there are no password strings.
- The only button combo is SELECT+START (soft reset, SHINKOU 0x800243b0 and MAIN 0x8002b5e8).
- No sound test, test screen or debug-menu strings in any executable or data file; no developer or
  WCW strings, dates or hidden credits (ASCII and Shift-JIS scans).
- Mode ids 2 and 3 are the menu items that open the Exhibition and Elimination sub-menus, not a cut mode.
- Every DAT, TEX, TMD and RING file is named in MAIN.EXE; all 25 rings are in the loader's table
  (the JR/HV rings come up through the hidden organisations, RND/ASM through the random pick); all
  60 wrestlers have data, textures, a bio box and a name cell. Gaps between files are directory
  sectors; file slack is zero.
- Not settled: unused message lines (indexed tables defeat a pointer search), which sound programs
  are used, the settings word at 0x800a397c, the menu-page jump tables page by page, and the
  uncalled functions beyond those checked (unused message and Memory Card variants).

## How to see it yourself
| Find | How |
|---|---|
| Secret wrestlers | Win the Official Match challenge against all six organisations, then the SUPER challenge; or poke 0xFF into 0x800a3974 (RAM, not saved) and use a mode other than Official/Seven-Bout |
| Secret wrestlers, no grinding | The "(All Wrestlers Unlocked)" patch, or `python3 build.py --unlocks all-wrestlers` (Exhibition, Elimination, Tournament, League, Double Title; not Official or Seven-Bout) |
| Debug display | Write non-zero to 0x80074d6c every frame from before the match loads (RAM poke) |
| Costume | Press START instead of Circle on the select screen |
| Unused intro cut | Replace the file name VPW12SON with VPW10SON in MOV.EXE's string, or swap the files on the disc |
