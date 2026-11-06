#!/usr/bin/env python3
"""Build the translated image from the original. Standard library only.

  python3 build.py [--name NAME] [--unlocks all|none|GROUP,...] [--clean]
      -> build/NAME.<ext> (default NAME: "<game> (English)")

Steps (default folders shown; move any of them with the folder options - see --help):
  1. verify the original in rom/ (size + SHA-1; --skip-verify skips the hash)
  2. prepare build/NAME: a fresh copy of the original, or - much faster for big images - the last
     build with every range it wrote restored from the original (tools/image.py; --clean copies)
  3. text: translation/script/ and translation/text/ into the game's files (TEXT_STEPS)
  4. code patches picked by --unlocks (CODE_PATCHES, tools/codepatch.py; debug-* groups only when named)
  5. images: for every catalogued image the English file the catalogue picks (hand-made >
     approved > rendered), imported by tools/gfx.py; the final set is copied to review/images-english/
  6. write every changed file back into the image (files that fit in place first)

Two name sets (e.g. real wrestlers' names and the game's parody names, two releases): fill
NAME_SETS; --names picks one (default the first) and text steps read NAMES. Names are written as
tokens in translation/ (`<Name>`) that the project's names tool resolves per set (Fire Pro
Wrestling S tools/names.py, D tools/fpdtext.py); lint's NAME_TOKEN checks them.

Test builds: --boot PART starts the game straight in PART (BOOT_PATCHES, once known);
--no-translation skips text and images, and gameplay patches unless --unlocks is given - on its
own the result is byte-identical to the original (tools/check.py --control proves it).
Developer flags (never for releases): --no-text FILE skips one text file.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools'))
import catalog  # noqa: E402
import codepatch  # noqa: E402
import disc  # noqa: E402
import gfx  # noqa: E402
import image  # noqa: E402
import paths  # noqa: E402

# Gameplay patches: (group, file, address, original, new, description) - see tools/codepatch.py.
# Groups named debug-* are developer extras (debug menus, cheat windows): never in "all" or the
# default, only when named, never in a release variant. An extra the owner wants to release (say a
# restored debug menu as its own patch) gets another group name, e.g. dev-menu, and a make_patches
# VARIANT, with DEFAULT_GROUPS = set() to keep it out of the main patch.
def _label_patches():
    # Label sprite records of the menu atlas (translation/label_records.json, written by private/work/img/label_layout.py):
    # new atlas position, width and on-screen x, with the original bytes checked. Docs: docs/TECHNICAL.md.
    import json
    out = []
    for fn, group in (('label_records.json', 'labels'), ('text_hook.json', 'texthook')):
        f = paths.ROOT / 'translation' / fn
        if f.exists():
            out += [(group, r.get('file', 'SHINKOU.EXE'), r['addr'], bytes.fromhex(r['orig']), bytes.fromhex(r['new_bytes']), r['text'])
                    for r in json.loads(f.read_text())]
    return out


CODE_PATCHES = _label_patches() + [
    # Secret wrestlers 53-60 (docs/HIDDEN_CONTENT.md): the select-screen setup shows a secret cell only if bit i of the
    # progress word 0x800a3974 is set (and only in modes >= 2). Make both bit tests always pass.
    ('all-wrestlers', 'SHINKOU.EXE', 0x8002e098, bytes.fromhex('24104300'), bytes.fromhex('01000234'), 'select cells: and v0,v0,v1 -> ori v0,zero,1 (bit always set)'),
    ('all-wrestlers', 'SHINKOU.EXE', 0x8002f2d4, bytes.fromhex('24104300'), bytes.fromhex('01000234'), 'select name sprites: same bit test always set'),
]
ALWAYS_GROUPS = {'labels', 'texthook'}               # in every translated build, not a choice (--unlocks ignores them): the English's own fixes
UNLOCK_GROUPS = sorted({p[0] for p in CODE_PATCHES} - ALWAYS_GROUPS)
PLAYER_GROUPS = [g for g in UNLOCK_GROUPS if not g.startswith('debug-')]
DEFAULT_GROUPS = set()  # was set(PLAYER_GROUPS): the all-wrestlers extra ships as its own variant; without --unlocks; set() when the extras ship as separate "(All Unlocked)" patches

# --boot: (part, file, address, original, new) - patches that start the game in a given part.
BOOT_PATCHES = {
}


def to_offset(name, addr):
    """GAME-SPECIFIC: file offset of a RAM address in file `name` (overlay base, ELF segments, ...)."""
    if name in ('SHINKOU.EXE', 'RESULT.EXE'):
        return addr - 0x8001d000 + 0x800          # PS-X EXE: load address 0x8001d000, 0x800-byte header
    raise SystemExit(f'build.py to_offset(): no address mapping for {name} yet')


# Text steps: (text file or folder under translation/, function(path, files)). Each inserts the
# English into the game's files through `files` and stops with a clear message if anything doesn't fit.
# Zero-padding files a grown file may take room from when the disc is full (PS2 disc.py
# take_from_padding: their end is cut off) - e.g. ['/DUMMY.DAT']; check they are all zeros.
PADDING_DONORS = []

# Name sets for the --names option, e.g. ('real', 'parody') - empty: one set, no option.
NAME_SETS = ('real', 'parody')      # wrestler names: the real wrestlers' or the game's own parody names
NAMES = NAME_SETS[0] if NAME_SETS else None

def resolve_names(line):
    """<N12> = wrestler 12's full name in the chosen name set (translation/names.json)."""
    import json, re
    if '<N' not in line:
        return line
    table = json.loads((paths.TRANSLATION / 'names.json').read_text(encoding='utf-8'))[NAMES]
    return re.sub(r'<N(\d+)>', lambda m: table[m.group(1)], line)


def messages_step(path, files):
    """translation/text/<file>.txt: fixed 32-byte message lines in an overlay EXE (meta: file, address, line count).
    English lines are padded with spaces to 32 bytes; ASCII is drawn two letters per cell by the text hook."""
    import blocks
    bf = blocks.BlockFile(path)
    n = 0
    for b in bf.blocks:
        en = b.english
        if not en:
            continue
        en = [resolve_names(l) for l in en]
        name, addr, count = b.meta.split()
        addr, count = int(addr, 0), int(count)
        src = bf.source(b)
        if len(en) > count:
            sys.exit(f'{path.name} {b.id}: {len(en)} English lines, only {count} fit')
        data = files.get(name)
        for i in range(count):
            line = en[i] if i < len(en) else ''
            raw = line.encode('cp932')
            if len(raw) > 32:
                sys.exit(f'{path.name} {b.id}: line {i + 1} is {len(raw)} bytes (max 32): {line!r}')
            raw = raw.ljust(32, b' ')
            off = addr + 0x21 * i          # file offset
            sb = src[i].encode('cp932')
            if bytes(data[off:off + 32]) != sb + b'\x81\x40' * ((32 - len(sb)) // 2):
                sys.exit(f'{path.name} {b.id}: original text not at file offset {off:#x}')
            data[off:off + 32] = raw
        files.put(name, data)
        n += 1
    print(f'text: {path.name}: {n} messages')


TEXT_STEPS = [
    ('text/shinkou.txt', messages_step),
    ('text/result.txt', messages_step),
]


class Files:
    """The game's files for this build: read from the image on first use, written back at the end."""

    def __init__(self, d):
        self.d, self.data, self.changed = d, {}, set()

    def get(self, name):
        if name not in self.data:
            self.data[name] = bytearray(self.d.read_file(self.d.find(name)))
        return self.data[name]

    def put(self, name, data):
        self.data[name] = bytearray(data)
        self.changed.add(name)


def unlock_groups(value):
    if value == 'all':
        return set(PLAYER_GROUPS)
    if value == 'none':
        return set()
    groups = {g.strip() for g in value.split(',') if g.strip()}
    if groups - set(UNLOCK_GROUPS):
        raise argparse.ArgumentTypeError(f'expected all, none or some of {",".join(UNLOCK_GROUPS) or "(no groups yet)"}')
    return groups


def images_step(files):
    final = catalog.final_images()
    missing, changed, _ = catalog.stale()
    if missing or changed:
        print(f'note: {len(missing) + len(changed)} automatic renders are out of date - run tools/render.py '
              f'(building with the frozen files there are)')
    if NAMES == 'parody':       # the parody-name pictures replace the real-name ones
        for png in sorted((paths.TRANSLATION / 'images-parody').glob('*.png')):
            if png.stem in final:
                final[png.stem] = ('hand', png)
    n = gfx.import_images({k: p for k, (tag, p) in final.items()}, files)
    if paths.ENGLISH_IMAGES.exists():
        shutil.rmtree(paths.ENGLISH_IMAGES)
    if final:
        paths.ENGLISH_IMAGES.mkdir(parents=True)
        for name, (tag, p) in final.items():
            dst = paths.ENGLISH_IMAGES / f'{name}.png'
            dst.parent.mkdir(parents=True, exist_ok=True)      # ids can be archive paths
            shutil.copyfile(p, dst)
        counts = {}
        for tag, _ in final.values():
            counts[tag] = counts.get(tag, 0) + 1
        print(f'images: {n} imported (' + ', '.join(f'{c} {t}' for t, c in sorted(counts.items())) + ')')


def verify_original(original):
    """SHA-1 of the original image, once: the result is remembered with the file's size and
    modification time (build/original.verified), so later builds only re-hash a changed file
    (a DVD image takes ~20 s to hash)."""
    st = original.stat()
    stamp = f'{original.resolve()} {st.st_size} {st.st_mtime_ns} {paths.ORIGINAL["sha1"]}'
    memo = paths.BUILD / 'original.verified'
    if memo.exists() and memo.read_text() == stamp:
        return
    print('verifying the original...')
    if image.sha1(original) != paths.ORIGINAL['sha1']:
        sys.exit(f'{original.name} does not match the expected SHA-1 {paths.ORIGINAL["sha1"]}')
    paths.BUILD.mkdir(parents=True, exist_ok=True)
    memo.write_text(stamp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0], epilog=paths.FOLDER_HELP,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', default=f'{paths.GAME_FILE} (English)')
    ap.add_argument('--skip-verify', action='store_true', help="don't hash the original image")
    ap.add_argument('--clean', action='store_true', help='copy the original instead of restoring the last build')
    ap.add_argument('--no-translation', action='store_true', help='skip text and images (alone: identical to the original)')
    ap.add_argument('--unlocks', type=unlock_groups, metavar='all|none|GROUP,...',
                    help='gameplay patches: all (debug-* groups only when named), none or some groups (default: DEFAULT_GROUPS); '
                         'none with --no-translation')
    if NAME_SETS:
        ap.add_argument('--names', choices=NAME_SETS, default=NAME_SETS[0],
                        help=f'name set: {" or ".join(NAME_SETS)} (default {NAME_SETS[0]})')
    ap.add_argument('--boot', choices=sorted(BOOT_PATCHES), help='TEST BUILD: start the game in this part')
    ap.add_argument('--no-text', action='append', default=[], metavar='FILE',
                    help='developer: leave this text file untranslated (repeatable)')
    args = ap.parse_args(paths.configure(sys.argv[1:] if argv is None else argv))
    global NAMES
    NAMES = getattr(args, 'names', NAMES)
    if args.unlocks is None:
        args.unlocks = set() if args.no_translation else set(DEFAULT_GROUPS)

    original = paths.ROM
    if not original.exists():
        sys.exit(f'put the original image in {paths.show(paths.ROM_DIR)} (or pass --rom): {paths.ORIGINAL_NAME}')
    if original.stat().st_size != paths.ORIGINAL['size']:
        sys.exit(f'{original.name}: {original.stat().st_size} bytes, expected {paths.ORIGINAL["size"]} - not the right image')
    if not args.skip_verify:
        verify_original(original)

    out = paths.BUILD / (args.name + original.suffix)
    with image.prepare(original, out, clean=args.clean) as f:
        d = disc.Disc(f, writable=True)
        files = Files(d)

        if not args.no_translation:
            for rel, step in TEXT_STEPS:
                if rel in args.no_text:
                    print(f'text: skipped {rel} (--no-text)')
                    continue
                step(paths.TRANSLATION / rel, files)

        codepatch.apply(files, CODE_PATCHES, set(args.unlocks) | (set() if args.no_translation else ALWAYS_GROUPS), to_offset)

        if not args.no_translation:
            images_step(files)

        if args.boot:
            codepatch.apply(files, [(args.boot, *p, f'TEST BUILD: boots into {args.boot}') for p in BOOT_PATCHES[args.boot]],
                            {args.boot}, to_offset)

        def fits(name):
            return (len(files.data[name]) + disc.SECTOR - 1) // disc.SECTOR <= d.allocated_sectors(d.find(name))
        for name in sorted(files.changed, key=lambda n: (not fits(n), n)):  # fixed order: same disc layout every build
            d.write_file(d.find(name), bytes(files.data[name]), relocate=True,
                         **({'donors': PADDING_DONORS} if PADDING_DONORS else {}))
            print(f'patched {name}')
    disc.companion_files(out, original)
    print(f'done: {paths.show(out)}  ({len(files.changed)} files patched)')
    return out


if __name__ == '__main__':
    main()
