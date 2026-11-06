#!/usr/bin/env python3
"""Game images: export every original and import the English ones (Virtual Pro Wrestling, PS1).

The pictures are TIM images packed back to back in four files:
  SHINKOU.BIN  (142 TIMs: title, menu word atlases, name atlases, 90x74 portraits)
  RESULT.BIN, T0623.DAT, STAFF.BIN (STAFF = credits, kept as is: exported for completeness)
Per-wrestler textures TEX/*/TAnn_1.DAT / TAnn_2.DAT: ids TAnn_001 (intro name banner), TAnn_002 (move list), TAnn_003 (name tag);
the _1 and _2 files share these three TIMs, so an import writes both.
Ids are <FILE>_<index>, e.g. SHINKOU_003 (index = order of the TIM in the file, found by tim.find_tims).

export_all(extracted, out) -> count
    out/<id>.png: indexed PNG with the pixel *indices* of the TIM and the colours of CLUT 0 (atlases that
    use more CLUTs keep their other palettes untouched in the file: only indices are edited), colour 0x0000
    transparent; out/<id>.json: file, offset, bpp, size, clut count.
import_images(images, files) -> count
    Writes the indices of each English PNG back over the TIM's pixel data. Size and colour depth must match.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pngio  # noqa: E402
import tim  # noqa: E402

FILES = [('SHINKOU', 'SHINKOU.BIN'), ('RESULT', 'RESULT.BIN'), ('T0623', 'T0623.DAT'), ('STAFF', 'STAFF.BIN')]


def _c15(v):
    return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31)


def _unpack(t):
    stride = t.vram[2] * 2
    raw = t.pixels_raw
    rows = []
    for y in range(t.height):
        line = raw[y * stride:(y + 1) * stride]
        idx = [n for b in line for n in (b & 15, b >> 4)] if t.bpp == 4 else list(line)
        rows.append(idx[:t.width])
    return rows


def _pack(rows, bpp):
    out = bytearray()
    for r in rows:
        if bpp == 4:
            r = list(r) + [0] * (len(r) % 2)
            out += bytes(r[i] | (r[i + 1] << 4) for i in range(0, len(r), 2))
        else:
            out += bytes(r)
    return bytes(out)


def _tims(data):
    return list(tim.find_tims(data))


def export_all(extracted, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for pre, name in FILES:
        data = (Path(extracted) / name).read_bytes()
        for i, (off, t) in enumerate(_tims(data)):
            if t.bpp not in (4, 8) or not t.cluts:
                continue
            pal = list(t.cluts[0])
            pal += [0] * ((16 if t.bpp == 4 else 256) - len(pal))
            colours = [_c15(v) for v in pal]
            alpha = [0 if v == 0 else 255 for v in pal]
            iid = f'{pre}_{i:03d}'
            pngio.write(str(out / f'{iid}.png'), _unpack(t), colours, alpha)
            (out / f'{iid}.json').write_text(json.dumps(
                {'file': name, 'offset': off, 'bpp': t.bpp, 'width': t.width, 'height': t.height,
                 'cluts': len(t.cluts), 'size': t.size}))
            n += 1
    for tex in sorted((Path(extracted) / 'TEX').glob('T*_1/TA*_1.DAT')):
        nn = tex.name[2:4]
        for i, (off, t) in enumerate(_tims(tex.read_bytes())):
            if i == 0 or t.bpp not in (4, 8) or not t.cluts:        # TIM 0 is the body texture (differs per file)
                continue
            pal = list(t.cluts[0]) + [0] * (16 - len(t.cluts[0]))
            iid = f'TA{nn}_{i:03d}'
            pngio.write(str(out / f'{iid}.png'), _unpack(t), [_c15(v) for v in pal], [0 if v == 0 else 255 for v in pal])
            (out / f'{iid}.json').write_text(json.dumps(
                {'file': tex.name, 'offset': off, 'bpp': t.bpp, 'width': t.width, 'height': t.height,
                 'cluts': len(t.cluts), 'size': t.size}))
            n += 1
    return n


def import_images(images, files):
    done = 0
    by_file = {}
    for iid, path in images.items():
        pre, idx = iid.rsplit('_', 1)
        if pre.startswith('TA') and pre[2:].isdigit():     # per-wrestler textures: the _1 and _2 files share these TIMs
            grp = 'T30' if int(pre[2:]) <= 30 else 'T60'
            for name in (f'TEX/{grp}_1/{pre}_1.DAT', f'TEX/{grp}_2/{pre}_2.DAT'):
                by_file.setdefault(name, []).append((int(idx), iid, path))
            continue
        name = dict(FILES).get(pre)
        if name is None:
            raise SystemExit(f'image {iid}: unknown source {pre}')
        by_file.setdefault(name, []).append((int(idx), iid, path))
    for name, items in by_file.items():
        data = files.get(name)
        found = _tims(bytes(data))
        for idx, iid, path in items:
            off, t = found[idx]
            png = pngio.read(str(path))
            if png.width != t.width or png.height != t.height:
                raise SystemExit(f'{iid}: PNG is {png.width}x{png.height}, the TIM is {t.width}x{t.height}')
            if png.palette is None:
                raise SystemExit(f'{iid}: PNG must be indexed in the original palette')
            top = 16 if t.bpp == 4 else 256
            if any(v >= top for r in png.rows for v in r):
                raise SystemExit(f'{iid}: pixel index beyond the {t.bpp}bpp palette')
            packed = _pack(png.rows, t.bpp)
            start = off + t.size - len(t.pixels_raw)
            if len(packed) != len(t.pixels_raw):
                raise SystemExit(f'{iid}: packed size {len(packed)} != {len(t.pixels_raw)}')
            data[start:start + len(packed)] = packed
            done += 1
        files.put(name, data)
    return done


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 3 and argv[0] == 'export':
        print(export_all(argv[1], argv[2]), 'images')
        return 0
    print('usage: gfx.py export <extracted> <outdir>')
    return 1


if __name__ == '__main__':
    sys.exit(main())
