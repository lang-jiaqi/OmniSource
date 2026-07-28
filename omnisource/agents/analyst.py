"""Analyst agent: ask an LLM why each signal merits a reader's attention."""
from __future__ import annotations

from .. import i18n
from ..entrepreneur_taxonomy import classify_entrepreneur_signal, is_entrepreneur_track
from ..llm.base import LLMProvider
from ..models import Signal
from ..prompt_feedback import feedback_prompt_clause
from ..topic_taxonomy import flatten_topics, match_topic

OTHER_TOPIC = "other"

SYSTEM_TEMPLATE = (
    'You are a research-intelligence analyst for the track "{name}": {description}\n'
    "Judge how relevant a paper is to THIS track — be strict: shared vocabulary but "
    "really about something else scores low — then write one short reading note for "
    "a busy researcher.\n"
    "\n"
    "why_it_matters = the so-what for a {name} researcher: what it unlocks, changes, or "
    "beats versus the usual approach, and for whom. Include concrete technical context "
    "or evidence when the text provides it; never just restate the title.\n"
    "If the item is a paper, also write method_brief: four concise fields that help "
    "a reader decide whether to open the PDF: problem, method, difference, evidence. "
    "Each field must be one short sentence grounded in the abstract and must not repeat "
    "why_it_matters.\n"
    "\n"
    "Voice: concrete, active, plain language. Ground every claim in the given text; if a "
    "result isn't stated, say what's claimed — don't invent numbers. Banned hype words: "
    "novel framework, revolutionary, state-of-the-art, we propose, paradigm, cutting-edge.\n"
    "\n"
    "{example}\n"
    "IMPORTANT: write why_it_matters ENTIRELY in {language} — every word, no "
    "other language mixed in. Respond with JSON only, keys:\n"
    "- relevance: number 0..1 (1 = squarely in this track, 0 = unrelated)\n"
    "- novelty: number 0..1 (1 = a genuinely new idea/result, 0 = incremental or a rehash)\n"
    "- why_it_matters: one sentence ({language}) — why this deserves attention now\n"
    "- method_brief: object with keys problem, method, difference, evidence ({language}; paper items only)\n"
    "- abstract: a faithful one-to-three-sentence rendering of the supplied abstract "
    "({language}; paper items only)\n"
    '- read_priority: "high" | "medium" | "low"'
    "{topic_clause}"
)

BILINGUAL_SYSTEM_TEMPLATE = (
    'You are a research-intelligence analyst for the track "{name}": {description}\n'
    "Judge how relevant a paper is to THIS track — be strict: shared vocabulary but "
    "really about something else scores low — then write one short reading note for "
    "a busy researcher in BOTH Chinese and English.\n"
    "\n"
    "why_it_matters = the so-what for a {name} researcher: what it unlocks, changes, or "
    "beats versus the usual approach, and for whom. Include concrete technical context "
    "or evidence when the text provides it; never just restate the title.\n"
    "If the item is a paper, also write method_brief: four concise fields that help "
    "a reader decide whether to open the PDF: problem, method, difference, evidence. "
    "Each field must be one short sentence grounded in the abstract and must not repeat "
    "why_it_matters.\n"
    "\n"
    "Voice: concrete, active, plain language. Ground every claim in the given text; if a "
    "result isn't stated, say what's claimed — don't invent numbers. Banned hype words: "
    "novel framework, revolutionary, state-of-the-art, we propose, paradigm, cutting-edge.\n"
    "\n"
    "Respond with JSON only, keys:\n"
    "- relevance: number 0..1 (1 = squarely in this track, 0 = unrelated)\n"
    "- novelty: number 0..1 (1 = a genuinely new idea/result, 0 = incremental or a rehash)\n"
    '- read_priority: "high" | "medium" | "low"\n'
    '- i18n: {{"zh": {{"why_it_matters": "...", '
    '"abstract": "...", '
    '"method_brief": {{"problem": "...", "method": "...", "difference": "...", "evidence": "..."}}}}, '
    '"en": {{"why_it_matters": "...", '
    '"method_brief": {{"problem": "...", "method": "...", "difference": "...", "evidence": "..."}}}}}}\n'
    "For paper items, zh.abstract must be a faithful one-to-three-sentence Chinese rendering "
    "of the supplied abstract. The zh strings must be entirely Chinese. The en strings must be "
    "entirely English."
    "{topic_clause}"
)

# One worked example per output language keeps the reading note concrete and
# avoids a generic "important because" response.
EXAMPLES = {
    "en": (
        "Example (yours must be in your output language):\n"
        'why_it_matters: "Tiles attention into on-chip SRAM blocks, letting you train '
        'longer-context Transformers on the same GPU, '
        '2–4× faster and exact rather than approximate — so it became a default kernel, '
        'not a speed/accuracy tradeoff."'
    ),
    "zh": (
        "范例(你的输出仍用规定语言):\n"
        'why_it_matters:"它把注意力按块放进片上 SRAM 计算,让同一张 GPU 上能训更长上下文的 Transformer,快 2–4 倍且是'
        '精确解而非近似——于是它成了默认算子,而不再是速度与精度的取舍。"'
    ),
}

USER_TEMPLATE = "Item type: {typ}\nTitle: {title}\n\nAbstract or description: {summary}"


def _topic_clause(topic_leaves: list[str]) -> str:
    if not topic_leaves:
        return ""
    options = "; ".join(topic_leaves)
    return (
        f'\n- topic: choose exactly ONE taxonomy leaf path, verbatim: [{options}]. '
        "A path is ordered broad > middle > narrow. "
        f'If none fit, use "{OTHER_TOPIC}".'
    )


class Analyst:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.successes = 0
        self.failures = 0

    def analyze(self, signal: Signal, track: dict) -> bool:
        """Enrich one signal in place. Failures leave the signal untouched."""
        topic_leaves = flatten_topics(track.get("topics"))
        output = track.get("output", {})
        languages = i18n.output_languages(output)
        lang = languages[0]
        if len(languages) > 1:
            system = BILINGUAL_SYSTEM_TEMPLATE.format(
                name=track["name"],
                description=track.get("description", ""),
                topic_clause=_topic_clause(topic_leaves),
            )
        else:
            system = SYSTEM_TEMPLATE.format(
                name=track["name"],
                description=track.get("description", ""),
                language=i18n.strings(lang)["llm_name"],
                example=EXAMPLES[i18n.norm_lang(lang)],
                topic_clause=_topic_clause(topic_leaves),
            )
        system += feedback_prompt_clause()
        user = USER_TEMPLATE.format(typ=signal.type, title=signal.title, summary=signal.summary)
        try:
            data = self.provider.complete_json(system, user)
        except Exception as exc:
            self.failures += 1
            print(f"    ! analyst failed for {signal.id}: {exc}")
            return False
        self.successes += 1
        try:
            signal.llm_relevance = float(data.get("relevance"))
        except (TypeError, ValueError):
            signal.llm_relevance = None
        try:
            signal.novelty = float(data.get("novelty"))
        except (TypeError, ValueError):
            signal.novelty = None
        localized = _localized_i18n(data, lang, include_method=signal.type == "paper")
        if localized:
            signal.extra.setdefault("i18n", {}).update(localized)
        primary = _localized_for(signal, lang)
        signal.why_it_matters = primary.get("why_it_matters") or data.get("why_it_matters")
        signal.read_priority = data.get("read_priority")
        if is_entrepreneur_track(track):
            # The startup taxonomy is deliberately deterministic so it stays
            # available when the entrepreneur track has no LLM configured.
            signal.topic = classify_entrepreneur_signal(signal).topic
        elif topic_leaves:
            # Map the LLM's answer back onto the taxonomy; fall back to "other".
            signal.topic = match_topic(data.get("topic"), topic_leaves) or OTHER_TOPIC
        return True


METHOD_BRIEF_KEYS = ("problem", "method", "difference", "evidence")


def _clean_method_brief(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result = {key: str(value.get(key) or "").strip() for key in METHOD_BRIEF_KEYS}
    return result if any(result.values()) else {}


def _localized_i18n(data: dict, fallback_language: str, *, include_method: bool = False) -> dict[str, dict]:
    raw = data.get("i18n")
    if not isinstance(raw, dict):
        fallback = {
            "why_it_matters": data.get("why_it_matters"),
        }
        if include_method and data.get("abstract"):
            fallback["abstract"] = str(data["abstract"]).strip()
        if include_method:
            method_brief = _clean_method_brief(data.get("method_brief"))
            if method_brief:
                fallback["method_brief"] = method_brief
        return {i18n.norm_lang(fallback_language): fallback} if any(fallback.values()) else {}
    result: dict[str, dict] = {}
    for lang, value in raw.items():
        norm = i18n.norm_lang(str(lang))
        if not isinstance(value, dict):
            continue
        text = {
            "why_it_matters": str(value.get("why_it_matters") or "").strip(),
        }
        abstract = str(value.get("abstract") or value.get("summary") or "").strip()
        if abstract:
            text["abstract"] = abstract
        if include_method:
            method_brief = _clean_method_brief(value.get("method_brief"))
            if method_brief:
                text["method_brief"] = method_brief
        if any(text.values()):
            result[norm] = text
    return result


def _localized_for(signal: Signal, language: str) -> dict[str, str]:
    raw = signal.extra.get("i18n") if isinstance(signal.extra, dict) else None
    if not isinstance(raw, dict):
        return {}
    value = raw.get(i18n.norm_lang(language))
    return value if isinstance(value, dict) else {}
