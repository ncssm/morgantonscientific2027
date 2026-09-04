---
title: CHANGEME — byte-identical to the title in myst.yml
short_title: CHANGEME — a one-line version, for the running header
abstract: |
    One paragraph, 180-250 words, 400 hard maximum. Stands alone: no
    citations, no abbreviations that are not spelled out here.
---

<!-- Headings start at ##. The title comes from frontmatter above; an "#"
     heading would duplicate it. Do not number headings by hand — numbering is
     applied automatically, and two Volume 3 articles carried 29 hand-numbered
     headings that were then numbered a second time in the PDF.

     Do not add a `date:` — the volume publication date is inherited.
     Do not end the file with "---" — it renders as a stray horizontal rule. -->

## Introduction

Body text. Cite with `[@key]` — one key per bracket, or `[@a; @b]` for a group.
Never type a citation as plain text; it will not link to anything.

## Methods

## Results

```{figure} images/CHANGEME.png
:align: center
:name: Figure_1

The caption goes here, after a blank line. It should stand alone: what is
shown, the conditions, what error bars represent, and how many replicates.
```

Reference every figure and table in the prose — `@Figure_1` renders "Figure 1"
and renumbers itself. In Volume 3, 36 of 84 figures were never mentioned at all.

```{table} The caption for a table goes on the fence line, unlike a figure.
:name: Table_1
:align: center

| Group | Value |
|---|---|
| A | 1.0 |
```

## Discussion

## Conclusion
