"""Track-level topic taxonomy helpers.

Daily tracks can keep the old flat `topics: [a, b, c]` shape, or use a small
tree with `name` + `children`. The LLM still returns one string: the full leaf
path, e.g. "Systems > Inference > KV cache".
"""
from __future__ import annotations

TOPIC_SEP = " > "


def normalize_topic_path(value: object) -> str:
    parts = [part.strip() for part in str(value or "").split(">")]
    return TOPIC_SEP.join(part for part in parts if part)


def flatten_topics(topics: object) -> list[str]:
    leaves: list[str] = []

    def add(path: list[str]) -> None:
        clean = [part.strip() for part in path if str(part).strip()]
        if clean:
            leaf = TOPIC_SEP.join(clean)
            if leaf not in leaves:
                leaves.append(leaf)

    def walk(node: object, path: list[str]) -> None:
        if isinstance(node, str):
            add([*path, node])
            return
        if isinstance(node, list):
            for child in node:
                walk(child, path)
            return
        if not isinstance(node, dict):
            return

        name = str(node.get("name") or node.get("label") or node.get("topic") or "").strip()
        children = (
            node.get("children")
            or node.get("subtopics")
            or node.get("topics")
            or node.get("leaves")
        )
        if children:
            next_path = [*path, name] if name else path
            walk(children, next_path)
            return
        if name:
            add([*path, name])
            return

        # Also accept the compact YAML shape:
        # topics:
        #   - Systems:
        #       - Inference
        if len(node) == 1:
            key, value = next(iter(node.items()))
            walk(value, [*path, str(key)])

    walk(topics or [], [])
    return leaves


def match_topic(raw: object, leaves: list[str]) -> str | None:
    normalized = normalize_topic_path(raw)
    if not normalized:
        return None
    by_lower = {normalize_topic_path(leaf).lower(): leaf for leaf in leaves}
    return by_lower.get(normalized.lower())
