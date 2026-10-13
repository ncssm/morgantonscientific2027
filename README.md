# Morganton Scientific — Volume 4 (2026–2027)

Student research from the North Carolina School of Science and Mathematics, Morganton.
Published at <https://morgantonscientific.ncssm.edu>.

**Start here:** [`docs/volume-4-workflow.md`](docs/volume-4-workflow.md) — how a volume gets made,
from intake through publication, written at the end of Volume 3.

## How an article gets published

Two steps happen before an article reaches GitHub; the rest happen on the article's issue and
pull request. Only the merge has consequences: it submits the article to Curvenote. A failed check
or a requested change sends the article back to the layout editor, on the same pull request.

```mermaid
flowchart TD
    subgraph before["Before GitHub"]
        submit["<b>Submission</b><br/>student author"]
        folder["<b>Manuscript folder</b><br/>an editor"]
    end
    subgraph github["On GitHub"]
        intake["<b>Intake</b><br/>copy editor"]
        convert["<b>Conversion</b><br/>layout editor"]
        checks["<b>Checks</b><br/>automatic"]
        proof["<b>Author proof</b><br/>author, by email"]
        copyedit["<b>Copy edit</b><br/>copy editor"]
        merge["<b>Merge</b><br/>submits to Curvenote"]
    end
    volume["<b>Volume assembly and publication</b><br/>Editors-in-Chief"]

    submit --> folder --> intake --> convert --> checks --> proof --> copyedit --> merge
    merge -- "once every article is in" --> volume
    checks -. "a check fails" .-> convert
    proof -. "changes needed" .-> convert
    copyedit -. "changes requested" .-> convert

    classDef offGitHub stroke-dasharray: 5 4
    classDef submits stroke-width: 3px
    class submit,folder offGitHub
    class merge submits
```

| Step | Who | Where | What happens |
|---|---|---|---|
| Submission | Student author | The intake Google Form | Answers land in a Sheet, uploads in Drive |
| Manuscript folder | An editor | Google Drive | The manuscript, figures, `.bib` file and any code go into one folder for the article |
| Intake | Copy editor | A *New article* issue | Opened with the folder link; the copy editor chases anything missing, then assigns the layout editor |
| Conversion | Layout editor | A pull request with the `draft` label | Its description links back to the issue |
| Checks | Automatic | The pull request | The manuscript check and Curvenote's checks run on every push and post their results and the preview link |
| Author proof | Author, via an editor | Email, then the issue | The author reads the Curvenote preview; an editor ticks *Author proof* |
| Copy edit | Copy editor | A review on the pull request | Read against the [checklist](docs/copy-editor-checklist.md), Part 5, then approved |
| Merge | Editor-in-Chief | The pull request | `submit.yml` sends the article to Curvenote, and the issue closes |
| Volume assembly | Editors-in-Chief | This repository | Front matter, cover, issue DOI and print PDF, then `publish_dispatch.yml` and the website |

The [Volume 4 workflow](docs/volume-4-workflow.md) explains each step, and the role guides below
say how to do them.

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
| [Layout Editor's Guide](docs/layout-editor-guide.md) | MyST conversion, and the most common mistakes |
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
| `lint.yml` | every PR | The manuscript check (`scripts/check_article.py`) on changed articles; results posted on the PR |
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
wrong with no error. The issue DOI must also be set in `frontmatter/volume.yml`; the cover template
requires it.

## Previous volumes

[2026 (Volume 3)](https://github.com/ncssm/morgantonscientific2026) ·
[2025 (Volume 2)](https://github.com/ncssm/morgantonscientific2025) ·
[website](https://github.com/ncssm/morsci-website)
