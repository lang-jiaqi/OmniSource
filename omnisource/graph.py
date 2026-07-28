"""Per-paper author collaboration data.

Builds author nodes and verified collaboration edges from enriched author data.
The site renderer turns this stable structure into its interactive SVG figure.
"""
from __future__ import annotations

import html
import re
from urllib.parse import quote

from .models import Signal

_COUNTRY_SUFFIX = re.compile(r"\s*\([^)]*\)\s*$")


def _short_inst(name: str) -> str:
    return _COUNTRY_SUFFIX.sub("", name).strip()


def _primary_inst(author: dict) -> str:
    insts = author.get("institutions") or []
    return _short_inst(insts[0]) if insts else ""


def _author_search_url(name: str) -> str:
    """Provide a useful click target when upstream metadata lacks a profile."""
    return "https://www.semanticscholar.org/search?q=" + quote(name, safe="")


def _author_tooltip(a: dict, code_url: str | None) -> tuple[str, str, str]:
    """Build the hover card (HTML) for an author node, plus the URL a click
    should open. Surfaces who/where + the reliable contact handles we have:
    homepage (Semantic Scholar), ORCID / OpenAlex profile, and the paper's repo.
    Email is intentionally absent — no API gives it reliably."""
    esc = html.escape
    lines = [f"<b>{esc(a.get('name', '?'))}</b>"]
    if a.get("institutions"):
        lines.append(esc(", ".join(_short_inst(x) for x in a["institutions"][:2])))
    cites, h = a.get("citations", 0), a.get("h_index", 0)
    stats = []
    if cites:
        stats.append(f"{cites} citations")
    if h:
        stats.append(f"h-index {h}")
    if stats:
        lines.append(" · ".join(stats))
    links = []
    if a.get("homepage"):
        links.append(f'<a href="{esc(a["homepage"])}">homepage</a>')
    if a.get("orcid"):
        links.append(f'<a href="{esc(a["orcid"])}">ORCID</a>')
    elif a.get("profile"):
        label = "Semantic Scholar" if "semanticscholar.org" in a["profile"] else "OpenAlex"
        links.append(f'<a href="{esc(a["profile"])}">{label}</a>')
    if code_url:
        links.append(f'<a href="{esc(code_url)}">code</a>')
    if links:
        lines.append(" · ".join(links))
    click = a.get("homepage") or a.get("orcid") or a.get("profile") or ""
    if click:
        return "<br>".join(lines), click, "profile"
    name = str(a.get("name") or "").strip()
    if name:
        lines.append("Academic profile not available; click to search")
        return "<br>".join(lines), _author_search_url(name), "search"
    return "<br>".join(lines), "", ""


def _author_metric(author: dict) -> tuple[bool, str | None, int | None, int]:
    """Return the best available author metric and a safe drawing value.

    ``value`` is deliberately kept separate from the metric metadata: the
    graph needs a non-zero radius even for an unenriched author, but that
    fallback must never be presented as a citation count in the UI.
    """
    for metric_type in ("citations", "h_index", "works"):
        if metric_type not in author or author.get(metric_type) is None:
            continue
        try:
            metric_value = int(author[metric_type])
        except (TypeError, ValueError):
            continue
        return True, metric_type, metric_value, max(metric_value, 1)
    return False, None, None, 1


def build_paper_graph(signal: Signal, max_authors: int = 12, min_collab: int = 1) -> dict:
    """Return author collaboration data for the report renderer.
    Author nodes carry `value` (citations) for size and a hover tooltip. Large
    author lists are capped to the most-cited, so cards don't get crowded."""
    nodes = []
    edges = []

    authors = signal.author_nodes or [{"name": n, "institutions": []} for n in signal.authors]
    if len(authors) > max_authors:
        authors = sorted(authors, key=lambda a: a.get("citations", 0), reverse=True)[:max_authors]

    institutions = []
    for author in authors:
        primary_inst = _primary_inst(author)
        if primary_inst and primary_inst not in institutions:
            institutions.append(primary_inst)
    inst_index = {name: i for i, name in enumerate(institutions)}

    node_id = {}  # OpenAlex author id -> graph node id
    for i, a in enumerate(authors):
        aid = f"a{i}"
        if a.get("id"):
            node_id[a["id"]] = aid
        has_metric, metric_type, metric_value, drawing_value = _author_metric(a)
        tip, click, click_kind = _author_tooltip(a, signal.code_url)
        # Institution is available in the hover card rather than inline. This
        # keeps the graph readable while colors still encode shared affiliation.
        label = a.get("name", "?")
        primary_inst = _primary_inst(a)
        index = inst_index.get(primary_inst)
        node = {"id": aid, "label": label, "group": "author",
                "value": drawing_value, "has_metric": has_metric,
                "metric_type": metric_type, "metric_value": metric_value,
                "title": tip, "url": click, "url_kind": click_kind}
        if primary_inst:
            node.update({
                "institution": primary_inst,
                "institution_index": index,
            })
        nodes.append(node)

    # Keep every verified author pair rather than just each author's strongest
    # collaborator. OpenAlex returns the count from either endpoint, so retain
    # the larger count if the two histograms differ while data is refreshing.
    pair_counts: dict[tuple[str, str], int] = {}
    for a in authors:
        author_id = a.get("id")
        if not author_id:
            continue
        for oid, raw_count in (a.get("collabs") or {}).items():
            if oid not in node_id or oid == author_id:
                continue
            try:
                count = int(raw_count)
            except (TypeError, ValueError):
                continue
            if count < min_collab:
                continue
            pair = tuple(sorted((author_id, oid)))
            pair_counts[pair] = max(pair_counts.get(pair, 0), count)

    for (author_id, collaborator_id), count in sorted(
        pair_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        edges.append({"from": node_id[author_id], "to": node_id[collaborator_id],
                      "kind": "collab",
                      "color": {"color": "#7c83ff", "highlight": "#9aa0ff"},
                      "width": min(7, 1.5 + count / 2),
                      "count": count,
                      "title": f"{count} shared publications"})

    # OpenAlex collaboration histograms are not always available for new or
    # recently indexed authors. Keep those authors in the same visual network
    # without overstating their history: a thin dashed edge only means they
    # jointly authored *this* paper, while solid edges above retain verified
    # historical publication counts.
    author_ids = [str(node["id"]) for node in nodes]
    if len(author_ids) > 1:
        adjacency = {author_id: set() for author_id in author_ids}
        for edge in edges:
            adjacency[edge["from"]].add(edge["to"])
            adjacency[edge["to"]].add(edge["from"])

        components: list[list[str]] = []
        unseen = set(author_ids)
        while unseen:
            start = unseen.pop()
            component = [start]
            stack = [start]
            while stack:
                current = stack.pop()
                for neighbour in adjacency[current]:
                    if neighbour in unseen:
                        unseen.remove(neighbour)
                        component.append(neighbour)
                        stack.append(neighbour)
            components.append(component)

        nodes_by_id = {str(node["id"]): node for node in nodes}
        anchor = max(author_ids, key=lambda author_id: int(nodes_by_id[author_id].get("value") or 0))
        anchor_component = next(component for component in components if anchor in component)
        for component in components:
            if component is anchor_component:
                continue
            representative = max(
                component,
                key=lambda author_id: int(nodes_by_id[author_id].get("value") or 0),
            )
            edges.append({
                "from": anchor,
                "to": representative,
                "kind": "coauthor",
                "color": {"color": "#9a83ff", "highlight": "#c5b7ff"},
                "width": 1.35,
                "count": 1,
                "evidence": "current_paper",
                "title": "Co-authors on this paper",
            })
    return {"nodes": nodes, "edges": edges}
