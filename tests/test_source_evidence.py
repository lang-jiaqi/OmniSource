from __future__ import annotations

import datetime as dt
import unittest

from omnisource.dedup import merge_by_id
from omnisource.agents import editor
from omnisource.models import Signal
from omnisource.source_evidence import (
    paper_source_signal_items,
    paper_source_signal_markdown,
    paper_source_signal_text,
    source_signal_markdown,
)


def make_signal(signal_id: str, typ: str, source: str, **kwargs) -> Signal:
    return Signal(
        id=signal_id,
        title=kwargs.get("title", "Useful Paper"),
        url=kwargs.get("url", f"https://example.com/{source}"),
        type=typ,
        published_at=dt.datetime(2026, 7, 6, tzinfo=dt.timezone.utc),
        summary=kwargs.get("summary", "A useful research paper."),
        authors=kwargs.get("authors", ["Ada Lovelace"]),
        sources=[source],
        popularity=kwargs.get("popularity", 0),
    )


class SourceEvidenceTests(unittest.TestCase):
    def test_merged_paper_keeps_hf_and_twitter_evidence(self) -> None:
        paper = make_signal("2607.00001", "paper", "arxiv")
        hf = make_signal("2607.00001", "paper", "hf_papers", popularity=22)
        tweet = make_signal(
            "2607.00001",
            "social",
            "twitter",
            url="https://x.com/biglab/status/1",
            authors=["@biglab"],
            popularity=700,
        )

        merged = merge_by_id([paper, hf, tweet])

        self.assertEqual(len(merged), 1)
        signal = merged[0]
        signal.followed = "Chelsea Finn"
        self.assertEqual(signal.sources, ["arxiv", "hf_papers", "twitter"])
        self.assertEqual(signal.popularity, 700)
        evidence = signal.extra["source_evidence"]
        self.assertTrue(any("arxiv" in item["sources"] for item in evidence))
        self.assertTrue(any("hf_papers" in item["sources"] for item in evidence))
        self.assertTrue(any("twitter" in item["sources"] for item in evidence))
        zh = paper_source_signal_text(signal, "中文")
        en = paper_source_signal_text(signal, "English")
        self.assertIn("论文作者名单命中 Chelsea Finn", zh)
        self.assertIn("arXiv 收录", zh)
        self.assertIn("Hugging Face Daily Papers（社区点赞 👍 22）", zh)
        self.assertIn("X/Twitter 提到 @biglab 👍 700", zh)
        self.assertIn("Paper author watchlist: Chelsea Finn", en)
        self.assertIn("arXiv indexed", en)
        self.assertIn("Hugging Face Daily Papers (community upvotes 👍 22)", en)
        self.assertIn("X/Twitter mentioned by @biglab 👍 700", en)
        items = paper_source_signal_items(signal, "English")
        urls = {item["source"]: item["url"] for item in items}
        self.assertEqual(urls["watchlist"], "")
        self.assertEqual(urls["arxiv"], "https://arxiv.org/abs/2607.00001")
        self.assertEqual(urls["hf_papers"], "https://huggingface.co/papers/2607.00001")
        self.assertEqual(urls["twitter"], "https://x.com/biglab/status/1")

    def test_source_signal_markdown_links_all_sources(self) -> None:
        paper = make_signal("2607.00001", "paper", "arxiv", url="https://arxiv.org/abs/2607.00001")
        hf = make_signal("2607.00001", "paper", "hf_papers", popularity=22)
        tweet = make_signal(
            "2607.00001",
            "social",
            "twitter",
            url="https://x.com/biglab/status/1",
            authors=["@biglab"],
            popularity=7,
        )
        blog = make_signal(
            "2607.00001",
            "blog",
            "rss",
            title="Lab note about Useful Paper",
            url="https://example.com/lab-note",
        )
        signal = merge_by_id([paper, hf, tweet, blog])[0]

        markdown = paper_source_signal_markdown(signal, "English")

        self.assertIn("[arXiv indexed](https://arxiv.org/abs/2607.00001)", markdown)
        self.assertIn("[Hugging Face Daily Papers (community upvotes 👍 22)](https://huggingface.co/papers/2607.00001)", markdown)
        self.assertIn("[X/Twitter mentioned by @biglab 👍 7](https://x.com/biglab/status/1)", markdown)
        self.assertIn("[Blog: Lab note about Useful Paper](https://example.com/lab-note)", markdown)

    def test_single_source_items_still_show_source_signal(self) -> None:
        paper = make_signal("2607.00002", "paper", "arxiv", url="https://arxiv.org/abs/2607.00002")
        repo = make_signal("github:example/repo", "repo", "github", url="https://github.com/example/repo")
        blog = make_signal("https://example.com/post", "blog", "rss", url="https://example.com/post")

        self.assertEqual(paper_source_signal_text(paper, "中文"), "arXiv 收录")
        self.assertIn("[GitHub 新项目/搜索](https://github.com/example/repo)", source_signal_markdown(repo, "中文"))
        self.assertIn("[RSS/博客源](https://example.com/post)", source_signal_markdown(blog, "中文"))
        curated = make_signal(
            "https://example.com/curated", "blog", "blogrxiv", url="https://example.com/curated"
        )
        self.assertIn("[BlogrXiv 精选](https://example.com/curated)", source_signal_markdown(curated, "中文"))

    def test_markdown_report_renders_source_signal_under_paper(self) -> None:
        paper = make_signal("2607.00001", "paper", "arxiv")
        hf = make_signal("2607.00001", "paper", "hf_papers", popularity=22)
        tweet = make_signal(
            "2607.00001",
            "social",
            "twitter",
            url="https://x.com/biglab/status/1",
            authors=["@biglab"],
            popularity=7,
        )
        signal = merge_by_id([paper, hf, tweet])[0]
        signal.followed = "Chelsea Finn"
        signal.extra.setdefault("i18n", {})["zh"] = {
            "why_it_matters": "这条值得看。",
            "key_idea": "核心机制。",
            "method_brief": {
                "problem": "解决具体瓶颈。",
                "method": "用新的训练流程处理它。",
                "difference": "比常规方法更直接。",
                "evidence": "摘要给出了实验信号。",
            },
        }

        markdown = editor.render(
            {"paper": [signal]},
            {"name": "test", "output": {"language": "中文"}},
            "2026-07-06",
        )

        self.assertIn("**来源信号:**", markdown)
        self.assertIn("论文作者名单命中 Chelsea Finn", markdown)
        self.assertIn("[arXiv 收录]", markdown)
        self.assertIn("(https://arxiv.org/abs/2607.00001)", markdown)
        self.assertIn("[Hugging Face Daily Papers（社区点赞 👍 22）](https://huggingface.co/papers/2607.00001)", markdown)
        self.assertIn("[X/Twitter 提到 @biglab 👍 7](https://x.com/biglab/status/1)", markdown)
        self.assertIn("<summary>方法解读</summary>", markdown)
        self.assertIn("**问题:** 解决具体瓶颈。", markdown)
        self.assertIn("<summary>摘要</summary>", markdown)
        self.assertIn("核心机制。", markdown)
        self.assertNotIn("A useful research paper.", markdown)
        self.assertNotIn("**链接:**", markdown)
        self.assertNotIn("via arxiv, hf_papers", markdown)


if __name__ == "__main__":
    unittest.main()
