#!/usr/bin/env python3
"""Build the handbook PDF from book/SUMMARY.md order: pandoc (Markdown -> HTML) + headless Chromium (HTML -> PDF).

Usage:  python3 scripts/build_pdf.py            (run from the repo root)
Needs:  pandoc, Python 'playwright' with Chromium installed (pip install playwright && playwright install chromium)
"""
import re, subprocess, pathlib, html, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book'
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)

CSS = r"""
@page { size: A4; margin: 20mm 18mm 22mm 18mm; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1f2328; }
h1 { font-size: 22pt; margin: 0 0 12pt; page-break-before: always; border-bottom: 2px solid #2f6feb; padding-bottom: 6pt; }
h1.part { font-size: 30pt; border: none; margin-top: 90mm; color: #2f6feb; }
h2 { font-size: 14pt; margin-top: 18pt; color: #0b3d91; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 14pt; page-break-after: avoid; }
h4 { font-size: 10.5pt; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 8.6pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #d0d7de; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #f3f4f6; }
code { font-family: 'SFMono-Regular', Menlo, Consolas, monospace; font-size: 8.4pt; background: #f6f8fa; padding: 0 2pt; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4px; padding: 6pt 8pt; font-size: 8pt; line-height: 1.35; white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8pt; }
blockquote { border-left: 3px solid #2f6feb; margin: 8pt 0; padding: 2pt 10pt; color: #444; background: #f7f9fc; }
img { max-width: 100%; }
a { color: #0b5cd5; text-decoration: none; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { page-break-before: avoid; border: none; font-size: 30pt; }
.cover .sub { font-size: 14pt; color: #57606a; margin-top: 6pt; }
nav#TOC { page-break-before: always; }
nav#TOC::before { content: "Contents"; display: block; font-size: 22pt; font-weight: bold; margin-bottom: 10pt; }
nav#TOC ul { list-style: none; padding-left: 0; }
nav#TOC > ul > li { margin-top: 6pt; }
nav#TOC ul ul { padding-left: 14pt; }
nav#TOC a { color: #1f2328; }
"""

def order():
    files, parts = [], []
    current = None
    for line in (BOOK / 'SUMMARY.md').read_text().splitlines():
        m = re.match(r'^## (.+)', line)
        if m:
            current = m.group(1).strip(); continue
        m = re.match(r'^\s*\* \[(.+?)\]\((.+?\.md)\)', line)
        if m:
            files.append((current, m.group(2)))
    return files

def main():
    seq = order()
    md_parts, last_part = [], None
    for part, rel in seq:
        if part and part != last_part and part.startswith('Part'):
            md_parts.append(f'\n\n# {part} {{.part}}\n\n')
        last_part = part
        text = (BOOK / rel).read_text()
        depth = rel.count('/')
        text = text.replace('../' * depth + 'assets/', 'assets/') if depth else text
        # internal .md links -> plain text targets are not navigable in PDF; keep link text only
        text = re.sub(r'\[([^\]]+)\]\((?!https?://)[^)]+\.md(#[^)]*)?\)', r'\1', text)
        md_parts.append('\n\n' + text + '\n\n')
    combined = BOOK / '_combined.md'
    combined.write_text(''.join(md_parts))
    html_body = subprocess.run(
        ['pandoc', str(combined), '-f', 'gfm+attributes', '-t', 'html5', '--toc', '--toc-depth=1', '--standalone',
         '--metadata', 'title=AI Solution Developer & Architect — Learner Handbook', '--highlight-style=tango',
         '--resource-path', str(BOOK)], capture_output=True, text=True, check=True).stdout
    combined.unlink()
    cover = ('<div class="cover"><h1>AI Solution Developer &amp; AI Solution Architect</h1>'
             '<div class="sub">Learner Handbook · Release 2026.11 · content as of October 2026</div>'
             '<div class="sub">Learning by doing on one evolving product, gated by evals</div></div>')
    html_doc = re.sub(r'<header id="title-block-header">.*?</header>', cover, html_body, flags=re.S)
    html_doc = html_doc.replace('</head>', f'<style>{CSS}</style></head>')
    html_doc = re.sub(r'<style>\s*html \{.*?</style>', '', html_doc, count=1, flags=re.S)  # drop pandoc default css
    page = BOOK / '_print.html'
    page.write_text(html_doc)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(page.as_uri(), wait_until='load')
        pg.pdf(path=str(OUT / 'AI-Solution-Developer-Architect-Learner-Handbook.pdf'), format='A4',
               display_header_footer=True, print_background=True, outline=True, tagged=True,
               header_template='<div></div>',
               footer_template='<div style="font-size:7pt;color:#888;width:100%;padding:0 18mm;display:flex;justify-content:space-between">'
                               '<span>AI Solution Developer &amp; Architect — Learner Handbook · 2026.11</span>'
                               '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
               margin={'top': '18mm', 'bottom': '20mm', 'left': '16mm', 'right': '16mm'})
        b.close()
    page.unlink()
    print('PDF written to', OUT / 'AI-Solution-Developer-Architect-Learner-Handbook.pdf')

if __name__ == '__main__':
    sys.exit(main())
