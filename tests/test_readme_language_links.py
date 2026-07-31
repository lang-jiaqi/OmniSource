from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


class ReadmeLanguageLinksTests(unittest.TestCase):
    def test_default_english_readme_points_to_current_official_site(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/", text)
        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/report.html", text)
        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/entrepreneur.html", text)
        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/tools.html", text)
        self.assertNotIn("https://lang-jiaqi.github.io/omnisource-site/en/", text)

    def test_readmes_link_to_each_other(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn('href="README.zh-CN.md">中文</a>', english)
        self.assertIn('href="README.md">English</a>', chinese)

    def test_readme_translations_have_matching_structure(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        heading_pattern = re.compile(r"^(#+) ", re.MULTILINE)
        fence_pattern = re.compile(r"^(?:```|~~~)([^\n]*)$", re.MULTILINE)
        self.assertEqual(heading_pattern.findall(english), heading_pattern.findall(chinese))
        self.assertEqual(fence_pattern.findall(english), fence_pattern.findall(chinese))
        self.assertEqual(english.count("|---"), chinese.count("|---"))
        self.assertIsNone(CJK_RE.search(english.replace("中文", "")))

    def test_english_sample_reports_do_not_contain_chinese_body_text(self) -> None:
        for path in sorted((ROOT / "examples" / "reports" / "en").glob("*.md")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(CJK_RE.search(text))
                self.assertIn("Why it matters", text)
                self.assertIn("Key idea", text)


if __name__ == "__main__":
    unittest.main()
