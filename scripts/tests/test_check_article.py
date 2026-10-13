"""Tests for scripts/check_article.py.

Builds a throwaway volume from this repository's real config, adds the two fixture articles,
and checks that the clean one passes and that every planted mistake in the broken one is
caught. Needs MyST, like the check itself:

    python -m unittest discover scripts/tests

The fixtures say YEAR wherever the volume year goes, so they carry over to the next volume
unchanged.
"""

import base64
import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"

spec = importlib.util.spec_from_file_location("check_article", ROOT / "scripts" / "check_article.py")
check_article = importlib.util.module_from_spec(spec)
sys.modules["check_article"] = check_article
spec.loader.exec_module(check_article)

# A 1x1 PNG, so the fixtures need no binary files.
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")

# Every rule the broken fixture plants a mistake for.
EXPECTED_BROKEN = {
    "folder-name", "placeholder", "id", "site", "date", "key-case", "title", "description",
    "keywords", "subject", "thumbnail", "affiliation", "orcid", "credit", "corresponding",
    "abbreviations", "error-rules", "abstract", "image-path", "table-image", "label", "h1",
    "author-information", "trailing-rule", "build", "unnamed", "caption-number", "unreferenced",
    "numbered-heading", "hard-coded-ref", "typed-citation", "bare-key", "bracketed-narrative",
    "missing-reference", "missing-target", "bib-key", "bib-duplicate", "uncited", "unused-image", "keyword-clash",
}


class CheckArticleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        config = next(ROOT.glob("morganton[0-9][0-9][0-9][0-9].yml"))
        year = re.search(r"\d{4}", config.name).group(0)
        shutil.copy(config, cls.tmp)
        for folder in ("frontmatter", "templates"):
            shutil.copytree(ROOT / folder, cls.tmp / folder)

        cls.articles = {}
        for fixture, folder in (("good", "good"), ("good", "practice-good"), ("broken", "Smith_Jones")):
            dest = cls.tmp / "papers" / folder
            shutil.copytree(FIXTURES / fixture, dest)
            for path in dest.iterdir():
                path.write_text(path.read_text(encoding="utf-8").replace("YEAR", year), encoding="utf-8")
            (dest / "images").mkdir()
            for name in ("fig1.png", "results-table.png", "unused.png") if fixture == "broken" else ("fig1.png",):
                (dest / "images" / name).write_bytes(PNG)

        affiliations, abbreviations = check_article.volume_info(cls.tmp)
        folders = check_article.article_folders(cls.tmp)
        for folder in folders:
            cls.articles[folder.name] = check_article.check(folder, cls.tmp, affiliations, abbreviations)
        check_article.check_keyword_clashes(list(cls.articles.values()), folders)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_good_article_has_no_errors(self):
        findings = self.articles["good"].findings
        errors = [f"{f.rule}: {f.message}" for f in findings if f.severity == "error"]
        self.assertEqual(errors, [])
        # The only warning: it shares keywords with the other fixtures, on purpose.
        self.assertEqual({f.rule for f in findings}, {"keyword-clash"})

    def test_practice_article_can_never_pass(self):
        # The clean article again, under a practice- folder: the guard is its only error.
        errors = {f.rule for f in self.articles["practice-good"].findings if f.severity == "error"}
        self.assertEqual(errors, {"practice"})

    def test_every_planted_mistake_is_caught(self):
        fired = {f.rule for f in self.articles["Smith_Jones"].findings}
        self.assertEqual(sorted(EXPECTED_BROKEN - fired), [], "rules that didn't fire")

    def test_typed_citation_names_the_key_when_it_can(self):
        a = self.articles["Smith_Jones"]
        a.bib = [e for e in a.bib if e["key"] == "smith_caffeine_2020"]
        self.assertIn("[@smith_caffeine_2020]", check_article.suggest_key(a, "(Smith and Lee, 2020)"))

    def test_orcid_check_digit(self):
        self.assertTrue(check_article.orcid_ok("0000-0002-1825-0097"))
        self.assertTrue(check_article.orcid_ok("0000-0002-9079-593X"))
        self.assertFalse(check_article.orcid_ok("0000-0002-1825-0098"))


if __name__ == "__main__":
    unittest.main()
