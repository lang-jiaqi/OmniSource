from __future__ import annotations

import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omnisource.distiller.audit import AuditAgent
from omnisource.distiller.canonicalize import dedup_candidates
from omnisource.distiller.fulltext import FullTextSignalExtractor, PDFFullTextFetcher
from omnisource.distiller.hub import HubAgent
from omnisource.distiller.models import (
    ExpertReview,
    PaperCandidate,
    ReviewScores,
    SupplementalScores,
)
from omnisource.distiller.pipeline import enrich_candidates, load_candidates_jsonl, run_distiller
from omnisource.distiller.selection import ExpertSelector
from omnisource.distiller.skills import load_skill_library
from omnisource.distiller.sources import CSLongHorizonArxivSource
from omnisource.distiller.taxonomy import load_taxonomy
from omnisource.distiller.venue_registry import load_venue_registry


class DistillerTaxonomyTests(unittest.TestCase):
    def test_builtin_taxonomy_has_three_level_leaves_and_matching_skills(self) -> None:
        taxonomy = load_taxonomy("cs-foundation-v1")
        skills = load_skill_library(taxonomy)

        self.assertEqual(taxonomy.version, "cs-foundation-v1")
        self.assertGreaterEqual(len(taxonomy.leaves), 30)
        for leaf in taxonomy.leaves.values():
            self.assertEqual(len(leaf.path), 3)
            self.assertIn(leaf.leaf_id, skills)
            self.assertIn("专家", skills[leaf.leaf_id].prompt)
            self.assertTrue(leaf.arxiv_categories or leaf.venue_ids)

    def test_expert_selector_returns_three_small_two_adjacent_one_far_reviewers(self) -> None:
        taxonomy = load_taxonomy("cs-foundation-v1")
        reviewers = ExpertSelector(taxonomy).select(
            "ai.rl_planning_agents",
            canonical_paper_id="arxiv:2501.12345",
            harness_version="test-harness",
        )

        self.assertEqual(len(reviewers), 6)
        self.assertEqual(
            [r.lens for r in reviewers[:3]],
            ["method_reviewer", "evidence_reviewer", "reproducibility_reviewer"],
        )
        self.assertTrue(all(r.leaf_id == "ai.rl_planning_agents" for r in reviewers[:3]))
        self.assertTrue(all(r.relationship == "adjacent_big_peer" for r in reviewers[3:5]))
        self.assertEqual(reviewers[5].relationship, "random_big_peer")
        self.assertNotIn(reviewers[5].leaf_id, {"ai.rl_planning_agents", *taxonomy.leaf("ai.rl_planning_agents").adjacent})

    def test_venue_registry_maps_top_conferences_to_taxonomy_leaves(self) -> None:
        registry = load_venue_registry()

        ml_names = registry.names_for_leaf("ai.ml_foundations")
        systems_names = registry.names_for_leaf("systems.networking")

        self.assertIn("NeurIPS", ml_names)
        self.assertIn("SIGCOMM", systems_names)


class DistillerDecisionTests(unittest.TestCase):
    def _candidate(self, paper_id: str, year: int, leaf: str = "ai.nlp_speech") -> PaperCandidate:
        return PaperCandidate(
            paper_id=paper_id,
            title="Attention Is All You Need",
            abstract="A transformer sequence transduction model with attention mechanisms.",
            authors=["A. Researcher"],
            published_at=dt.datetime(year, 6, 1, tzinfo=dt.timezone.utc),
            primary_leaf=leaf,
            arxiv_id="1706.03762" if "1706.03762" in paper_id else None,
        )

    def _reviews(self, score: float, *, must_keep: int = 0, red_flags: list[str] | None = None) -> list[ExpertReview]:
        reviews = []
        for i in range(6):
            reviews.append(
                ExpertReview(
                    reviewer_id=f"reviewer-{i}",
                    skill_leaf="ai.nlp_speech",
                    lens="method_reviewer",
                    relationship="small_peer",
                    scores=ReviewScores(
                        novelty=score,
                        workload=score,
                        open_source_completeness=score,
                        insight_contribution=score,
                        paper_presentation=score,
                    ),
                    confidence=0.8,
                    rationale="calibrated test review",
                    red_flags=red_flags or [],
                    must_keep_signal=i < must_keep,
                )
            )
        return reviews

    def test_classic_paper_is_kept_even_when_age_adjusted_score_is_low(self) -> None:
        decision = HubAgent(current_year=2026).decide(
            self._candidate("arxiv:1706.03762", 2017),
            self._reviews(0.42),
            SupplementalScores(citation=0.1, hf_upvote=0.0, github_star=0.0),
        )

        self.assertEqual(decision.decision, "keep")
        self.assertEqual(decision.decision_reason, "classic_override")
        self.assertIn("classic", decision.audit_trail)

    def test_old_non_classic_borderline_paper_is_filtered_by_age_weight(self) -> None:
        decision = HubAgent(current_year=2026).decide(
            self._candidate("arxiv:1401.00001", 2014, leaf="systems.networking"),
            self._reviews(0.72),
            SupplementalScores(citation=0.2, hf_upvote=None, github_star=None),
        )

        self.assertEqual(decision.decision, "filter")
        self.assertEqual(decision.decision_reason, "below_threshold")
        self.assertLess(decision.age_adjusted_score, decision.keep_threshold)

    def test_reviewer_dispersion_triggers_human_review(self) -> None:
        reviews = self._reviews(0.9)
        reviews[0].scores.novelty = 0.1
        decision = HubAgent(current_year=2026).decide(
            self._candidate("arxiv:2501.00002", 2025),
            reviews,
            SupplementalScores(citation=0.1, hf_upvote=0.0, github_star=0.0),
        )

        self.assertEqual(decision.decision, "human_review")
        self.assertEqual(decision.decision_reason, "reviewer_dispersion")


class DistillerPipelineTests(unittest.TestCase):
    def test_full_text_signals_reward_clear_figures_tables_and_formulae(self) -> None:
        signals = FullTextSignalExtractor().from_text(
            "Abstract\nWe propose a method.\n"
            "Figure 1 shows the architecture. Table 2 reports ablations.\n"
            "Equation: L = sum_i log p(y_i | x_i).\n"
            "Experiments compare against strong baselines and discuss limitations."
        )

        self.assertGreaterEqual(signals.figure_count, 1)
        self.assertGreaterEqual(signals.table_count, 1)
        self.assertGreaterEqual(signals.formula_count, 1)
        self.assertGreater(signals.presentation_bonus, 0.0)

    def test_canonicalization_deduplicates_arxiv_versions(self) -> None:
        first = PaperCandidate(
            paper_id="arxiv:2601.12345v1",
            title="A Useful Agent Benchmark",
            abstract="benchmark",
            authors=["A"],
            published_at=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
            arxiv_id="2601.12345v1",
            primary_leaf="ai.rl_planning_agents",
        )
        second = PaperCandidate(
            paper_id="arxiv:2601.12345v2",
            title="A Useful Agent Benchmark",
            abstract="benchmark extended",
            authors=["A"],
            published_at=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc),
            arxiv_id="2601.12345v2",
            primary_leaf="ai.rl_planning_agents",
            github_url="https://github.com/example/benchmark",
        )

        merged = dedup_candidates([first, second])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].canonical_id, "arxiv:2601.12345")
        self.assertEqual(merged[0].github_url, "https://github.com/example/benchmark")

    def test_canonicalization_merges_conference_doi_with_arxiv_preprint(self) -> None:
        preprint = PaperCandidate(
            paper_id="arxiv:2501.99999",
            title="A Shared Paper Title",
            abstract="long arxiv abstract",
            authors=["A. Author", "B. Builder"],
            published_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            arxiv_id="2501.99999",
            primary_leaf="ai.ml_foundations",
            pdf_url="https://arxiv.org/pdf/2501.99999",
        )
        conference = PaperCandidate(
            paper_id="10.1145/example",
            title="A Shared Paper Title",
            abstract="conference abstract",
            authors=["A. Author", "B. Builder"],
            published_at=dt.datetime(2025, 6, 1, tzinfo=dt.timezone.utc),
            doi="10.1145/example",
            venue="ICML",
            primary_leaf="ai.ml_foundations",
        )

        merged = dedup_candidates([preprint, conference])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].doi, "10.1145/example")
        self.assertEqual(merged[0].arxiv_id, "2501.99999")
        self.assertEqual(merged[0].venue, "ICML")
        self.assertEqual(merged[0].pdf_url, "https://arxiv.org/pdf/2501.99999")

    def test_non_arxiv_external_ids_fall_back_to_title_canonical_id(self) -> None:
        candidate = PaperCandidate(
            paper_id="https://openalex.org/W123",
            title="A Venue Paper Without DOI",
            abstract="metadata only",
            authors=["A"],
            published_at=dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc),
            primary_leaf="systems.databases",
        )

        self.assertEqual(candidate.canonical_id, "title:a venue paper without doi:2024")

    def test_arxiv_source_builds_one_query_per_year_for_long_horizon(self) -> None:
        leaf = load_taxonomy().leaf("ai.nlp_speech")

        queries = CSLongHorizonArxivSource().build_year_queries(leaf, start_year=2012, end_year=2026)

        self.assertEqual(len(queries), 15)
        self.assertIn("cat:cs.CL", queries[0])
        self.assertIn("submittedDate:[201201010000 TO 201212312359]", queries[0])
        self.assertIn("submittedDate:[202601010000 TO 202612312359]", queries[-1])

    def test_metadata_enrichment_invokes_citation_hf_and_code_sources(self) -> None:
        candidate = PaperCandidate(
            paper_id="arxiv:2601.00001",
            title="A New Paper",
            abstract="abstract",
            authors=["A"],
            published_at=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
            arxiv_id="2601.00001",
            primary_leaf="ai.ml_foundations",
        )

        class Citation:
            def enrich(self, item):
                item.field_year_normalized_citation = 0.7
                return item

        class HF:
            def enrich_many(self, items):
                items[0].normalized_hf_upvote = 0.6
                return items

        class Code:
            def enrich(self, item):
                item.normalized_github_star = 0.5
                return item

        enriched = enrich_candidates([candidate], Citation(), HF(), Code())

        self.assertEqual(enriched[0].field_year_normalized_citation, 0.7)
        self.assertEqual(enriched[0].normalized_hf_upvote, 0.6)
        self.assertEqual(enriched[0].normalized_github_star, 0.5)

    def test_jsonl_loader_preserves_decision_critical_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.jsonl"
            path.write_text(
                '{"paper_id":"arxiv:2601.00002","title":"Risky Paper","abstract":"x","authors":["A"],'
                '"published_at":"2026-01-01T00:00:00+00:00","primary_leaf":"security.ai_security",'
                '"secondary_leaves":["ai.deep_learning_foundation_models"],"arxiv_id":"2601.00002",'
                '"is_withdrawn":true,"is_retracted":true,"self_citation_ratio":0.8,'
                '"survey_anchor_count":4,"benchmark_years_active":6,"contribution_type":"benchmark"}\n',
                encoding="utf-8",
            )

            loaded = load_candidates_jsonl(path)[0]

        self.assertTrue(loaded.is_withdrawn)
        self.assertTrue(loaded.is_retracted)
        self.assertEqual(loaded.self_citation_ratio, 0.8)
        self.assertEqual(loaded.survey_anchor_count, 4)
        self.assertEqual(loaded.benchmark_years_active, 6)
        self.assertEqual(loaded.secondary_leaves, ["ai.deep_learning_foundation_models"])
        self.assertEqual(loaded.contribution_type, "benchmark")

    def test_pdf_fetcher_reports_missing_parser_before_silent_fallback(self) -> None:
        def missing_reader():
            raise ModuleNotFoundError("pypdf")

        with self.assertRaises(RuntimeError):
            PDFFullTextFetcher(reader_loader=missing_reader).require_pdf_parser()

    def test_dry_run_pipeline_writes_summary_decisions_and_reviewer_traces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_distiller(dry_run=True, years=15, max_candidates=3, output_dir=Path(tmp), current_year=2026)

            self.assertTrue(result.summary_path.exists())
            self.assertTrue(result.decisions_path.exists())
            self.assertTrue(result.reviewer_traces_path.exists())
            self.assertGreaterEqual(len(result.decisions), 1)
            self.assertEqual(result.review_count, len(result.decisions) * 6)
            self.assertEqual(AuditAgent().validate_decision(result.decisions[0]), [])

    def test_live_pipeline_path_uses_venue_adapter_without_stale_variable_name(self) -> None:
        candidate = PaperCandidate(
            paper_id="arxiv:2601.00003",
            title="A Live Path Paper",
            abstract="foundation model with experiments and code",
            authors=["A"],
            published_at=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
            arxiv_id="2601.00003",
            primary_leaf="ai.deep_learning_foundation_models",
        )

        class FakeArxivSource:
            def fetch(self, leaves, years, max_per_leaf_per_year):
                return [candidate]

        class FakeVenueSource:
            def fetch(self, venue_names, leaf_id, years, per_venue):
                self.last_per_venue = per_venue
                return []

        with tempfile.TemporaryDirectory() as tmp:
            with patch("omnisource.distiller.pipeline.CSLongHorizonArxivSource", return_value=FakeArxivSource()):
                with patch("omnisource.distiller.pipeline.VenueProceedingsSource", return_value=FakeVenueSource()):
                    result = run_distiller(
                        dry_run=False,
                        max_candidates=1,
                        output_dir=Path(tmp),
                        current_year=2026,
                        enrich_metadata=False,
                        include_venues=True,
                    )

        self.assertEqual(len(result.decisions), 1)


if __name__ == "__main__":
    unittest.main()
