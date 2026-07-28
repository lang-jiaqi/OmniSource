from __future__ import annotations

import datetime as dt
import json
import unittest
from unittest.mock import patch

from omnisource.agents.review_distill import _institution_reputation
from omnisource.enrich import (
    _infer_pdf_institutions,
    enrich_arxiv_pdf_affiliations,
    enrich_semantic_scholar,
)
from omnisource.graph import build_paper_graph
from omnisource.models import Signal


def make_paper() -> Signal:
    return Signal(
        id="paper",
        title="Institution-aware graph paper",
        url="https://example.com/paper",
        type="paper",
        published_at=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
        summary="A paper with multiple institutions.",
        sources=["test"],
    )


class InstitutionSignalTests(unittest.TestCase):
    def test_graph_colors_authors_by_primary_institution_without_extra_institution_nodes(self) -> None:
        paper = make_paper()
        paper.author_nodes = [
            {"id": "oa1", "name": "Ada", "institutions": ["University of California, Berkeley"], "citations": 10},
            {"id": "oa2", "name": "Grace", "institutions": ["Massachusetts Institute of Technology"], "citations": 20},
            {"id": "oa3", "name": "Alan", "institutions": ["University of California, Berkeley"], "citations": 30},
        ]

        graph = build_paper_graph(paper)

        authors = {node["label"].split("\n", 1)[0]: node for node in graph["nodes"] if node["group"] == "author"}
        self.assertEqual(authors["Ada"]["label"], "Ada")
        self.assertEqual(authors["Ada"]["institution_index"], authors["Alan"]["institution_index"])
        self.assertNotEqual(authors["Ada"]["institution_index"], authors["Grace"]["institution_index"])
        self.assertEqual(authors["Ada"]["value"], 10)
        self.assertEqual(authors["Grace"]["value"], 20)
        self.assertTrue(authors["Ada"]["has_metric"])
        self.assertEqual(authors["Ada"]["metric_type"], "citations")
        self.assertEqual(authors["Ada"]["metric_value"], 10)
        self.assertFalse(any(node["group"] == "institution" for node in graph["nodes"]))
        self.assertFalse(any(node["group"] == "paper" for node in graph["nodes"]))
        self.assertFalse(any(edge.get("kind") == "author_institution" for edge in graph["edges"]))

    def test_graph_keeps_each_verified_author_collaboration_pair(self) -> None:
        paper = make_paper()
        paper.author_nodes = [
            {"id": "oa1", "name": "Ada", "collabs": {"oa2": 8, "oa3": 4}},
            {"id": "oa2", "name": "Grace", "collabs": {"oa1": 7, "oa3": 1}},
            {"id": "oa3", "name": "Alan", "collabs": {"oa1": 4, "oa2": 1}},
        ]

        graph = build_paper_graph(paper)

        edges = {(edge["from"], edge["to"]): edge for edge in graph["edges"]}
        self.assertEqual(len(edges), 3)
        self.assertEqual(sorted(edge["count"] for edge in edges.values()), [1, 4, 8])
        self.assertTrue(all(edge["kind"] == "collab" for edge in edges.values()))
        self.assertGreater(
            max(edge["width"] for edge in edges.values()),
            min(edge["width"] for edge in edges.values()),
        )

    def test_graph_connects_unenriched_coauthors_without_claiming_history(self) -> None:
        paper = make_paper()
        paper.author_nodes = [
            {"name": "Ada", "citations": 30},
            {"name": "Grace", "citations": 20},
            {"name": "Alan", "citations": 10},
        ]

        graph = build_paper_graph(paper)

        self.assertEqual(len(graph["edges"]), 2)
        self.assertTrue(all(edge["kind"] == "coauthor" for edge in graph["edges"]))
        self.assertTrue(all(edge["evidence"] == "current_paper" for edge in graph["edges"]))
        self.assertTrue(all(edge["width"] < 2 for edge in graph["edges"]))

    def test_graph_can_size_authors_from_h_index_when_citations_are_missing(self) -> None:
        paper = make_paper()
        paper.author_nodes = [
            {"id": "s2:1", "name": "Ada", "institutions": ["University of California, Berkeley"], "h_index": 8},
            {"id": "s2:2", "name": "Grace", "institutions": ["Massachusetts Institute of Technology"], "h_index": 13},
        ]

        graph = build_paper_graph(paper)

        authors = {node["label"].split("\n", 1)[0]: node for node in graph["nodes"] if node["group"] == "author"}
        self.assertEqual(authors["Ada"]["value"], 8)
        self.assertEqual(authors["Grace"]["value"], 13)
        self.assertTrue(authors["Ada"]["has_metric"])
        self.assertEqual(authors["Ada"]["metric_type"], "h_index")
        self.assertEqual(authors["Ada"]["metric_value"], 8)

    def test_graph_does_not_turn_missing_metrics_into_citations(self) -> None:
        paper = make_paper()
        paper.author_nodes = [{"name": "Ada Lovelace", "institutions": []}]

        graph = build_paper_graph(paper)
        author = next(node for node in graph["nodes"] if node["group"] == "author")

        self.assertEqual(author["value"], 1)
        self.assertFalse(author["has_metric"])
        self.assertIsNone(author["metric_type"])
        self.assertIsNone(author["metric_value"])

    def test_graph_provides_scholarly_search_when_author_profile_is_unavailable(self) -> None:
        paper = make_paper()
        paper.author_nodes = [
            {"name": "Ada Lovelace", "institutions": []},
        ]

        graph = build_paper_graph(paper)
        author = next(node for node in graph["nodes"] if node["group"] == "author")

        self.assertEqual(author["url_kind"], "search")
        self.assertIn("semanticscholar.org/search", author["url"])
        self.assertIn("Ada%20Lovelace", author["url"])

    def test_semantic_scholar_can_seed_author_nodes_without_openalex(self) -> None:
        paper = make_paper()
        paper.url = "https://arxiv.org/abs/2606.29215"
        body = json.dumps({
            "authors": [
                {
                    "authorId": "1",
                    "name": "Ada",
                    "affiliations": ["University of California, Berkeley"],
                    "homepage": "ada.example",
                    "hIndex": 8,
                },
                {
                    "authorId": "2",
                    "name": "Grace",
                    "affiliations": ["Massachusetts Institute of Technology"],
                    "homepage": None,
                    "hIndex": 13,
                },
            ]
        })

        with patch("omnisource.enrich.cached_get", return_value=body):
            enrich_semantic_scholar(paper)

        self.assertEqual(paper.author_nodes[0]["id"], "s2:1")
        self.assertEqual(paper.author_nodes[0]["profile"], "https://www.semanticscholar.org/author/1")
        self.assertEqual(paper.author_nodes[0]["homepage"], "https://ada.example")
        self.assertEqual(paper.author_nodes[0]["institutions"], ["University of California, Berkeley"])
        self.assertEqual(paper.author_nodes[1]["profile"], "https://www.semanticscholar.org/author/2")
        self.assertEqual(paper.author_nodes[1]["h_index"], 13)
        self.assertIn("Massachusetts Institute of Technology", paper.affiliations)

        graph = build_paper_graph(paper)
        authors = {node["label"].split("\n", 1)[0]: node for node in graph["nodes"] if node["group"] == "author"}
        self.assertEqual(authors["Ada"]["url"], "https://ada.example")
        self.assertEqual(authors["Grace"]["url"], "https://www.semanticscholar.org/author/2")
        self.assertIn("Semantic Scholar", authors["Grace"]["title"])

    def test_arxiv_pdf_affiliation_fallback_assigns_single_institution_to_missing_authors(self) -> None:
        paper = make_paper()
        paper.url = "https://arxiv.org/abs/2606.29215"
        paper.author_nodes = [
            {"name": "Ada Lovelace", "institutions": []},
            {"name": "Grace Hopper", "institutions": []},
        ]
        first_page = """A Useful Paper
Ada Lovelace, Grace Hopper
Massachusetts Institute of Technology
Abstract
We study useful things.
"""

        with (
            patch("omnisource.enrich._cached_get_bytes", return_value=b"%PDF"),
            patch("omnisource.enrich._extract_pdf_first_page_text", return_value=first_page),
        ):
            assigned = enrich_arxiv_pdf_affiliations(paper)

        self.assertEqual(assigned, 2)
        self.assertEqual(paper.author_nodes[0]["institutions"], ["Massachusetts Institute of Technology"])
        self.assertEqual(paper.author_nodes[1]["institutions"], ["Massachusetts Institute of Technology"])
        self.assertIn("Massachusetts Institute of Technology", paper.affiliations)

    def test_arxiv_pdf_affiliation_fallback_uses_markers_when_available(self) -> None:
        paper = make_paper()
        paper.url = "https://arxiv.org/abs/2606.29215"
        paper.author_nodes = [
            {"name": "Ada Lovelace", "institutions": []},
            {"name": "Grace Hopper", "institutions": []},
        ]
        first_page = """A Useful Paper
Ada Lovelace 1, Grace Hopper 2
1 University of California, Berkeley
2 Massachusetts Institute of Technology
Abstract
We study useful things.
"""

        with (
            patch("omnisource.enrich._cached_get_bytes", return_value=b"%PDF"),
            patch("omnisource.enrich._extract_pdf_first_page_text", return_value=first_page),
        ):
            assigned = enrich_arxiv_pdf_affiliations(paper)

        self.assertEqual(assigned, 2)
        self.assertEqual(paper.author_nodes[0]["institutions"], ["University of California, Berkeley"])
        self.assertEqual(paper.author_nodes[1]["institutions"], ["Massachusetts Institute of Technology"])

    def test_pdf_institution_parser_splits_inline_numbered_institutions(self) -> None:
        institutions, marker_map = _infer_pdf_institutions(
            """A Useful Paper
Ada Lovelace 1, Grace Hopper 2, Alan Turing 3
1Shanghai Jiao Tong University, 2Xi'an Jiao Tong University, 3Huawei
Abstract
We study useful things.
"""
        )

        self.assertEqual(institutions, [
            "Shanghai Jiao Tong University",
            "Xi'an Jiao Tong University",
            "Huawei",
        ])
        self.assertEqual(marker_map["1"], "Shanghai Jiao Tong University")
        self.assertEqual(marker_map["2"], "Xi'an Jiao Tong University")
        self.assertEqual(marker_map["3"], "Huawei")

    def test_arxiv_pdf_affiliation_fallback_fills_only_missing_institutions(self) -> None:
        paper = make_paper()
        paper.url = "https://arxiv.org/abs/2606.29215"
        paper.author_nodes = [
            {"name": "Ada Lovelace", "institutions": ["University of California, Berkeley"]},
            {"name": "Grace Hopper", "institutions": []},
        ]
        first_page = """A Useful Paper
Ada Lovelace, Grace Hopper
Massachusetts Institute of Technology
Abstract
We study useful things.
"""

        with (
            patch("omnisource.enrich._cached_get_bytes", return_value=b"%PDF"),
            patch("omnisource.enrich._extract_pdf_first_page_text", return_value=first_page),
        ):
            assigned = enrich_arxiv_pdf_affiliations(paper)

        self.assertEqual(assigned, 1)
        self.assertEqual(paper.author_nodes[0]["institutions"], ["University of California, Berkeley"])
        self.assertEqual(paper.author_nodes[1]["institutions"], ["Massachusetts Institute of Technology"])

    def test_institution_reputation_is_a_weak_positive_prior_for_known_research_institutions(self) -> None:
        elite = make_paper()
        elite.author_nodes = [{"name": "Ada", "institutions": ["University of California, Berkeley"]}]

        unknown = make_paper()
        unknown.author_nodes = [{"name": "Builder", "institutions": ["Small Regional College"]}]

        self.assertGreater(_institution_reputation(elite), 0.9)
        self.assertEqual(_institution_reputation(unknown), 0.0)


if __name__ == "__main__":
    unittest.main()
