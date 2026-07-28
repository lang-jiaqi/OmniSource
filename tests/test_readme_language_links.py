from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


class ReadmeLanguageLinksTests(unittest.TestCase):
    def test_english_readme_points_to_english_demo_and_samples(self) -> None:
        text = (ROOT / "README.en.md").read_text(encoding="utf-8")

        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/en/", text)
        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/en/report.html", text)
        self.assertIn("https://lang-jiaqi.github.io/omnisource-site/en/tools.html", text)
        self.assertIn("examples/reports/en/llm-agents.md", text)
        self.assertIn("examples/reports/en/ai-safety.md", text)
        self.assertNotIn("https://lang-jiaqi.github.io/omnisource-site/report.html", text)
        self.assertNotIn("https://lang-jiaqi.github.io/omnisource-site/tools.html", text)
        self.assertNotIn("examples/reports/llm-agents.md)", text)

    def test_english_sample_reports_do_not_contain_chinese_body_text(self) -> None:
        for path in sorted((ROOT / "examples" / "reports" / "en").glob("*.md")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(CJK_RE.search(text))
                self.assertIn("Why it matters", text)
                self.assertIn("Key idea", text)


if __name__ == "__main__":
    unittest.main()
