from __future__ import annotations

import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from omnisource.agents.quality import distill_quality
from omnisource.models import Signal


def make_signal(
    signal_id: str,
    *,
    title: str = "Agent planning benchmark",
    summary: str = "A benchmark for agent planning with strong experiments.",
    typ: str = "paper",
    popularity: int = 0,
    keyword_hits: int = 1,
    code_url: str | None = None,
) -> Signal:
    signal = Signal(
        id=signal_id,
        title=title,
        url=f"https://example.com/{signal_id}",
        type=typ,
        published_at=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
        summary=summary,
        sources=["test"],
        popularity=popularity,
        code_url=code_url,
    )
    signal.keyword_hits = keyword_hits
    return signal


class QualityDistillTests(unittest.TestCase):
    def test_official_quantity_guard_widens_windows_until_minimum_is_met(self) -> None:
        from omnisource import main as main_module

        first = make_signal("paper-1")
        second = make_signal("paper-2")
        track = {
            "name": "test",
            "days": 3,
            "collection": {"retry_factors": [2], "max_days": 30},
            "minimum_output": {"paper": 2},
            "output": {"top_papers": 2},
        }

        with patch.object(main_module, "Collector") as collector_cls:
            collector_cls.return_value.collect.side_effect = [[first], [first, second]]
            with patch.object(main_module.curator, "rank", side_effect=lambda items, _track: items):
                with patch.object(main_module.quality, "distill_quality", side_effect=lambda items, _track: items):
                    signals, _watchlist, _ranked, distilled = main_module._collect_and_shortlist(
                        track, "test", None
                    )

        self.assertEqual(len(signals), 2)
        self.assertEqual(len(distilled), 2)
        calls = collector_cls.return_value.collect.call_args_list
        self.assertEqual([call.args[0]["days"] for call in calls], [3, 6])

    def test_quality_distill_scores_and_filters_weak_items(self) -> None:
        track = {
            "keywords": ["agent", "planning", "benchmark"],
            "output": {"top_papers": 2},
            "quality_distill": {"min_score": 0.35, "buffer": 2},
        }
        strong = make_signal(
            "strong",
            popularity=50,
            keyword_hits=3,
            code_url="https://github.com/example/agent-benchmark",
        )
        weak = make_signal("weak", title="Sparse note", summary="", keyword_hits=0)

        distilled = distill_quality([weak, strong], track)

        self.assertEqual([signal.id for signal in distilled], ["strong"])
        self.assertIsNotNone(strong.quality_score)
        self.assertIsNotNone(weak.quality_score)
        self.assertGreater(strong.quality_score or 0.0, weak.quality_score or 0.0)

    def test_quality_distill_keeps_section_buffer_per_type(self) -> None:
        track = {
            "keywords": ["agent"],
            "output": {"top_papers": 2},
            "quality_distill": {"min_score": 0.0, "buffer": 1},
        }
        signals = [
            make_signal("paper-1", popularity=500, keyword_hits=2),
            make_signal("paper-2", popularity=100, keyword_hits=2),
            make_signal("paper-3", popularity=10, keyword_hits=1),
            make_signal("paper-4", popularity=0, keyword_hits=1),
        ]

        distilled = distill_quality(signals, track)

        self.assertEqual([signal.id for signal in distilled], ["paper-1", "paper-2", "paper-3"])

    def test_quality_distill_treats_scalar_config_as_defaults(self) -> None:
        signal = make_signal("paper", keyword_hits=1)

        distilled = distill_quality([signal], {"keywords": ["agent"], "quality_distill": True})

        self.assertEqual(distilled, [signal])
        self.assertIsNotNone(signal.quality_score)

    def test_quality_distill_can_fill_section_quota_below_threshold(self) -> None:
        track = {
            "keywords": ["infra"],
            "output": {"top_blogs": 2},
            "quality_distill": {
                "min_score": 0.99,
                "buffer": 0,
                "fill_quota_types": ["blog"],
            },
        }
        blogs = [
            make_signal("blog-1", typ="blog", title="Infra note", summary="", keyword_hits=1),
            make_signal("blog-2", typ="blog", title="Systems note", summary="", keyword_hits=0),
            make_signal("blog-3", typ="blog", title="Third note", summary="", keyword_hits=0),
        ]

        distilled = distill_quality(blogs, track)

        self.assertEqual([signal.id for signal in distilled], ["blog-1", "blog-2"])
        self.assertTrue(all((signal.quality_score or 0.0) < 0.99 for signal in distilled))

    def test_run_pipeline_passes_quality_distilled_signals_to_section_selection(self) -> None:
        from omnisource import main as main_module

        ranked = [make_signal("ranked")]
        distilled = [make_signal("distilled")]

        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            select_sections = Mock(return_value=({"paper": distilled}, {"paper": distilled}))
            with patch.object(main_module, "REPORTS_DIR", reports_dir):
                with patch.object(main_module, "load_dotenv"):
                    with patch.object(main_module, "load_track", return_value={"name": "test", "output": {"top_papers": 1}}):
                        with patch.object(main_module, "Collector") as collector_cls:
                            collector_cls.return_value.collect.return_value = ranked
                            with patch.object(main_module.curator, "rank", return_value=ranked):
                                with patch.object(main_module.quality, "distill_quality", return_value=distilled):
                                    with patch.object(main_module.curator, "make_analyst", return_value=None):
                                        with patch.object(main_module.curator, "select_sections_with_candidates", select_sections):
                                            with patch.object(main_module.editor, "render", return_value="# report"):
                                                with patch.object(main_module, "build_publishers", return_value=[]):
                                                    main_module.run_pipeline("test", no_memory=True)

        select_sections.assert_called_once()
        self.assertIs(select_sections.call_args.args[0], distilled)

    def test_run_pipeline_days_override_updates_loaded_track(self) -> None:
        from omnisource import main as main_module

        ranked = [make_signal("ranked")]
        track = {"name": "test", "days": 3, "output": {"top_papers": 1}}

        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            with patch.object(main_module, "REPORTS_DIR", reports_dir):
                with patch.object(main_module, "load_dotenv"):
                    with patch.object(main_module, "load_track", return_value=track):
                        with patch.object(main_module, "Collector") as collector_cls:
                            collector_cls.return_value.collect.return_value = ranked
                            with patch.object(main_module.curator, "rank", return_value=ranked):
                                with patch.object(main_module.quality, "distill_quality", return_value=ranked):
                                    with patch.object(main_module.curator, "make_analyst", return_value=None):
                                        with patch.object(
                                            main_module.curator,
                                            "select_sections_with_candidates",
                                            return_value=({"paper": ranked}, {"paper": ranked}),
                                        ):
                                            with patch.object(main_module.editor, "render", return_value="# report"):
                                                with patch.object(main_module, "build_publishers", return_value=[]):
                                                    main_module.run_pipeline("test", no_memory=True, days=7)

        used_track = collector_cls.return_value.collect.call_args.args[0]
        self.assertEqual(used_track["days"], 7)
        self.assertEqual(track["days"], 3)

    def test_empty_collection_does_not_publish_a_blank_report(self) -> None:
        from omnisource import main as main_module

        with patch.object(main_module, "load_dotenv"):
            with patch.object(main_module, "load_track", return_value={"name": "test", "output": {}}):
                with patch.object(main_module, "Collector") as collector_cls:
                    collector_cls.return_value.collect.return_value = []
                    with patch.object(main_module, "build_publishers") as publishers:
                        with self.assertRaisesRegex(RuntimeError, "Existing reports were left untouched"):
                            main_module.run_pipeline("test", no_memory=True)

        publishers.assert_not_called()

    def test_weekly_memory_is_separate_from_daily_memory(self) -> None:
        from omnisource import main as main_module
        from omnisource.memory.store import SignalStore

        signal = make_signal("weekly-paper")
        track = {
            "name": "test",
            "weekly_days": 7,
            "output": {"top_papers": 1},
            "enrich_openalex": False,
            "review_distill": False,
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(main_module, "REPORTS_DIR", root / "reports"):
                with patch.object(main_module, "DB_PATH", root / "memory.db"):
                    with patch.object(main_module, "load_dotenv"):
                        with patch.object(main_module, "load_track", return_value=track):
                            with patch.object(main_module, "Collector") as collector_cls:
                                collector_cls.return_value.collect.return_value = [signal]
                                with patch.object(main_module.curator, "rank", return_value=[signal]):
                                    with patch.object(main_module.quality, "distill_quality", return_value=[signal]):
                                        with patch.object(main_module.curator, "make_analyst", return_value=None):
                                            with patch.object(
                                                main_module.curator,
                                                "select_sections_with_candidates",
                                                return_value=({"paper": [signal]}, {"paper": [signal]}),
                                            ):
                                                with patch.object(main_module, "build_publishers", return_value=[]):
                                                    main_module.run_pipeline("test", weekly=True)

            store = SignalStore(root / "memory.db")
            self.assertIn("weekly-paper", store.seen_ids("test::weekly"))
            self.assertNotIn("weekly-paper", store.seen_ids("test"))
            store.close()


if __name__ == "__main__":
    unittest.main()
