# AI Solution Developer & Architect — Learner Handbook (source)

This repository is the source of the learner handbook (release 2026.11, content as of October 2026).
The book itself lives in [`book/`](book/README.md); its table of contents is [`book/SUMMARY.md`](book/SUMMARY.md).

The same Markdown builds three outputs:

| Output | How |
| --- | --- |
| **GitBook** | Connect this repo with GitBook **Git Sync** (GitHub). `.gitbook.yaml` points GitBook at `book/`, and `SUMMARY.md` defines the navigation. Readers can download a PDF if the published site's plan includes PDF export. |
| **Website (GitHub Pages)** | `mkdocs serve` locally, or push to `main`: the workflow in `.github/workflows/publish.yml` runs `mkdocs gh-deploy`. Enable Pages on the `gh-pages` branch in repo settings. |
| **PDF** | `python scripts/build_pdf.py` → `dist/AI-Solution-Developer-Architect-Learner-Handbook.pdf` (needs pandoc and Playwright Chromium). The workflow also uploads it as a build artifact. |

## Editing rules

- Edit chapters in `book/`. If you add, rename or move a page, update **both** `book/SUMMARY.md` (GitBook) and `nav` in `mkdocs.yml` (website).
- With GitBook Git Sync on, edit `README.md` files in the repo, not in GitBook, to avoid conflicts.
- This is the **learner edition**: instructor notes, gate internals and capstone hidden complexities are deliberately excluded. Keep them out of this repo.

## Local preview

```bash
pip install mkdocs-material playwright && python -m playwright install chromium
mkdocs serve                      # website at http://127.0.0.1:8000
python scripts/build_pdf.py       # PDF in dist/
```
