#!/usr/bin/env python3
"""Write the wrestler guide's data: python3 tools/guidedata.py [PAGE] [--out FILE.json] [--check]

  PAGE           the page whose data block to fill (default docs/guide/wrestlers/index.html)
  --out FILE     also write the data as a JSON file (pretty-printed)
  --check        only check that PAGE is up to date (exit 1 if not); with no page yet it only
                 checks that the data can be built

With no page yet, the data goes to build/work/guide_data.json (or --out) and the counts are printed.
The page renders it with its own script (pagedata.py puts it on one line in the page's
<script type="application/json" id="page-data"> block).

Reads, at run time:
  extracted/SHINKOU.EXE   select grid (0x8005d73c), class table (0x8005d664), second-portrait ids
                          (0x8005d704), secret unlock order (0x8005d7dc)
  extracted/MAIN.EXE      ring table (0x8006b9cc, 25 x 20 bytes)
  extracted/DAT/D30|D60/DAnn.DAT
                          13-byte action records: 38 = offence (bytes 0-5) + running-dive flag
                          (byte 6), 39 = defence + springboard-dive flag, 13 = the special; every
                          move's power (byte 0), the attacker's offence stat it uses (byte 7,
                          1-6; 0 = none) and kind (byte 11: 1 = KO move, 2 = throw with a pin
                          count, 3-5 = hold)
  translation/names.json  the patch's wrestler names, {"real"|"parody": {id: name}}
  translation/guide_roster.json
                          what exists only as pictures or as the patch's wording: heights and
                          weights as the bio boxes draw them, the real-names variant's promotion
                          tags and star moves, parody move wording, promotion names and id
                          blocks, CD track lengths
  translation/guide_moves.tsv
                          the move names of docs/MOVES.md (id, rec, name)
Wrestler ids are the game's own, 1-60 (= DAnn.DAT = names.json key); ids 53-60 are the secret
wrestlers. Research notes behind every table: docs/MOVES.md, docs/HIDDEN_CONTENT.md.

Top-level keys of the data: about, stats, promotions, wrestlers, rings, tracks, names
(names = {"wN": [real, parody]} for the starter page's names switch).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pagedata  # noqa: E402
import paths  # noqa: E402

EXE_BASE = 0x8001d000      # SHINKOU.EXE / MAIN.EXE load address; file offset = address - base + 0x800
GRID, CLASS, ALT_IDS, UNLOCK_IDS = 0x8005d73c, 0x8005d664, 0x8005d704, 0x8005d7dc   # SHINKOU
RING_TABLE = 0x8006b9cc    # MAIN
REC = 13                   # bytes per DAnn action record

# The six stat pairs: DAnn record 38 = offence, 39 = defence, values 1-5. Labels chosen by the
# owner; the game itself never names them. What each powers / is hit by: which moves use the index
# as attacker stat (byte 7) and as target stat (byte 8) - from the data.
STATS = [
    ('head', 'Head', 'Headbutts, and every counter to a close grab',
     'Slaps, punches to the face, brainbusters, piledrivers, high kicks, dropkicks'),
    ('back', 'Neck/Back', 'Snapmares, suplexes, neckbreakers',
     'German and backdrop suplexes, neckbreakers, chops to the chest'),
    ('arms', 'Arms', 'Slaps, punches, elbows, chops, body slams, arm locks',
     'Arm breakers, arm bars, shoulder breakers'),
    ('body', 'Body', 'Piledrivers, German suplexes, powerbombs, the Boston crab, gutwrenches (values only 1-2)',
     'Body slams, kicks and knees to the body, crabs, camel clutch (values only 1-2)'),
    ('legs', 'Legs', 'Kicks, knees, leg drops, dropkicks', 'Low kicks, leg locks, drop toe holds, the Dragon Screw'),
    ('air', 'Aerial', 'Top-rope attacks, dives and splashes', 'Top-rope attacks'),
]

# Move record -> input, grouped as the sections of docs/MOVES.md "How the moves are chosen"
MOVE_GROUPS = [
    ('Strikes', [(0, 'Cross tap, near'), (1, 'Cross tap, far'), (2, 'Cross held, near'), (3, 'Cross held, far')]),
    ('Grapples', [(4, 'Far tap'), (5, 'Far tap + Up'), (6, 'Far tap + Down'),
                  (7, 'Close tap'), (8, 'Close tap + Up'), (9, 'Close tap + Down'),
                  (10, 'Hold'), (11, 'Hold + Up'), (12, 'Hold + Down')]),
    ('Special', [(13, 'Special (full spirit, hold)')]),
    ('From behind', [(17, 'Tap from behind'), (18, 'Tap from behind + Up/Down'),
                     (19, 'Hold from behind'), (20, 'Hold from behind + Up/Down'),
                     (21, 'Break free of a grab from behind (tap)')]),
    ('Ground', [(31, 'Ground hold, standing at the head (Circle)'), (32, 'Ground hold, standing at the feet (Circle)'),
                (33, 'Cross on an opponent lying on the mat')]),
    ('Top rope and dives', [(34, 'Corner top-rope attack, opponent lying'),
                            (35, 'Corner top-rope attack, opponent standing'),
                            (40, 'Running dive through the ropes (opponent outside)'),
                            (41, 'Spring off the ropes onto the floor (opponent outside)')]),
    ('Running', [(22, 'Tap Circle as the opponent runs at you'), (23, 'Hold Circle as the opponent runs at you'),
                 (24, 'Triangle + Circle (from standing)'), (25, 'Cross while running')]),
    ('Reversals and corner', [(27, 'Punch reversal (Square + Cross, opponent taps Cross)'),
                              (28, 'Kick reversal (Square + Cross, opponent holds Cross)'),
                              (29, 'Strong grab on a dazed opponent in the corner (hold Circle)'),
                              (30, 'Reversal of the corner grab')]),
    ('Other', [(36, 'L1: leapfrog over a running opponent'), (37, 'L2: taunt')]),
    ('Counters', [(14, 'Counter to a close tap'), (15, 'Counter to a close tap + Up'),
                  (16, 'Counter to a close tap + Down')]),
]

# Secret cells the reveal routine (SHINKOU 0x8002e070) fills, in unlock-bit order
HIDDEN_CELLS = [(14, 1), (14, 2), (14, 3), (14, 4), (14, 5), (14, 6), (1, 1), (1, 6)]
SUPER_HOW = ('With one wrestler who has won all six promotions\' challenges, win the 7th challenge, {} '
             '(the wrestler must be a {})')

# Costumes (docs/HIDDEN_CONTENT.md, texture comparison): a real change without a new portrait; details seen
COSTUME_CLEAR = {5, 6, 14, 15, 16, 22, 53}
COSTUME_DETAIL = {35: 'mask colour red to green', 38: 'sunglasses', 49: 'headband reading "LEAGUN"',
                  42: 'a hiragana poem on the face'}

# CD audio: music n plays CD track n+3 (from the code); file names from the disc's track list
TRACK_FILES = {2: 'OPEN', 3: '6BGM02', 4: '2BGM13', 5: '4BGM06', 6: 'SINNNICH', 7: '3ENDING', 8: '2BGM11',
               9: '1BGM04', 10: '2BGM05', 11: '2BGM14', 12: '3BGM02', 13: '3BGM10', 14: '4BGM09', 15: '5BGM08',
               16: '5BGM10', 17: 'BGM07', 18: 'OPENING'}
FED_TRACK = {1: 6, 2: 13, 3: 17, 4: 10, 5: 5, 6: 15, 7: 14, 8: 16}   # ring federation -> match music
TRACK_USE = {2: 'Copy of track 6 (for CD players)', 3: 'Menus', 4: 'Short jingle in the match program',
             7: 'Staff credits (after a SUPER challenge)', 8: 'Never played', 9: 'Giant Baba\'s theme: plays in '
             'any match he is in', 11: 'Never played', 12: 'Menus', 18: 'Copy of track 6 (for CD players)'}
BABA = 22


def need(p):
    if not p.exists():
        sys.exit(f'{paths.show(p)} missing: run python3 tools/extract.py first (it unpacks the disc into extracted/)')
    return p


def exe(name):
    data = need(paths.EXTRACTED / name).read_bytes()
    return lambda addr, n: data[addr - EXE_BASE + 0x800:addr - EXE_BASE + 0x800 + n]


def da_file(n):
    return need(paths.EXTRACTED / 'DAT' / ('D30' if n <= 30 else 'D60') / f'DA{n:02d}.DAT')


def ring_random_odds():
    """Mat Select = Random: the loader's own rule for each 5-bit counter value (MAIN 0x8001fa48)."""
    odds = {}
    for c in range(32):
        i = c if c < 25 else c & 15
        if 11 <= i <= 14:
            i += 5
        odds[i] = odds.get(i, 0) + 1
    return odds


def read_moves():
    p = need(paths.TRANSLATION / 'guide_moves.tsv')
    lines = [ln for ln in p.read_text(encoding='utf-8').splitlines() if ln and not ln.startswith('#')]
    out = {}
    for r in csv.DictReader(lines, delimiter='\t'):
        out[(int(r['id']), int(r['rec']))] = r['name']
    return out


def build():
    names = json.loads(need(paths.TRANSLATION / 'names.json').read_text(encoding='utf-8'))
    extra = json.loads(need(paths.TRANSLATION / 'guide_roster.json').read_text(encoding='utf-8'))
    moves = read_moves()
    parody = extra['parody_moves']
    two = lambda s: [s, parody[s]] if s in parody else s       # a name or [real, parody]

    sh = exe('SHINKOU.EXE')
    grid, cls = sh(GRID, 128), sh(CLASS, 60)
    alt_ids = {b for b in sh(ALT_IDS, 16) if b}
    unlock_ids = list(sh(UNLOCK_IDS, 8))
    cell = {grid[i]: (i // 8, i % 8) for i in range(128) if 1 <= grid[i] <= 60}
    cell.update({n: HIDDEN_CELLS[i] for i, n in enumerate(unlock_ids)})

    proms = extra['promotions']
    prom_of = {n: p for p in proms for n in range(p['ids'][0], p['ids'][1] + 1)}

    def unlock(i):
        if i < 6:
            return f"Win the Official Match challenge for {proms[i]['name']} ({proms[i]['abbr']})"
        return SUPER_HOW.format(*(('SUPER Jr.', 'junior heavyweight') if i == 6 else ('SUPER HEAVY', 'heavyweight')))

    wrestlers = []
    for n in range(1, 61):
        d = da_file(n).read_bytes()
        rec = lambda r: d[r * REC:(r + 1) * REC]
        off, dfn, sp = rec(38), rec(39), rec(13)
        groups = []
        for g, slots in MOVE_GROUPS:
            ms = []
            for r, label in slots:
                if (n, r) in moves:
                    b = rec(r)
                    m = {'rec': r, 'input': label, 'name': two(moves[(n, r)]),
                         'power': b[0], 'pin': b[11] == 2, 'hold': b[11] in (3, 4, 5), 'st': b[7]}
                    if b[11] == 1:
                        m['ko'] = True      # only on the 100 KO moves, to keep the page data small
                    ms.append(m)
            if ms:
                groups.append({'group': g, 'moves': ms})
        x = extra['wrestlers'][str(n)]
        p = prom_of.get(n)
        secret = n in unlock_ids
        r, c = cell[n]
        wrestlers.append({
            'id': n,
            'names': [names['real'][str(n)], names['parody'][str(n)]],
            'promotion': {'abbr': p['abbr'], 'name': p['name']} if p else None,
            'tag': [x['tag'], p['abbr'] if p else None],     # bio-box promotion tag: real-names / parody variant
            'class': 'junior' if cls[n - 1] == 0 else 'heavyweight',
            'height': x['height_cm'], 'weight': x['weight_kg'],
            'offence': list(off[:6]), 'defence': list(dfn[:6]),
            'offence_total': sum(off[:6]), 'defence_total': sum(dfn[:6]),
            'dives': {'running': off[6], 'springboard': dfn[6]},
            'special': {'name': two(moves.get((n, 13))), 'power': sp[0],
                        'kind': 'throw with a pin count' if sp[11] == 2 else ('hold' if sp[11] in (3, 4, 5) else 'damage only, no pin count')},
            'star': [x['star'], parody.get(x['star'], x['star'])],
            'moves': groups,
            'costumes': {'count': 2, 'alt_portrait': n in alt_ids,
                         'change': 'own portrait' if n in alt_ids else ('clear' if n in COSTUME_CLEAR else 'minor'),
                         'detail': COSTUME_DETAIL.get(n)},
            'secret': secret,
            'unlock': unlock(unlock_ids.index(n)) if secret else None,
            'available_in': ('every mode but Official Match and Seven-Bout Blaze, once unlocked' if secret
                             else 'every mode'),
            'cell': {'row': r, 'col': c},
            'theme_track': 9 if n == BABA else None,
        })

    mn = exe('MAIN.EXE')
    odds = ring_random_odds()
    rings = []
    for i in range(25):
        f = mn(RING_TABLE + i * 20, 20).split(b'\0')[0].decode('ascii').split('\\')[-1].split(';')[0]
        if i <= 10:
            org = [0, 0, 1, 1, 2, 2, 3, 3, 4, 5, 5][i]
            how, fed, abbr = f'Mat Select {proms[org]["abbr"]} (one of its mats at random), or Random', org + 1, proms[org]['abbr']
        elif i <= 14:
            sup = 'SUPER Jr.' if i <= 12 else 'SUPER HEAVY'
            how, fed, abbr = f'Only in the Official Match {sup} challenge', 7 if i <= 12 else 8, sup
        else:
            how, fed, abbr = 'Random only', 1, None       # the loader leaves the federation at 1 (NSW music)
        rings.append({'index': i, 'file': f, 'promotion': abbr, 'how': how,
                      'random_odds': odds.get(i, 0), 'music_track': FED_TRACK[fed]})

    fed_name = {i + 1: f"{p['name']} ({p['abbr']}) rings" for i, p in enumerate(proms)}
    fed_name.update({7: 'SUPER Jr. rings', 8: 'SUPER HEAVY rings'})
    tracks = []
    for t, f in TRACK_FILES.items():
        use = TRACK_USE.get(t) or 'Matches on ' + ' and '.join(fed_name[k] for k, v in FED_TRACK.items() if v == t)
        if t == 6:
            use += ', the Random-only mats, and the intro'
        tracks.append({'track': t, 'file': f + '.DA', 'seconds': extra['track_seconds'][str(t)], 'use': use})

    promotions = [{'abbr': p['abbr'], 'name': p['name'], 'ids': p['ids'], 'mat_select': i + 1,
                   'music_track': FED_TRACK[i + 1], 'prize': unlock_ids[i]} for i, p in enumerate(proms)]
    return {
        'about': ("Virtual Pro Wrestling wrestler data. Ids are the game's own (1-60; 53-60 secret). Names "
                  "[real, parody] for the names switch. Height cm and weight kg as the game's bio box shows them. "
                  "Stats 1-5 in the order of 'stats'. dives.running 0 none, 1 yes, 2 yes (another start point); "
                  "dives.springboard 0/1. Cell = select grid row, column (table coordinates; rows 1 and 14 hold "
                  "the secret wrestlers). random_odds = chances in 32 under Mat Select Random. "
                  "Music n plays CD track n+3. Move st = the offence stat it uses (1-6 in the order of "
                  "'stats', 0 none); ko true = a KO move (can end a match with the TKO rule on)."),
        'stats': [{'key': k, 'label': lab, 'offence': o, 'defence': dd} for k, lab, o, dd in STATS],
        'promotions': promotions,
        'wrestlers': wrestlers,
        'rings': rings,
        'tracks': tracks,
        'names': {f"w{w['id']}": w['names'] for w in wrestlers},
    }


def validate(data):
    """Stop with what's wrong when the data doesn't look like the game's."""
    W = data['wrestlers']
    errs = []
    for key, n in (('wrestlers', 60), ('rings', 25), ('tracks', 17), ('promotions', 6), ('stats', 6)):
        if len(data[key]) != n:
            errs.append(f'{len(data[key])} {key}, expected {n}')
    for v, label in ((0, 'real'), (1, 'parody')):
        seen = {}
        for w in W:
            nm = w['names'][v]
            if not nm:
                errs.append(f"wrestler {w['id']}: no {label} name in translation/names.json")
            elif nm in seen:
                errs.append(f"{label} name {nm!r} used by wrestlers {seen[nm]} and {w['id']}")
            seen[nm] = w['id']
    secret = sorted(w['id'] for w in W if w['secret'])
    if secret != list(range(53, 61)):
        errs.append(f'secret wrestlers {secret}, expected 53-60')
    cells = [(w['cell']['row'], w['cell']['col']) for w in W]
    if len(set(cells)) != 60:
        errs.append('two wrestlers share a select-grid cell')
    for w in W:
        if not w['moves']:
            errs.append(f"wrestler {w['id']}: no moves (translation/guide_moves.tsv)")
        if not w['special']['name']:
            errs.append(f"wrestler {w['id']}: no special (record 13) in translation/guide_moves.tsv")
        if not all(0 <= m['st'] <= 6 for g in w['moves'] for m in g['moves']):
            errs.append(f"wrestler {w['id']}: a move's offence stat (record byte 7) outside 0-6")
        if not all(1 <= s <= 5 for s in w['offence'] + w['defence']):
            errs.append(f"wrestler {w['id']}: a stat outside 1-5 - is extracted/DAT from the original disc?")
        if not (150 <= w['height'] <= 250 and 50 <= w['weight'] <= 250):
            errs.append(f"wrestler {w['id']}: {w['height']} cm {w['weight']} kg - check translation/guide_roster.json")
    if errs:
        sys.exit('guide data looks wrong:\n  ' + '\n  '.join(errs))


def counts(data):
    nm = sum(len(g['moves']) for w in data['wrestlers'] for g in w['moves'])
    return (f"{len(data['wrestlers'])} wrestlers ({nm} moves), {len(data['rings'])} rings, "
            f"{len(data['tracks'])} tracks, {len(data['promotions'])} promotions")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0], epilog=paths.FOLDER_HELP,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page', type=Path, nargs='?', help='page to fill (default docs/guide/wrestlers/index.html)')
    ap.add_argument('--out', type=Path, help='also write the data to this JSON file')
    ap.add_argument('--check', action='store_true', help='only check that the page is up to date')
    args = ap.parse_args(paths.configure(sys.argv[1:] if argv is None else argv))
    page = args.page or paths.DOCS / 'guide' / 'wrestlers' / 'index.html'
    if args.page and not page.exists():
        sys.exit(f'{paths.show(page)} does not exist (leave PAGE out for the default page)')
    data = build()
    validate(data)
    if args.check:
        if not page.exists():
            print(f'{paths.show(page)}: no page yet - data builds: {counts(data)}')
        elif pagedata.write(page, data, check=True):
            print(f'{paths.show(page)}: up to date')
        return 0
    out = args.out
    if page.exists():
        pagedata.write(page, data)
    elif out is None:
        out = paths.WORK / 'guide_data.json'
        print(f'{paths.show(page)}: no page yet')
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
        print(f'{paths.show(out)}: written')
    print(counts(data))
    return 0


if __name__ == '__main__':
    sys.exit(main())
