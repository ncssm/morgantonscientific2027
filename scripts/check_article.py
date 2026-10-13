#!/usr/bin/env python3
"""Manuscript checks for Morganton Scientific articles.

Curvenote's checks read an article's metadata. These read the manuscript itself:
figures that are never mentioned, hard-coded figure numbers, typed citations,
hand-numbered headings and the other mistakes in docs/layout-editor-guide.md.

Each article is built with MyST first, and most checks read the built AST,
where cross-references and citations are already resolved. The rest read
myst.yml, article.md and refs.bib directly.

    python scripts/check_article.py papers/smith            # one article
    python scripts/check_article.py                         # every article
    python scripts/check_article.py --changed-since origin/main

Errors exit 1. Warnings are reported but don't fail the check.

Needs PyYAML, and the MyST CLI (`myst`) on the path; set MYST_CMD to use
something else, e.g. MYST_CMD="npx --yes mystmd@1.10.1".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
GUIDE = "docs/layout-editor-guide.md"
AUTHOR_GUIDE = "docs/author-guide.md"

# Changing any of these can affect every article, so they trigger a full run.
SHARED = re.compile(r"^(morganton\d{4}\.yml|frontmatter/volume\.yml|scripts/check_article\.py"
                    r"|\.github/workflows/lint\.yml)$")

# MyST warnings that say nothing about the manuscript. The PDF is only built for
# print, so a missing article.pdf download is expected everywhere else.
BENIGN_WARNINGS = [
    re.compile(r'Could not find static resource at "article\.pdf"'),
    re.compile(r"to convert to webp"),
]

CREDIT_ROLES = [
    "Conceptualization", "Data curation", "Formal analysis", "Funding acquisition",
    "Investigation", "Methodology", "Project administration", "Resources", "Software",
    "Supervision", "Validation", "Visualization", "Writing – original draft",
    "Writing – review & editing",
]
SUBJECTS = ["Biology", "Chemistry", "Physics", "Engineering", "Public Health", "Computer Science"]
SEVERITIES = {"ignore", "warn", "error"}

# Fields an article's myst.yml may set; used only to catch wrongly capitalised keys.
KNOWN_KEYS = {
    "version", "extends", "project", "id", "title", "short_title", "subtitle", "description",
    "keywords", "authors", "subject", "abbreviations", "thumbnail", "exclude", "error_rules",
    "doi", "first_page", "last_page", "date", "site", "bibliography", "exports", "downloads",
    "license", "github", "venue", "volume", "issue", "affiliations", "funding", "banner",
}

HARD_CODED_REF = re.compile(r"\b(?:Fig(?:ure)?s?\.?|Tables?)\s?\d+")
NUMBERED_HEADING = re.compile(r"^\s*(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s+\S")
CAPTION_NUMBER = re.compile(r"^\s*(?:Fig(?:ure)?\.?|Table)\s*\d+\s*[:.\-–—]")
TYPED_CITATION = re.compile(
    r"\((?:see |e\.g\.,? )?[A-Z][\w'’\-]+(?: [A-Z][\w'’\-]+)*(?: et al\.?)?"
    r"(?:,? (?:and|&) [A-Z][\w'’\-]+)?,? "
    r"(?:19|20)\d{2}[a-z]?(?:[;,][^)]*)?\)")
FIGURE_PATH = re.compile(r"^`{3,}\s*\{(?:figure|image)\}\s*(\S.*?)\s*$")
SKIP_INSIDE = {"caption", "crossReference", "cite", "citeGroup", "link", "code", "inlineCode",
               "legend", "abbreviation"}


@dataclass
class Finding:
    severity: str  # "error" or "warning"
    rule: str
    message: str
    file: Path
    line: int | None = None
    guide: str | None = None  # path#anchor


class Article:
    def __init__(self, folder: Path, root: Path):
        self.folder = folder
        self.root = root
        self.rel = folder.relative_to(root)
        self.findings: list[Finding] = []
        self.myst_path = folder / "myst.yml"
        self.md_path = folder / "article.md"
        self.myst_text = self.myst_path.read_text(encoding="utf-8")
        self.md_text = self.md_path.read_text(encoding="utf-8") if self.md_path.exists() else ""
        self.myst = yaml.safe_load(self.myst_text) or {}
        self.project = self.myst.get("project") or {}
        self.md_meta, self.body_offset = split_frontmatter(self.md_text)
        self.bib_path = next(iter(sorted(folder.glob("*.bib"))), None)
        self.bib = parse_bib(self.bib_path.read_text(encoding="utf-8")) if self.bib_path else []
        self.ast: dict | None = None
        self.myst_warnings: list[tuple[Path, int | None, str]] = []

    def add(self, severity, rule, message, file=None, line=None, guide=None):
        self.findings.append(Finding(severity, rule, message, file or self.myst_path, line, guide))

    def myst_line(self, pattern: str) -> int | None:
        return line_of(self.myst_text, pattern)

    def md_line(self, pattern: str) -> int | None:
        return line_of(self.md_text, pattern)


# --- helpers -------------------------------------------------------------------------------

def line_of(text: str, pattern: str) -> int | None:
    rx = re.compile(pattern)
    for n, line in enumerate(text.splitlines(), 1):
        if rx.search(line):
            return n
    return None


def split_frontmatter(text: str) -> tuple[dict, int]:
    """Return (frontmatter, number of lines it occupies)."""
    if not text.startswith("---"):
        return {}, 0
    lines = text.splitlines()
    for n in range(1, len(lines)):
        if lines[n].strip() == "---":
            try:
                meta = yaml.safe_load("\n".join(lines[1:n])) or {}
            except yaml.YAMLError:
                meta = {}
            return (meta if isinstance(meta, dict) else {}), n + 1
    return {}, 0


def parse_bib(text: str) -> list[dict]:
    """A small BibTeX reader: enough for keys, DOIs and line numbers."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in {"comment", "preamble", "string"}:
            continue
        start = m.end()
        nxt = re.search(r"\n\s*@\w+\s*\{", text[start:])
        chunk = text[start:start + nxt.start()] if nxt else text[start:]
        doi = re.search(r"\bdoi\s*=\s*[{\"]\s*([^}\"]+)", chunk, re.I)
        author = re.search(r"\bauthor\s*=\s*[{\"]\s*([^,}\"]+?)(?:,| and |[}\"])", chunk, re.I)
        year = re.search(r"\b(?:year|date)\s*=\s*[{\"]?\s*(\d{4})", chunk, re.I)
        pmid = re.search(r"\bpmid\s*=\s*[{\"]?\s*(\d+)", chunk, re.I)
        url = re.search(r"\burl\s*=\s*[{\"]\s*([^}\"\s]+)", chunk, re.I)
        entries.append({
            "key": m.group(2),
            "doi": normalise_doi(doi.group(1)) if doi else None,
            # Anything that identifies the work, for spotting duplicates.
            "ids": {x for x in (doi and "doi:" + normalise_doi(doi.group(1)),
                                pmid and "pmid:" + pmid.group(1),
                                url and "url:" + url.group(1).rstrip("/").lower()) if x},
            "surname": author.group(1).strip().split()[-1].strip("{}").lower() if author else None,
            "year": year.group(1) if year else None,
            "line": text.count("\n", 0, m.start()) + 1,
        })
    return entries


def normalise_doi(doi: str) -> str:
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.I).lower()


def orcid_ok(orcid: str) -> bool:
    digits = orcid.replace("-", "")
    total = 0
    for d in digits[:15]:
        total = (total + int(d)) * 2
    check = (12 - total % 11) % 11
    return digits[15] == ("X" if check == 10 else str(check))


def credit_key(role: str) -> str:
    return re.sub(r"[^a-z]", "", role.lower().replace("&", "and"))


CREDIT_KEYS = {credit_key(r): r for r in CREDIT_ROLES}


def walk(node, ancestors=()):
    yield node, ancestors
    for child in node.get("children") or []:
        yield from walk(child, ancestors + (node,))


def text_of(node, skip=frozenset()) -> str:
    if node.get("type") in skip:
        return ""
    if node.get("type") == "text":
        return node.get("value", "")
    return "".join(text_of(c, skip) for c in node.get("children") or [])


def ast_line(node, ancestors) -> int | None:
    """The line in article.md: AST positions count from the top of the file. Figures carry no
    position of their own, so fall back to their first child that does, then to an ancestor."""
    for n, _ in walk(node):
        if n.get("position"):
            return n["position"]["start"]["line"]
    for n in reversed(ancestors):
        if n.get("position"):
            return n["position"]["start"]["line"]
    return None


def volume_info(root: Path) -> tuple[set[str], set[str]]:
    path = root / "frontmatter" / "volume.yml"
    if not path.exists():
        return {"ncssm"}, set()
    project = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("project") or {}
    affs = {a["id"] for a in project.get("affiliations") or [] if isinstance(a, dict) and "id" in a}
    return affs or {"ncssm"}, set((project.get("abbreviations") or {}).keys())


# --- metadata checks (myst.yml, article.md frontmatter) ------------------------------------

def check_metadata(a: Article, affiliations: set[str], volume_abbr: set[str]):
    p, f = a.project, a.myst_path

    for path, text in ((a.myst_path, a.myst_text), (a.md_path, a.md_text)):
        for n, line in enumerate(text.splitlines(), 1):
            if "CHANGEME" in line:
                a.add("error", "placeholder", "A CHANGEME placeholder from the article template "
                      "is still here.", path, n)

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", a.folder.name):
        a.add("error", "folder-name", f"The folder name '{a.folder.name}' must be lowercase "
              "letters and digits, with hyphens between names — no spaces, capitals or '&'.",
              f, None, f"{GUIDE}#1-folder-layout")

    extends = a.myst.get("extends") or []
    extends = [extends] if isinstance(extends, str) else extends
    year = next((m.group(1) for e in extends if (m := re.search(r"morganton(\d{4})\.yml$", str(e)))),
                None)
    if not year:
        a.add("error", "extends", "myst.yml must extend the volume config, e.g. "
              "'extends: ../../morganton2027.yml'. Without it the article inherits no venue, "
              "affiliation, licence or PDF template.", f, a.myst_line(r"^extends"),
              f"{GUIDE}#field-by-field")

    pid = str(p.get("id") or "")
    year_rx = year or r"\d{4}"
    if not re.fullmatch(rf"morganton-{year_rx}-[A-Za-z0-9_-]{{2,15}}", pid):
        a.add("error", "id", f"The id '{pid}' must be 'morganton-{year or 'YYYY'}-' followed by 2 "
              "to 15 letters, digits, hyphens or underscores.", f, a.myst_line(r"^\s*id:"),
              f"{GUIDE}#field-by-field")

    if "site" in a.myst:
        a.add("error", "site", "Remove the 'site:' block. The theme comes from the volume config, "
              "and an article-level one conflicts with it.", f, a.myst_line(r"^site:"),
              f"{GUIDE}#do-not-include")

    if "date" in p:
        a.add("error", "date", "Remove 'date:' from myst.yml. The volume publication date is "
              "inherited, and an article-level date overrides it.", f, a.myst_line(r"^\s*date:"),
              f"{GUIDE}#3-articlemd")
    if "date" in a.md_meta:
        a.add("error", "date", "Remove 'date:' from the article.md frontmatter. The volume "
              "publication date is inherited, and an article-level date overrides it.",
              a.md_path, a.md_line(r"^date:"), f"{GUIDE}#3-articlemd")

    for key in [*a.myst.keys(), *p.keys()]:
        if key != key.lower() and key.lower() in KNOWN_KEYS:
            a.add("error", "key-case", f"'{key}:' should be '{key.lower()}:'. MyST ignores fields "
                  "with the wrong capitalisation, silently.", f, a.myst_line(rf"^\s*{re.escape(key)}:"))

    title, md_title = " ".join(str(p.get("title") or "").split()), " ".join(
        str(a.md_meta.get("title") or "").split())
    if not title or not md_title:
        a.add("error", "title", "The title must be set in both myst.yml and article.md.", f,
              a.myst_line(r"^\s*title:"), f"{GUIDE}#field-by-field")
    elif title != md_title:
        a.add("error", "title", f"The titles in myst.yml and article.md differ:\n  myst.yml: "
              f"{title}\n  article.md: {md_title}", f, a.myst_line(r"^\s*title:"),
              f"{GUIDE}#field-by-field")

    desc = str(p.get("description") or "").strip()
    if not desc:
        a.add("error", "description", "Add a 'description:' of 2-4 sentences. It drives the "
              "listing card and search results.", f, None, f"{GUIDE}#field-by-field")
    elif re.search(r"[*_`]", desc) or not desc.isascii():
        a.add("warning", "description", "Keep the description plain ASCII, with no markdown "
              "emphasis or symbols. It's shown in places where markup won't render.", f,
              a.myst_line(r"^\s*description:"), f"{GUIDE}#field-by-field")

    keywords = p.get("keywords") or []
    if not keywords:
        a.add("error", "keywords", "Add up to five 'keywords:'. Curvenote requires them.", f,
              None, f"{GUIDE}#field-by-field")
    elif len(keywords) > 5:
        a.add("error", "keywords", f"There are {len(keywords)} keywords; Curvenote allows at most "
              "5.", f, a.myst_line(r"^\s*keywords:"), f"{GUIDE}#field-by-field")

    subject = p.get("subject")
    if not subject:
        a.add("error", "subject", f"Add a 'subject:', one of: {', '.join(SUBJECTS)}.", f)
    elif subject not in SUBJECTS:
        a.add("warning", "subject", f"'{subject}' isn't one of the volume's subjects: "
              f"{', '.join(SUBJECTS)}.", f, a.myst_line(r"^\s*subject:"))

    thumb = p.get("thumbnail")
    if not thumb:
        a.add("warning", "thumbnail", "Add a 'thumbnail:': a figure from the article, or the "
              "NCSSM logo if there isn't a suitable one.", f, None, f"{GUIDE}#field-by-field")
    elif not (a.folder / str(thumb)).exists():
        a.add("error", "thumbnail", f"The thumbnail '{thumb}' doesn't exist.", f,
              a.myst_line(r"^\s*thumbnail:"))

    check_authors(a, affiliations)

    abbr = p.get("abbreviations")
    if abbr is not None and not isinstance(abbr, dict):
        a.add("error", "abbreviations", "'abbreviations:' must be a mapping, one 'KEY: expansion' "
              "per line, not a list with dashes.", f, a.myst_line(r"^\s*abbreviations:"),
              f"{GUIDE}#field-by-field")
    elif abbr:
        for key in abbr:
            if key in volume_abbr:
                a.add("warning", "abbreviation-volume", f"'{key}' is already defined for the "
                      "whole volume; remove it here.", f, a.myst_line(rf"^\s*{re.escape(str(key))}:"))

    for rule in p.get("error_rules") or []:
        if isinstance(rule, dict) and rule.get("severity") not in SEVERITIES:
            a.add("error", "error-rules", f"In error_rules, severity '{rule.get('severity')}' isn't "
                  "valid. Use exactly ignore, warn or error; any other value makes Curvenote "
                  "discard the whole rule.", f, a.myst_line(r"^\s*severity:"),
                  f"{GUIDE}#error_rules--waiving-a-check-with-a-reason")

    abstract = a.md_meta.get("abstract")
    if a.rel.parts[0] == "papers":
        words = len(str(abstract or "").split())
        if not abstract:
            a.add("error", "abstract", "Add an 'abstract:' to the article.md frontmatter.", a.md_path)
        elif words > 400:
            a.add("error", "abstract", f"The abstract is {words} words; Curvenote allows at most 400.",
                  a.md_path, a.md_line(r"^abstract:"))
        elif not 180 <= words <= 250:
            a.add("warning", "abstract", f"The abstract is {words} words; the house target is "
                  "180-250.", a.md_path, a.md_line(r"^abstract:"), f"{AUTHOR_GUIDE}#4-your-abstract")


def check_authors(a: Article, affiliations: set[str]):
    f = a.myst_path
    authors = a.project.get("authors")
    if not isinstance(authors, list) or not authors:
        a.add("error", "authors", "'authors:' must be a list, with every entry starting '- name:'.",
              f, a.myst_line(r"^\s*authors:"), f"{GUIDE}#field-by-field")
        return
    for author in authors:
        if not isinstance(author, dict) or not author.get("name"):
            a.add("error", "authors", "Every author needs a 'name:'.", f, a.myst_line(r"^\s*authors:"))
            continue
        name = author["name"]
        line = a.myst_line(rf"name:\s*['\"]?{re.escape(str(name))}")

        affs = author.get("affiliations") or author.get("affiliation") or []
        for aff in [affs] if isinstance(affs, str) else affs:
            if aff not in affiliations:
                a.add("error", "affiliation", f"{name}: affiliation '{aff}' isn't defined for the "
                      f"volume (use {', '.join(sorted(affiliations))}). An unknown id creates a bare "
                      "affiliation and drops the address and ROR ID.", f, line,
                      f"{GUIDE}#field-by-field")

        orcid = re.sub(r"^https?://orcid\.org/", "", str(author.get("orcid") or "").strip())
        if not orcid:
            a.add("error", "orcid", f"{name}: add an ORCID.", f, line, f"{GUIDE}#field-by-field")
        elif not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", orcid):
            a.add("error", "orcid", f"{name}: '{orcid}' isn't a full ORCID; use the form "
                  "0000-0002-1825-0097.", f, line, f"{GUIDE}#field-by-field")
        elif not orcid_ok(orcid):
            a.add("error", "orcid", f"{name}: the ORCID {orcid} has the wrong check digit, so a "
                  "digit is probably mistyped. Copy it from the intake sheet again.", f, line,
                  f"{GUIDE}#field-by-field")

        roles = author.get("roles") or []
        if not roles:
            a.add("error", "credit", f"{name}: add CRediT 'roles:'. The venue requires them for "
                  "every author.", f, line, f"{GUIDE}#field-by-field")
        for role in roles:
            if credit_key(str(role)) not in CREDIT_KEYS:
                a.add("error", "credit", f"{name}: '{role}' isn't a CRediT role. The 14 roles "
                      "are listed in the author guide.", f, line,
                      f"{AUTHOR_GUIDE}#your-contribution--credit-roles")


# --- article.md source checks --------------------------------------------------------------

def check_source(a: Article) -> set[str]:
    """Checks on article.md as written. Returns the image paths it references."""
    md, used = a.md_path, set()
    lines = a.md_text.splitlines()
    in_fence = False
    for n, line in enumerate(lines, 1):
        m = FIGURE_PATH.match(line)
        if m:
            path = m.group(1)
            used.add(path.replace("\\", "/"))
            if "\\" in path:
                a.add("error", "image-path", f"'{path}' uses backslashes. Use forward slashes; "
                      "backslashes fail on GitHub's Linux machines.", md, n, f"{GUIDE}#image-paths")
            elif not (a.folder / path).exists():
                a.add("error", "image-path", f"'{path}' doesn't exist.", md, n, f"{GUIDE}#image-paths")
            if "table" in Path(path).name.lower() and "{figure}" in line:
                a.add("warning", "table-image", f"'{path}' looks like a table saved as an image. "
                      "Tables should be typed out as a {table}.", md, n,
                      f"{GUIDE}#tables-are-table-not-figure")
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if re.match(r"^:label:", line):
            a.add("error", "label", "Use ':name:', not ':label:'. A :label: can't be referenced.",
                  md, n, f"{GUIDE}#4-figures-and-tables")
        if n > a.body_offset and not in_fence and re.match(r"^#\s", line):
            a.add("error", "h1", "Headings start at '##'. The title comes from the frontmatter, "
                  "so a '#' heading duplicates it.", md, n, f"{GUIDE}#3-articlemd")
        if re.match(r"^#{1,6}\s+Author Information\s*$", line, re.I):
            a.add("error", "author-information", "Remove the 'Author Information' section. The "
                  "corresponding author and contributions belong in myst.yml.", md, n,
                  f"{GUIDE}#3-articlemd")
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", a.md_text):
        used.add(m.group(1))
    tail = [l for l in lines if l.strip()]
    if len(lines) > a.body_offset and tail and tail[-1].strip() == "---":
        a.add("error", "trailing-rule", "Remove the '---' at the end of the file; it renders as a "
              "stray horizontal rule.", md, len(lines), f"{GUIDE}#3-articlemd")
    return used


def check_images(a: Article, used: set[str]):
    images = a.folder / "images"
    if not images.is_dir():
        return
    thumb = str(a.project.get("thumbnail") or "")
    referenced = {str((a.folder / u).resolve()) for u in used | {thumb} if u}
    for path in sorted(images.rglob("*")):
        if path.is_file() and not path.name.startswith(".") and str(path.resolve()) not in referenced:
            a.add("warning", "unused-image", f"{path.relative_to(a.folder)} isn't used by any "
                  "figure. Delete it, or add the figure it belongs to.", path)


# --- build and AST checks ------------------------------------------------------------------

def build(a: Article) -> bool:
    """Build the article with MyST. Keeps its warnings for later, and loads the AST."""
    cmd = shlex.split(os.environ.get("MYST_CMD", "myst")) + ["build", "--site"]
    try:
        proc = subprocess.run(cmd, cwd=a.folder, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        sys.exit(f"Can't run {cmd[0]!r}. Install MyST (npm install -g mystmd) or set MYST_CMD.")
    output = re.sub(r"\x1b\[[0-9;]*m", "", proc.stdout + proc.stderr)
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith(("⚠️", "⛔️", "🚨")) or any(b.search(line) for b in BENIGN_WARNINGS):
            continue
        text = line.lstrip("⚠️⛔️🚨\ufe0f ").replace(str(a.folder) + "/", "").replace(str(a.folder), ".")
        loc = re.match(r"([\w./-]+\.(?:md|yml|bib))(?::(\d+))?(?::\d+)?\s+(.*)", text)
        file, lineno, message = (a.folder / loc.group(1), loc.group(2), loc.group(3)) if loc else (a.md_path, None, text)
        warning = (file if file.exists() else a.md_path, int(lineno) if lineno else None, message)
        if warning not in a.myst_warnings:
            a.myst_warnings.append(warning)
    content = a.folder / "_build" / "site" / "content"
    for path in sorted(content.glob("*.json")) if content.is_dir() else []:
        data = json.loads(path.read_text(encoding="utf-8"))
        if str(data.get("location", "")).endswith("article.md"):
            a.ast = data
            return True
    a.add("error", "build", "MyST couldn't build this article, so most checks didn't run. "
          "The build output is in the job log.", a.md_path)
    return False


# MyST warnings that the checks above already explain in plainer words.
COVERED = [
    (re.compile(r"extra key ignored: (\S+)"), lambda m, msgs: f"'{m.group(1)}:'" in msgs),
    (re.compile(r"'abbreviations' must be object"), lambda m, msgs: "'abbreviations:' must be" in msgs),
    (re.compile(r"'severity' invalid value"), lambda m, msgs: "In error_rules, severity" in msgs),
    (re.compile(r'Cannot find image "([^"]+)"'), lambda m, msgs: f"'{m.group(1)}'" in msgs),
    (re.compile(r'Could not link citation with label "([^"]+)"'), lambda m, msgs: m.group(1) in msgs),
]


def add_build_warnings(a: Article):
    """Report MyST's own warnings, except those a check has already explained."""
    messages = "\n".join(x.message for x in a.findings)
    for file, line, text in a.myst_warnings:
        if any((m := rx.search(text)) and covered(m, messages) for rx, covered in COVERED):
            continue
        a.add("error", "build", "MyST reported: " + text, file, line)


def check_ast(a: Article):
    md, mdast = a.md_path, a.ast["mdast"]
    labels, refs, cites, used_abbr = {}, set(), [], set()

    for node, anc in walk(mdast):
        t = node.get("type")
        if t == "container" and node.get("kind") in {"figure", "table"}:
            kind = node["kind"]
            if node.get("identifier"):
                labels[node["identifier"]] = (node, anc)
            else:
                a.add("error", "unnamed", f"This {kind} has no ':name:', so the text can't refer "
                      "to it.", md, ast_line(node, anc), f"{GUIDE}#4-figures-and-tables")
            caption = next((c for c in node.get("children") or [] if c.get("type") == "caption"), None)
            if caption and CAPTION_NUMBER.match(text_of(caption, skip={"captionNumber"})):
                a.add("error", "caption-number", f"The caption starts with its own number. MyST "
                      f"numbers {kind}s itself, so this would print as 'Figure 1: Figure 1: …'.",
                      md, ast_line(caption, anc + (node,)), f"{GUIDE}#4-figures-and-tables")
        elif t == "crossReference":
            refs.add(node.get("identifier"))
        elif t == "cite":
            cites.append((node, anc))
        elif t == "abbreviation":
            used_abbr.add(text_of(node))
        elif t == "heading":
            text = text_of(node)
            if NUMBERED_HEADING.match(text):
                a.add("error", "numbered-heading", f"'{text}' is numbered by hand. Remove the "
                      "number; the PDF numbers headings itself, so it would print twice.", md,
                      ast_line(node, anc), f"{GUIDE}#7-verification")
        elif t == "text" and not any(x.get("type") in SKIP_INSIDE for x in anc):
            value = node.get("value", "")
            for m in HARD_CODED_REF.finditer(value):
                a.add("error", "hard-coded-ref", f"'{m.group(0)}' is typed as text. Use a "
                      f"cross-reference such as @Figure_1 so the number stays right. (Referring to "
                      "a figure in another paper? Write it in lower case.)", md,
                      ast_line(node, anc), f"{GUIDE}#5-cross-references")
            for m in TYPED_CITATION.finditer(value):
                a.add("error", "typed-citation", f"'{m.group(0)}' looks like a citation typed as "
                      f"text, so it won't link to the reference list. {suggest_key(a, m.group(0))}",
                      md, ast_line(node, anc), f"{GUIDE}#6-citations")
            for entry in a.bib:
                if len(entry["key"]) > 5 and entry["key"] in value:
                    a.add("error", "bare-key", f"The bibliography key '{entry['key']}' is typed as "
                          f"text. Write [@{entry['key']}] to cite it.", md,
                          ast_line(node, anc), f"{GUIDE}#6-citations")

    for ident, (node, anc) in labels.items():
        if ident not in refs:
            a.add("error", "unreferenced", f"{node['kind'].capitalize()} '{node.get('label', ident)}' "
                  "is never mentioned in the text. Refer to it, e.g. (@"
                  f"{node.get('label', ident)}), or ask the author whether it belongs.", md,
                  ast_line(node, anc), f"{GUIDE}#5-cross-references")

    check_citations(a, cites)

    defined = a.project.get("abbreviations")
    if isinstance(defined, dict):
        for key in defined:
            if key not in used_abbr and not re.search(rf"\b{re.escape(str(key))}\b", a.md_text):
                a.add("warning", "unused-abbreviation", f"The abbreviation '{key}' is defined but "
                      "never used.", a.myst_path, a.myst_line(rf"^\s*{re.escape(str(key))}:"),
                      f"{AUTHOR_GUIDE}#abbreviations")


def suggest_key(a: Article, typed: str) -> str:
    """Name the bibliography entry a typed citation probably means."""
    names = re.search(r"\(?(?:see |e\.g\.,? )?([A-Z][\w'’\-]+(?: [A-Z][\w'’\-]+)*)", typed)
    year = re.search(r"(?:19|20)\d{2}", typed)
    words = names.group(1).lower().split() if names else []
    matches = [e["key"] for e in a.bib if year and e["surname"] in words and e["year"] == year.group(0)]
    if len(matches) == 1:
        return f"The bibliography has it as '{matches[0]}': write [@{matches[0]}]."
    return "Replace it with the entry's key from the .bib file, e.g. [@smith_caffeine_2020]."


def check_corresponding(a: Article):
    """MyST treats a sole author with an email as corresponding, so read the built metadata."""
    authors = (a.ast or {}).get("frontmatter", {}).get("authors") if a.ast else a.project.get("authors")
    if isinstance(authors, list) and authors and not any(
            isinstance(x, dict) and x.get("corresponding") for x in authors):
        a.add("error", "corresponding", "No author is the corresponding author. Add "
              "'corresponding: true' and an email to the author readers should contact. (MyST "
              "picks the first author with an email if none is marked, so this means no author "
              "has one.)", a.myst_path,
              a.myst_line(r"^\s*authors:"))


def check_citations(a: Article, cites):
    md = a.md_path
    bib_keys = {e["key"] for e in a.bib}
    bib_dois = {e["doi"]: e["key"] for e in a.bib if e["doi"]}
    cited = set()

    for node, anc in cites:
        identifier = str(node.get("identifier") or "")
        doi = normalise_doi(identifier) if re.match(r"(https?://(dx\.)?doi\.org/|10\.)", identifier) else None
        ident = identifier if doi else str(node.get("label") or identifier)
        line = ast_line(node, anc)
        cited.add(ident)
        if doi and doi in bib_dois:
            a.add("error", "doi-duplicate", f"This cites the DOI {ident}, which is also in the "
                  f"bibliography as '{bib_dois[doi]}', so it would be listed twice. Use "
                  f"[@{bib_dois[doi]}].", md, line, f"{GUIDE}#6-citations")
            cited.add(bib_dois[doi])
        elif not doi and ident not in bib_keys and re.match(r"(?i)(fig(ure)?|tab(le)?)[_-]?\d", ident):
            a.add("error", "missing-target", f"@{ident} refers to a figure or table, but none has "
                  f":name: {ident}. Check the spelling, or which figure it should be.", md, line,
                  f"{GUIDE}#5-cross-references")
        elif not doi and ident not in bib_keys:
            a.add("error", "missing-reference", f"'{ident}' is cited but isn't in the bibliography. "
                  "Ask the author for the reference rather than guessing.", md, line,
                  f"{GUIDE}#6-citations")

        # (@key): the author's own brackets round a narrative citation.
        if node.get("kind") == "narrative" and anc:
            in_group = anc[-1].get("type") == "citeGroup"
            target, holder = (anc[-1], anc[-2]) if in_group and len(anc) > 1 else (node, anc[-1])
            items = holder.get("children") or []
            i = next((k for k, s in enumerate(items) if s is target), None)
            if i is not None and 0 < i < len(items) - 1:
                before, after = items[i - 1], items[i + 1]
                if (before.get("type") == "text" and before.get("value", "").rstrip().endswith("(")
                        and after.get("type") == "text" and after.get("value", "").lstrip().startswith(")")):
                    a.add("error", "bracketed-narrative", f"(@{ident}) renders with doubled "
                          f"brackets. Write [@{ident}] instead.", md, line, f"{GUIDE}#6-citations")

    seen = {}
    for e in a.bib:
        if "<" in e["key"]:
            a.add("error", "bib-key", f"The key '{e['key']}' contains '<', which silently drops the "
                  "citation. Rename the key here and wherever it's cited.", a.bib_path, e["line"],
                  f"{GUIDE}#6-citations")
        twin = next((seen[i] for i in e["ids"] if i in seen), None)
        if twin:
            a.add("error", "bib-duplicate", f"'{e['key']}' is the same work as '{twin}' (same DOI, "
                  "PubMed ID or URL), so it would be listed twice. Keep one entry and cite it "
                  "everywhere.", a.bib_path, e["line"], f"{GUIDE}#6-citations")
        for i in e["ids"]:
            seen.setdefault(i, e["key"])
        if e["key"] not in cited:
            a.add("warning", "uncited", f"'{e['key']}' is in the bibliography but never cited, so "
                  "it won't appear in the reference list. Cite it or delete it.", a.bib_path,
                  e["line"], f"{AUTHOR_GUIDE}#two-rules-that-catch-almost-everything")


def check_keyword_clashes(articles: list[Article], all_folders: list[Path]):
    """The venue checks keyword uniqueness across the collection."""
    owners: dict[str, set[str]] = {}
    for folder in all_folders:
        try:
            project = (yaml.safe_load((folder / "myst.yml").read_text(encoding="utf-8")) or {})
            keywords = (project.get("project") or {}).get("keywords") or []
        except (OSError, yaml.YAMLError):
            continue
        for k in keywords:
            owners.setdefault(str(k).strip().lower(), set()).add(folder.name)
    for a in articles:
        for k in a.project.get("keywords") or []:
            others = owners.get(str(k).strip().lower(), set()) - {a.folder.name}
            if others:
                a.add("warning", "keyword-clash", f"The keyword '{k}' is also used by "
                      f"{', '.join(sorted(others))}. Curvenote checks that keywords are unique "
                      "across the volume.", a.myst_path, a.myst_line(rf"^\s*-\s*['\"]?{re.escape(str(k))}"))


# --- running and reporting -----------------------------------------------------------------

def article_folders(root: Path) -> list[Path]:
    return sorted(p.parent for section in ("papers", "essays") for p in root.glob(f"{section}/*/myst.yml")
                  if p.parent.name != "_template")


def changed_folders(root: Path, base: str) -> list[Path]:
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=root,
                         capture_output=True, text=True, check=True).stdout.split()
    if any(SHARED.match(path) for path in out):
        return article_folders(root)
    folders = {root / Path(*Path(p).parts[:2]) for p in out
               if Path(p).parts[:1] in (("papers",), ("essays",)) and len(Path(p).parts) > 2}
    return sorted(f for f in folders if (f / "myst.yml").exists() and f.name != "_template")


def check(folder: Path, root: Path, affiliations, volume_abbr, skip_build=False) -> Article:
    a = Article(folder, root)
    check_metadata(a, affiliations, volume_abbr)
    used = check_source(a)
    check_images(a, used)
    if not skip_build and build(a):
        check_ast(a)
    check_corresponding(a)
    add_build_warnings(a)
    return a


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def guide_url(guide: str | None) -> str | None:
    if not guide:
        return None
    repo = os.environ.get("GITHUB_REPOSITORY")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    return f"{server}/{repo}/blob/main/{guide}" if repo else guide


def print_console(articles: list[Article], root: Path):
    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    for a in articles:
        errors = [x for x in a.findings if x.severity == "error"]
        warnings = [x for x in a.findings if x.severity == "warning"]
        print(f"\n{a.rel}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for x in sorted(a.findings, key=lambda x: (x.severity != "error", rel(x.file, root), x.line or 0)):
            where = rel(x.file, root) + (f":{x.line}" if x.line else "")
            print(f"  {x.severity.upper():7} {where}  [{x.rule}] {x.message}")
            if annotate:
                level = "error" if x.severity == "error" else "warning"
                msg = x.message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
                line = f",line={x.line}" if x.line else ""
                print(f"::{level} file={rel(x.file, root)}{line},title={x.rule}::{msg}")


def write_report(articles: list[Article], root: Path, path: Path):
    total = sum(1 for a in articles for x in a.findings if x.severity == "error")
    out = ["<!-- manuscript-check -->", "## Manuscript check", ""]
    if not total:
        out.append(f"✅ No errors in {len(articles)} article(s).")
    else:
        out.append(f"❌ {total} error(s) to fix before this can merge. Each one links to the part "
                   "of the guide that explains the fix.")
    for a in articles:
        if not a.findings:
            continue
        out += ["", f"### `{a.rel}`", "", "| | Where | Problem |", "|---|---|---|"]
        for x in sorted(a.findings, key=lambda x: (x.severity != "error", rel(x.file, root), x.line or 0)):
            icon = "❌" if x.severity == "error" else "⚠️"
            where = rel(x.file, root).removeprefix(str(a.rel) + "/") + (f":{x.line}" if x.line else "")
            msg = x.message.replace("\n", "<br>").replace("|", "\\|")
            url = guide_url(x.guide)
            out.append(f"| {icon} | `{where}` | {msg}" + (f" [How to fix]({url})" if url else "") + " |")
    out += ["", "<sub>❌ errors fail the check · ⚠️ warnings are worth a look but don't block. "
            "Rerun by pushing a fix.</sub>"]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folders", nargs="*", type=Path, help="article folders (default: all)")
    parser.add_argument("--changed-since", metavar="REF", help="check only articles changed since REF")
    parser.add_argument("--root", type=Path, default=ROOT, help="the volume repository")
    parser.add_argument("--report", type=Path, help="also write a Markdown report here")
    parser.add_argument("--no-build", action="store_true", help="skip the MyST build and AST checks")
    args = parser.parse_args()

    root = args.root.resolve()
    if args.folders:
        folders = [f.resolve() for f in args.folders]
    elif args.changed_since:
        folders = changed_folders(root, args.changed_since)
    else:
        folders = article_folders(root)
    if not folders:
        print("No articles to check.")
        if args.report:
            args.report.write_text("<!-- manuscript-check -->\n## Manuscript check\n\n"
                                   "No articles changed in this pull request.\n", encoding="utf-8")
        return 0

    affiliations, volume_abbr = volume_info(root)
    articles = [check(f, root, affiliations, volume_abbr, args.no_build) for f in folders]
    check_keyword_clashes(articles, article_folders(root))
    print_console(articles, root)
    if args.report:
        write_report(articles, root, args.report)
    errors = sum(1 for a in articles for x in a.findings if x.severity == "error")
    print(f"\n{errors} error(s) in {len(articles)} article(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
