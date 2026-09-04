# Morganton Scientific — Volume 4 (2026–2027)

Student research from the North Carolina School of Science and Mathematics, Morganton.
Published at <https://morgantonscientific.ncssm.edu>.

**Start here:** [`docs/volume-4-workflow.md`](docs/volume-4-workflow.md) — how a volume gets made,
from intake through publication, written at the end of Volume 3.

## Layout

```
papers/<lastname>/     one article: article.md, myst.yml, refs.bib, images/
essays/<lastname>/     same shape
papers/_template/      copy this to start a new article
frontmatter/           foreword and editors' note
dividers/              the section pages in the print PDF
templates/             typst templates for the print edition
scripts/               make_pdfs.sh and friends
docs/                  role guides and the workflow plan
morganton2027.yml      shared config; every article extends it
```

## Guides

| | For |
|---|---|
| [Author's Guide](docs/author-guide.md) | Students — what to supply and why. No markup required |
| [Copy Editor's Checklist](docs/copy-editor-checklist.md) | Content review and house style |
| [Layout Editor's Guide](docs/layout-editor-guide.md) | MyST conversion, and 24 real mistakes from Volume 3 |
| [Volume 4 workflow](docs/volume-4-workflow.md) | How the whole thing runs this year |
| [Reference](docs/reference.md) | Identifiers, issue DOIs, editors, and non-obvious behaviour |

## Adding an article

```bash
cp -R papers/_template papers/<lastname>
```

Fill in the `CHANGEME`s, open a PR, apply the **`draft`** label to get a Curvenote preview, and
merge when the checks pass. Merging submits it; nothing is published until
`publish_dispatch.yml` is run manually.

## Workflows

| | Trigger | Effect |
|---|---|---|
| `draft.yml` | PR labelled `draft` | Preview and checks. Submits nothing |
| `submit.yml` | push to `main` | Submits changed articles as new versions |
| `resubmit_dispatch.yml` | manual | Submits **all** articles — use after changing `frontmatter/` or shared config |
| `publish_dispatch.yml` | manual | Submits all, then **publishes**. Irreversible |

## Building the print PDF

```bash
brew install typst pdftk-java
brew install --cask font-noto-sans font-noto-serif
npm install -g mystmd
cd scripts && bash ./make_pdfs.sh
```

The Noto fonts are required. Without them typst substitutes silently and the page numbers come out
wrong with no error — Volume 3 first built as 143 pages instead of 160. The issue DOI must also be
set in `frontmatter/volume.yml`; the cover template requires it.

## Previous volumes

[2026 (Volume 3)](https://github.com/ncssm/morgantonscientific2026) ·
[2025 (Volume 2)](https://github.com/ncssm/morgantonscientific2025) ·
[website](https://github.com/ncssm/morsci-website)
