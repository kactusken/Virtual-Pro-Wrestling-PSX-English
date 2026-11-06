# Patches

What the build changes besides text and images, one section per patch: what the original code
does, what changed, why it works, the tool that makes it, limits to respect, and whether it was
*verified in game*.

## all-wrestlers (secret wrestlers selectable from the start)
*verified in game (2026-11-06): all wrestlers, the eight secret ones included, are selectable.*

**Original.** The select-screen setup (SHINKOU 0x8002e070) fills the eight secret cells (ids 53-60) only when bit *i*
of the progress word 0x800a3974 is set, and only in modes 2 and up; 0x8002f2ac does the same for the name sprites.
The bits are set by winning Official Match challenges (docs/HIDDEN_CONTENT.md).

**Change.** Two instructions, `and v0,v0,v1` at 0x8002e098 and at 0x8002f2d4, become `ori v0,zero,1`, so every bit
test passes. Nothing is written to the progress word or the Memory Card. Group `all-wrestlers`, not in the default build;
released only as the "(All Wrestlers Unlocked)" variants.

**Limits.** Official Match and Seven-Bout Blaze still never show the secret cells (the original's mode check).
The SUPER HEAVY / SUPER Jr. challenge and the staff roll are not affected.

**Checked.** With the patch the grid table at 0x8005d73c holds ids 56, 58, 57, 55, 54, 53 in row 14 and 59, 60 in row 1
(the original holds 0x80 there); the owner then selected all of them in game.
