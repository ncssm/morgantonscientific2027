#!/usr/bin/env python3
"""Draw the README's diagram of how an article gets published.

Writes docs/images/workflow-light.svg and docs/images/workflow-dark.svg; the README shows
whichever matches the reader's GitHub theme. To change the diagram, edit STAGES below and run:

    python3 scripts/workflow_diagram.py

Each stage is (name, what happens, who and where, [what happens automatically]). Start an
automatic line with "~" if it isn't set up yet; it's drawn in gray italics.
"""

from html import escape
from pathlib import Path

TITLE = "An article loops until it is right, and only the merge submits it"

STAGES = [
    ("1. Submission", "Student author fills in the intake Google Form",
     "Who: student author · Not on GitHub: a Google Form",
     ["~Answers land in the intake Sheet", "~Uploads land in the form's Drive"]),
    ("2. Manuscript folder", "Editor puts manuscript, figures, .bib and code in one folder",
     "Who: an editor · Not on GitHub: a shared Drive folder",
     ["Nothing: done by hand, because", "uploads arrive sorted by question"]),
    ("3. Intake", "Copy editor opens a “New article” issue with the folder link",
     "Who: copy editor · On GitHub: an issue, assigned to themselves",
     ["Card lands in Intake on the board", "Assigning notifies the next editor"]),
    ("4. Conversion", "Layout editor opens a PR from article/smith-jones, adds draft",
     "Who: the assigned layout editor · On GitHub: branch and PR",
     ["Issue and PR linked by Closes #", "~Card moves itself to Conversion"]),
    ("5. Checks", "Manuscript check and Curvenote checks run on every push",
     "Who: nobody · On GitHub: the Checks tab",
     ["Bot comment explains each problem", "Curvenote posts the preview link"]),
    ("6. Author proof", "Author reads the Curvenote preview and replies by email",
     "Who: author, via an editor · On GitHub: a tick on the issue",
     ["needs-author label shows the wait", "on the board"]),
    ("7. Copy edit", "Copy editor's read-through of the preview (checklist Part 5)",
     "Who: copy editor · On GitHub: a requested PR review",
     ["Approval counts toward the rule", "that protects main"]),
    ("8. Merge", "Merging submits this one article to Curvenote",
     "Who: Editor-in-Chief · On GitHub: the Merge button",
     ["submit.yml sends it to Curvenote", "Issue closes; card to Submitted"]),
    ("9. Volume assembly and publish", "Front matter, cover, issue DOI, print PDF, then publish",
     "Who: Editors-in-Chief · On GitHub: one assembly issue",
     ["~pdf.yml builds the print PDF", "~Readiness check gates publishing"]),
]
OFF_GITHUB = {0, 1}          # drawn dashed
SUBMITS = 7                  # drawn in the accent color
LOOP_FROM, LOOP_TO = (4, 5, 6), 3
BETWEEN = {7: "once every article is in"}  # label on the arrow below a stage

THEMES = {
    "light": dict(ink="#1f1e1c", quiet="#6b6a66", edge="#b5b2aa", grid="#d9d6cf",
                  tint="#efeeea", accent="#2f6fdd", accent_fill="#e6eefb"),
    "dark": dict(ink="#ecebe7", quiet="#a3a19b", edge="#77756f", grid="#4a4844",
                 tint="#262522", accent="#5b9cf5", accent_fill="#1d2a3d"),
}

W, H0, STEP, BOX_H = 760, 96, 96, 72
SX, SW, AX, AW, CX = 60, 410, 502, 234, 265
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def text(x, y, words, c, size=11.5, weight=400, italic=False, anchor="start", extra=""):
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{c}" '
            f'text-anchor="{anchor}"{style}{extra}>{escape(words)}</text>')


def draw(t: dict) -> str:
    rows = [H0 + STEP * i for i in range(len(STAGES))]
    height = rows[-1] + BOX_H + 24
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" '
           f'height="{height}" font-family="{FONT}" role="img" aria-label="{escape(TITLE)}">',
           f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
           f'markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" '
           f'fill="{t["edge"]}"/></marker></defs>',
           text(24, 34, TITLE, t["ink"], 15, 600),
           text(24, 54, "Dashed outline: before the article reaches GitHub · gray italics: "
                "not set up yet", t["quiet"]),
           text(SX, 82, "Stage, who acts, and where it happens", t["quiet"], weight=600),
           text(AX, 82, "Happens automatically", t["quiet"], weight=600)]

    line = f'fill="none" stroke="{t["edge"]}" stroke-width="1.25"'
    for i, y in enumerate(rows[:-1]):
        out.append(f'<path d="M{CX} {y + BOX_H}V{y + BOX_H + 22}" {line} marker-end="url(#arrow)"/>')
        if i in BETWEEN:
            out.append(text(CX + 10, y + BOX_H + 16, BETWEEN[i], t["quiet"]))
    for i in LOOP_FROM:
        out.append(f'<path d="M{SX} {rows[i] + 36}H36" {line}/>')
    top = rows[LOOP_TO] + 36
    out.append(f'<path d="M36 {rows[max(LOOP_FROM)] + 36}V{top}H{SX - 1}" {line} marker-end="url(#arrow)"/>')
    mid = (top + rows[max(LOOP_FROM)] + 36) / 2
    out.append(text(26, mid, "check fails or changes requested: fix and push", t["quiet"],
                    anchor="middle", extra=f' transform="rotate(-90 26 {mid})"'))

    for i, (name, what, who, auto) in enumerate(STAGES):
        y = rows[i]
        main = i == SUBMITS
        out.append(f'<rect x="{SX}" y="{y}" width="{SW}" height="{BOX_H}" rx="8" '
                   f'fill="{t["accent_fill"] if main else "none"}" '
                   f'stroke="{t["accent"] if main else t["edge"]}" stroke-width="{2 if main else 1.25}"'
                   + (' stroke-dasharray="5 4"' if i in OFF_GITHUB else "") + "/>")
        out.append(text(SX + 16, y + 24, name, t["ink"], 13, 600))
        out.append(text(SX + 16, y + 42, what, t["ink"]))
        out.append(text(SX + 16, y + 58, who, t["quiet"]))
        out.append(f'<line x1="{SX + SW}" y1="{y + 36}" x2="{AX}" y2="{y + 36}" stroke="{t["edge"]}" '
                   'stroke-width="1" stroke-dasharray="3 3"/>')
        out.append(f'<rect x="{AX}" y="{y}" width="{AW}" height="{BOX_H}" rx="8" fill="{t["tint"]}" '
                   f'stroke="{t["grid"]}" stroke-width="1"/>')
        for k, words in enumerate(auto):
            planned = words.startswith("~")
            ly = y + 40 if len(auto) == 1 else y + 32 + 18 * k
            out.append(text(AX + 16, ly, words.lstrip("~"), t["quiet"] if planned else t["ink"],
                            italic=planned))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    folder = Path(__file__).resolve().parent.parent / "docs" / "images"
    folder.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        path = folder / f"workflow-{name}.svg"
        path.write_text(draw(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(folder.parent.parent)}")


if __name__ == "__main__":
    main()
