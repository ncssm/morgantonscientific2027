# Morganton Scientific — Copy Editor's Checklist

For reviewing a submission **before** it goes to a layout editor for conversion. Work through it
once per article, in order — the completeness checks first, because they're the ones that need the
author, and the author is the slowest part of the loop.

Anything you can't resolve, raise with the author immediately rather than passing it downstream.
Every issue caught here costs minutes; the same issue caught after conversion costs an email and a
week.

---

## Part 1 — Completeness

These four checks account for most of what goes wrong.

### 1.1 Every figure and table is referred to in the text

Read through and tick off each figure as you find its mention. A figure the text never refers to is
either decoration or a gap in the argument, and only the author can say which.

> In Volume 3, **36 of 84** figures and tables were never mentioned in the prose. Three papers
> referenced none of their own.

### 1.2 Everything cited appears in the bibliography

Go through the citations in order and confirm each has an entry. A missing entry is a **blocker** —
it can't be resolved without the author, and the longer it waits the less likely they remember.

### 1.3 Everything in the bibliography is cited

The reverse direction. Uncited entries silently disappear from the published reference list, so
they're invisible in proofs — you have to check deliberately.

Ask the author whether each is a dropped citation (put it back) or a leftover (delete it).

### 1.4 Every figure and table has a caption

And the caption should stand alone: what's shown, conditions, what error bars represent, sample
size. A caption reading "Results" is not a caption.

Watch for captions that **begin with their own number** — "Figure 1: Normalized dye…". Numbering is
applied automatically, so a typed number ends up duplicated as "Figure 1: Figure 1: …".

---

## Part 2 — Figures and tables

- [ ] **Numbering follows first mention.** Figure 1 is the first figure referred to. If they're out
      of order, the author renumbers — don't renumber for them, since the text references have to
      move too.
- [ ] **Tables are tables.** Anything with rows and columns is a Table, in its own numbering
      sequence. Charts and graphs are Figures.
- [ ] **No screenshotted tables.** If a "figure" is a picture of a table, send it back and ask for
      the data. Screenshots can't be searched, read aloud, or printed sharply.
- [ ] **Resolution is adequate.** At least 2000 px on the long edge, ideally 300 dpi. Check now —
      once the author has moved on, the original is often gone.
- [ ] **Third-party figures are flagged.** Anything from a paper, website or textbook. We publish
      CC-BY, which we can only grant for material we own. Watch for visible watermarks and
      publication-style multi-panel layouts (a, b, c…) — both are giveaways.

---

## Part 3 — Author metadata

- [ ] **ORCID for every author**, in full form: `0009-0006-7158-659X`
- [ ] **CRediT roles for every author** — see the author guide for the fourteen terms
- [ ] **One corresponding author** named, with a durable email address
- [ ] **Names are consistent** between the manuscript, the email, and the ORCID record. "Alvin Qu"
      and "Alvin L. Qu" must be resolved to one form before conversion.
- [ ] **Affiliations correct.** Don't assume a co-author is from NCSSM — ask. Volume 3 had three
      co-authors from three other high schools.
- [ ] **Five keywords or fewer**, and none duplicating another article in the same volume

---

## Part 4 — Style guide

House style. Apply consistently; flag anything that looks deliberate before changing it.

### Referring to figures and tables

| Use | Not |
|---|---|
| Figure 1 | Fig. 1, Fig 1, fig.1, FIGURE 1 |
| Table 2 | Tab. 2, table 2 |

Spelled out, capitalised, every time — including mid-sentence. This is the house form across all
three volumes.

### Headings

- **No trailing colons.** "General Overview:" → "General Overview"
- **No hand-numbering.** "3.2 Locomotive Ability" → "Locomotive Ability"; numbering is automatic
- **No abbreviation definitions in headings.** Define in the prose on first use instead
- **Sentence case or title case**, consistently within an article

### Titles

- No full stop at the end
- Proofread character by character — it goes into the permanent DOI record
- Species names italicised, lowercase epithet

### Spelling and terminology

- **American English**: modeled, behavior, analyze, aging, characterized, synthesized
- **Species names**: *Drosophila melanogaster*, *Caenorhabditis elegans* — italic, capital genus,
  lowercase species. Not "Drosophila Melanogaster".
- **Product names keep their capitals**: "Instant Drosophila Medium" is a Carolina Biological
  product, not a species
- **Abbreviations** defined in prose on first use, then used consistently. Case matters — HIT and
  Hit are different strings to the publishing system.
- **Numbers and units**: space between value and unit (3.2 mm), consistent decimal places within a
  table

### Abstract

- [ ] Under 400 words; 180–250 is the target
- [ ] Stands alone — no citations, no undefined abbreviations
- [ ] Opens with the work, not a paragraph of background

---

## Part 5 — Read-through

Things only a careful reader catches:

- [ ] **Statistics in the text match the figures and tables.** Check a sample of p-values against
      their source.
- [ ] **Claims are proportionate.** A pilot study with n = 12 shouldn't read as established fact.
- [ ] **Numbers are plausible.** A Volume 3 abstract stated that Parkinson's disease "affects 60% of
      the United States population" — the real figure is around 1%. That one survived every stage of
      review because it reads fluently.
- [ ] **The abstract matches the paper.** Findings described in the abstract actually appear in the
      results.
- [ ] **Acknowledgements are present** where people contributed without being authors.

---

## Handoff

When you pass an article to a layout editor, confirm:

- [ ] Parts 1–4 complete, or every exception listed with a reason
- [ ] Figures supplied as separate full-resolution files, named so the mapping to the text is obvious
- [ ] Tables supplied as text or spreadsheet, not images
- [ ] A `.bib` file, or a clearly formatted reference list
- [ ] Author metadata complete: ORCIDs, CRediT roles, corresponding author, affiliations
- [ ] Any third-party figures flagged, with source

If something is outstanding, say so explicitly in the handoff rather than leaving it to be
discovered. A known gap is manageable; a surprise one late in production is not.
