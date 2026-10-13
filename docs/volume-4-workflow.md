# Volume 4 — how this volume gets made

Written at the end of Volume 3 and carried into this repository as the working plan. Section 1 is the
evidence it rests on; the rest is what to do differently.

Volumes 1–3 were assembled the same way: editors worked in a shared Drive folder all year, and the
whole volume converged on the publishing pipeline at the very end. Everything that was wrong surfaced
at once, months after the authors had moved on.

This proposes a different shape. The goal is not to make students learn git — it's to get each
article into the repository **as soon as it exists**, so that problems surface in days rather than in
June.

---

## 1. What actually cost time in Volume 3

Worth being precise, because it determines where to spend effort.

| Problem | Scale | Caught by Curvenote? |
|---|---|---|
| Figures and tables never mentioned in the prose | **36 of 84** | ❌ |
| Bibliography entries never cited | **60**, across 10 articles | ❌ |
| Hard-coded "Figure 1" in prose | **14 of 15** articles | ❌ |
| `:label:` instead of `:name:` | 24 figures, 4 articles | ❌ |
| Windows backslashes in image paths | 24 paths, 4 articles | partly (build error) |
| Wrong image folder name | 6 articles | partly (build error) |
| Title mismatch between the two files | 4 articles | ❌ |
| Tables submitted as screenshots | 3 tables | ❌ |
| Figure references off by one | 2 articles | ❌ |
| Missing CRediT roles | **15 of 15** | ✅ |
| Missing ORCID | several | ✅ |

**The pattern is the point.** Curvenote runs 13 checks and every one is metadata — abstract, authors,
ORCID, keywords, DOIs, links. Not one reads the manuscript body. The problems it catches are the ones
that take a minute to fix. The problems that consumed the work were all invisible to CI.

Two conclusions follow, and they drive everything below:

1. **Get articles into the repo early**, so the checks that do exist run continuously instead of once.
2. **Add the checks that don't exist**, because the expensive failures are all mechanically detectable.

---

## 2. Principles

**Students keep writing in Google Docs or Word.** Nothing here asks a 16-year-old to learn git or
MyST. The leverage is in converting early and often, not in changing who writes where.

**Each article is its own PR, opened as soon as there's a draft worth converting.** Not fifteen
articles in one branch in May. An article's PR stays open, is pushed to as the author revises, and
carries its full check history.

**A student's proof is the Curvenote preview link**, not a marked-up Word file. They see their
article as it will publish, on their own PR, and can say "figure 3 is wrong" while it's still cheap.

**Editors never chase what a machine can tell them.** Every failure mode above that can be detected
should be detected automatically, before a human reads the article.

---

## 3. The pipeline

The diagram in the [README](../README.md#how-an-article-gets-published) shows these stages at a glance,
with who acts at each.

### Stage 0 — Intake (at submission, not at the end)

The single highest-value change. **Author metadata is collected with the manuscript, not chased in
May.** CRediT roles were the last thing holding up Volume 3, and by then the students had scattered.

A short form, filled in once per article by the corresponding author:

- Full name, as it should appear
- ORCID (with the registration link inline — it takes two minutes)
- Email that survives graduation
- CRediT roles per author (checkbox list of the 14)
- Up to 5 keywords
- Subject area
- Any figure not created by the authors, with its source

That's ten minutes for the author and eliminates four of Volume 3's blockers. A Google Form writing
to a Sheet is entirely adequate — the layout editor copies fields into `myst.yml`.

**The copy editor opens the article's issue** the day the manuscript arrives, using the *New
article* issue form, and assigns themselves. They then make the first pass of the
[copy editor's checklist](copy-editor-checklist.md) — Parts 1–4, on the manuscript itself — and
chase the author for anything missing while the author is still around. When everything is in,
they assign the layout editor on the issue in their place.

**The issue's assignee is always whoever has the next action**, so "what am I waiting on" is
answered by the issues assigned to you.

**Gate:** no article enters the repository without a completed intake form.

### Stage 1 — Conversion

The layout editor assigned on the issue converts the manuscript to MyST following the
[layout editor guide](layout-editor-guide.md), and opens a PR: **one article, one folder, one PR**,
`draft`-labelled, with `Closes #<issue>` in its description so that merging closes the issue. Once
the checks are green, they request the copy editor's review on the PR.

**Gate:** CI green — Curvenote's metadata checks *and* the manuscript checks in §4.

### Stage 2 — Author proof

The author gets the Curvenote preview URL from their PR and confirms: figures are the right ones and
in the right order, tables read correctly, the abstract is right, their name and affiliation are
right.

This is the step Volumes 1–3 never really had, and it's where transcription errors get caught by the
one person who can actually catch them.

**Gate:** the author approves the preview. Students don't have GitHub accounts, so they reply by
email, and an editor ticks *Author proof* on the article's issue and pastes the reply as a comment.

### Stage 3 — Copy edit

The copy editor's second pass: Part 5 of the [checklist](copy-editor-checklist.md), the
read-through, against the rendered preview. Completeness and house style were settled before
conversion and the mechanical checks have passed, so the copy editor is reading for sense,
proportionate claims, and statistics that match their figures — not hunting for missing captions.

**Gate:** the copy editor approves the PR.

### Stage 4 — Merge

Merging submits that article to Curvenote. Articles accumulate in the collection through the year
rather than arriving in one batch.

### Stage 5 — Volume assembly

Once all articles are in: front matter, cover art and credit, running order, the issue DOI, the print
PDF. This is the only genuinely end-loaded work, and it is small when the articles are already done.

Two things that force a rebuild if they're done in the wrong order:

- **Pagination is computed from final content.** `scripts/make_pdfs.sh` writes `first_page` /
  `last_page` into every `myst.yml`, so run it *after* the last content change. Even a one-line edit
  can move an article by a page and shift everything after it.
- **Install the Noto fonts before building.** The template sets `Noto Sans` and `Noto Serif`; without
  them typst substitutes silently, with no error, and the page numbers come out wrong while the PDF
  looks entirely normal.

### Stage 6 — Publish

`publish_dispatch.yml`, manually. It submits all articles fresh and then publishes each, so it picks
up any metadata change made since the last submission.

This is the irreversible step: the DOIs go live. Two things to know beforehand —

- **A failing check will not stop it.** `strict` defaults to `false`, so checks report but do not
  gate publication.
- **Ask Curvenote what withdrawal looks like** before pressing it. Whether an article can be pulled
  after publication, and what happens to a minted DOI, is not answerable from the code.

### Stage 7 — The website

**Publishing a volume does not put it on the website.** That is a separate repository and a separate
step, and it is easy to forget.

[`ncssm/morsci-website`](https://github.com/ncssm/morsci-website) holds the landing pages at
<https://morgantonscientific.ncssm.edu>. Its README documents the procedure; in outline it is four
files, two of them one-line changes: a new `<year>.md`, a section at the top of `articles.md`, the
collection name in `index.md`, and a line in the `myst.yml` table of contents.

Two things that repository does differently, and they are easy to get wrong coming from here:

- **There is no preview and no checks.** Push to `main` and the site is live in a couple of minutes.
- **`:collection:` must match** what this repository submits under. If they disagree the listing
  renders empty, with no error on either side.

### Stage 8 — Archive the print PDF

`morganton2027.pdf` is gitignored build output. Cut a GitHub release on this repository and attach
it — Volume 3 is at [`v3.0`](https://github.com/ncssm/morgantonscientific2026/releases/tag/v3.0).
That gives a permanent, versioned link, and room for a `v4.1` if errata ever need a corrected PDF.

The volume's `frontmatter/` project also carries a `Download Full PDF` declaration and reaches
Curvenote separately, which is what puts the PDF on the site's `/volumes` page — so the release is an
archive rather than the only copy.

---

## 4. The checks to add

This is the concrete engineering, and it's modest — one script in CI, run per article on every PR.
Each rule below maps to a real Volume 3 failure.

**Blocking:**

| Check | Volume 3 |
|---|---|
| Every figure and table is referenced at least once in the prose | 36 of 84 |
| Every `{figure}`/`{table}` has `:name:` and not `:label:` | 24 figures |
| No hard-coded `Figure N` / `Table N` / `Fig. N` outside captions | 14 of 15 articles |
| `title` identical in `myst.yml` and `article.md` | 4 articles |
| No `site:` key, no article-level `date:` | 14 and 3 articles |
| `id` matches the pattern and the suffix is ≤ 15 characters | 1 article |
| `affiliation` is lowercase `ncssm` | 8 articles |
| Every cited key exists in the `.bib` | 1 article |
| No hand-numbered headings (`### 3.1 Results`) | 29 headings, 2 articles |
| No bare bib key in parentheses — `(smith2020)` instead of `[@smith2020]` | 3, in 1 article |
| No typed citation — `(Smith, 2020)` as plain text | 5, in 1 article |
| No duplicate bibliography entries (same DOI or PMID twice) | 1 article |

**Warning (report, don't block):**

| Check | Volume 3 |
|---|---|
| Bibliography entries never cited | 60 |
| Abbreviations defined but never used | 13 |
| Figure filename contains "table" — possible screenshotted table | 3 |
| Abstract outside 180–250 words | several |
| Frontmatter headings match the TOC entries in `generate_summary.sh` | out of step in 2 volumes |
| Every DOI and URL resolves **in a browser**, not just to an automated request | 3 dead links |

Roughly 150 lines of Python over the built MyST AST — which is where to read it, since the AST has
resolved cross-references and citations. Reading `article.md` with regexes would miss the ways the
source text and the rendered output differ.

Add it as `scripts/check_article.py`, called from a new `lint.yml` on every PR. It needs no Curvenote
token, so it runs on forks and is fast.

**Worth writing this before articles start arriving**, not during. It can be validated against
[Volume 3](https://github.com/ncssm/morgantonscientific2026) — every rule above should flag exactly
the cases we know about there, which is a free and rigorous test.

The argument for it got stronger at the end of Volume 3. The 29 hand-numbered headings were caught
by eye, in the print PDF, days before publication — and they were **already prohibited** by both the
author guide and the copy editor checklist. The rule was written down, circulated, and still missed.
Documenting a rule does not enforce it; this one is three lines of regex.

---

## 5. Workflow configuration

**Already done in this repository** — recorded so nobody re-derives it.

The workflows call `curvenote/actions@v1`, which resolves to `v1.0.21` or later, so papers and essays
can be submitted in the same push. Earlier versions crashed when both ran in one push
([curvenote/actions#57](https://github.com/curvenote/actions/issues/57)); if a `summary` job ever
fails with `Cannot read properties of undefined`, check that the action version hasn't slipped
backwards.

Each job also sets a distinct `comment-title`. Without it the papers and essays previews overwrite
each other's PR comment and you can only ever see one.

`papers/_template` is in the `exclude` list of all four workflows. Without that the template folder
is treated as a submission.

Four workflows, and it is worth knowing which does what:

| Workflow | Trigger | Effect |
|---|---|---|
| `draft.yml` | PR labelled `draft` | Preview + checks. Nothing is submitted |
| `submit.yml` | push to `main` | Submits **changed** articles as new versions |
| `resubmit_dispatch.yml` | manual | Submits **all** articles. Use after a change to `frontmatter/` or shared config, which no article path glob matches |
| `publish_dispatch.yml` | manual | Submits all, then **publishes**. The irreversible one |

---

## 6. Repository changes

**Already in this repository:**

- **`papers/_template/`** — copy it to `papers/<lastname>/` and fill in the `CHANGEME`s. Every field
  carries a comment explaining the trap it exists to avoid. Copying another article
  instead tends to carry its title words and metadata into yours.
- **`docs/`** — the three role guides, carried over, with a table of common mistakes.
- **The workflows**, configured as in §5.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — links the PR to the article's issue with `Closes #`, so
  merging closes it. The stage checklist lives on the issue only.
- **A "New article" issue form** (`.github/ISSUE_TEMPLATE/new-article.yml`) — one issue per article,
  opened the day the manuscript arrives. It records what has been received and which stage the
  article has reached, and closes when the article's PR merges.
- **The manuscript check** — `scripts/check_article.py`, run by `lint.yml` on every PR, as in §4.
  Validated against Volume 3: before its editorial fixes it reproduces every count in §1, and on
  the published volume it finds only problems that really shipped. `scripts/tests/` holds a
  clean article and one with every mistake planted, which doubles as a practice article.

**Still to build:**

- **A project board** with a column per stage, fed by the article issues. Fifteen open PRs are hard
  to survey; a board makes "what is blocked on the author" answerable at a glance.

---

## 7. Calendar

Dates are illustrative — you know the academic year. The shape matters more than the months.

| When | What |
|---|---|
| Early autumn | Editors appointed; guides circulated to prospective authors **before** they write |
| Rolling | Articles converted and PR'd as drafts become available |
| Rolling | Author proof and copy edit per article |
| Late winter | **Submissions close.** Everything not converted by this date is Volume 5 |
| Early spring | Last articles merged; front matter, cover art, editors' note |
| Mid spring | Issue DOI from Curvenote; pagination; print PDF |
| Late spring | Publish |

The important line is **submissions close**, and holding it. Volume 3's real problem wasn't any single
defect — it was that everything arrived simultaneously with no slack behind it.

---

## 8. Before articles start arriving

1. ~~**Write `scripts/check_article.py`** and validate it against Volume 3's fifteen articles.~~
   Done; once it has run on a PR, make it a required check on `main` (Settings → Rules).
2. **Draft the intake form** and agree with the editors that it gates submission. CRediT roles were
   the last thing holding up Volume 3, by which point the authors had scattered.
3. **Commission the cover art early**, and get the credit line with it.
   `templates/ncssm-preface/banner.jpg` is still Volume 3's cover by Layla Ibrahim — it must be
   replaced before publication.
4. **Fill in the volume metadata** — `frontmatter/volume.yml` and `frontmatter/myst.yml` both carry
   `TODO(2027)` markers for the publication date, the issue DOI and the editors.
5. **Build the print PDF once, early**, with a single dummy article. It exercises the typst path,
   which nothing else does, and confirms the toolchain before it matters. Volume 3 discovered a
   broken template function, a stale cover and wrong page numbers at the very end.

---

## Open questions

- **How many layout editors, and how comfortable with git?** The plan assumes at least one confident
  with PRs. If not, conversion can be centralised and the rest of the workflow is unchanged.
- **Can the intake form be made a condition of submission?** It works only as a gate, not a request.
- **Do authors reliably respond after submitting?** Stage 2 depends on it. If they do not, the proof
  step moves earlier — before an article is considered received.
- **Is there an interviews section this year?** Volume 2 had one, Volume 3 did not. It adds a third
  `kind` and a third pair of jobs to each workflow.
- **Who owns the website step?** Stage 7 is in a different repository with different habits — no
  preview, no checks. Worth naming a person rather than assuming it falls to whoever published.

---

## What Volume 3 actually cost

For calibration, since the pitch above is "spend a little early to save a lot late". Volume 3 arrived
as a Drive folder in June and published on 1 September. The preparation work included:

- 81 broken image paths, 24 figures using `:label:` instead of `:name:`, 24 Windows path separators
- 36 of 84 figures and tables never referenced; 29 hand-numbered headings; 3 tables as screenshots
- 60 uncited bibliography entries; 3 dead links; 1 duplicate entry; 8 hand-typed citations
- CRediT roles collected from nobody, resolved only in the final week
- A print PDF that had never been built, against a template calling a removed typst function

Almost none of that needed judgement. It needed someone to notice — which is what §4 is for.
