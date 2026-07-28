from __future__ import annotations

import unittest

from omnisource.agents.analyst import BILINGUAL_SYSTEM_TEMPLATE, _localized_i18n


class AnalystLocalizationTests(unittest.TestCase):
    def test_bilingual_analysis_preserves_translated_abstract(self) -> None:
        result = _localized_i18n(
            {
                "i18n": {
                    "zh": {
                        "why_it_matters": "值得关注。",
                        "abstract": "这是一段忠实的中文摘要。",
                    }
                }
            },
            "中文",
            include_method=True,
        )

        self.assertEqual(result["zh"]["abstract"], "这是一段忠实的中文摘要。")

    def test_bilingual_prompt_requests_a_chinese_abstract(self) -> None:
        self.assertIn('"abstract": "..."', BILINGUAL_SYSTEM_TEMPLATE)
        self.assertIn("zh.abstract", BILINGUAL_SYSTEM_TEMPLATE)

