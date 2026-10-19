#!/usr/bin/env python3
"""List Bulgarian pages that are missing or older (by last git commit) than their English source."""
import pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book'

def last_commit(p):
    out = subprocess.run(['git', 'log', '-1', '--format=%ct', '--', str(p)], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return int(out) if out else None

missing, stale, ok = [], [], 0
for en in sorted(BOOK.rglob('*.md')):
    if en.name.endswith('.bg.md') or 'i18n' in en.parts or en.name == 'SUMMARY.md':
        continue
    bg = en.with_name(en.stem + '.bg.md')
    rel = en.relative_to(BOOK)
    if not bg.exists():
        missing.append(rel); continue
    te, tb = last_commit(en), last_commit(bg)
    if te and tb and te > tb:
        stale.append(rel)
    else:
        ok += 1
print(f'Up to date: {ok}  ·  Stale: {len(stale)}  ·  Missing: {len(missing)}')
for r in stale: print('  STALE  ', r)
for r in missing: print('  MISSING', r)
