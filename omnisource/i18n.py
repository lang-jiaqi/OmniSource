"""Report localization helpers."""
from __future__ import annotations

_ZH = {"zh", "zh-cn", "zh_cn", "中文", "chinese", "cn"}

STRINGS = {
    "en": {
        "paper": "📄 Papers",
        "repo": "💻 Repositories",
        "blog": "📝 Lab Notes",
        "social": "💬 Community Signals",
        "watchlist": "🔔 Paper author watchlist",
        "topic_dist": "This week's topics",
        "why": "Why it matters",
        "abstract": "Abstract",
        "method_brief": "Method brief",
        "method_brief_show": "Show method brief",
        "method_brief_hide": "Hide method brief",
        "method_problem": "Problem",
        "method_method": "Method",
        "method_difference": "Difference",
        "method_evidence": "Evidence",
        "authors": "Authors",
        "link": "Link",
        "code": "Code",
        "category": "Category",
        "topic_area": "Area",
        "topic_focus": "Topic",
        "signals": "signals",
        "source_signal": "Source signals",
        "sources": "sources",
        "llm_name": "English",
        "potential": "Potential",
        "review": "Expert review",
        "dim_novelty": "novelty",
        "dim_insight_contribution": "insight",
        "dim_open_source_completeness": "open-source",
        "dim_paper_presentation": "presentation",
        "dim_institution_signal": "institution",
        "dim_momentum": "momentum",
        "dim_maturity": "maturity",
        "dim_relevance": "relevance",
        "dim_adoption": "adoption",
        "dim_substance": "substance",
        "dim_authority": "authority",
        "dim_freshness": "freshness",
        "graph_paper": "paper",
        "graph_author": "author",
        "graph_collab": "collab",
        "graph_same_inst": "same color = same institution; missing = author color",
        "language": "Language",
        "read_in": "Read in English",
        "track_picker": "Choose a track to view its papers, community signals, lab notes, and repositories",
        "hero_copy": "AI-Driven Open Research Community",
        "report_hero_title": "Today's research,\nproperly prioritized.",
        "report_hero_copy": "Cross-source signals, ranked into a reading flow for the work ahead.",
        "priority_stream": "Priority stream",
        "section_papers": "Papers",
        "section_blogs": "Lab signals",
        "section_repos": "Open source",
        "section_social": "Community",
        "graph_show": "Show collaboration network",
        "graph_hide": "Hide collaboration network",
        "graph_authors": "authors",
        "graph_institutions": "institutions",
        "graph_links": "links",
        "favorite": "Save",
        "favorite_add": "Save this item",
        "favorite_remove": "Remove from saved items",
        "home": "Home",
        "reports": "Reports",
        "theme": "Theme",
        "theme_dark": "Dark theme",
        "theme_light": "Light theme",
        "settings": "Settings",
        "tools": "Tools",
        "feedback_up": "Worth recommending",
        "feedback_down": "Not a fit",
        "feedback": "Recommendation feedback",
        "feedback_export": "Export feedback events",
        "feedback_copied": "Feedback copied",
        "feedback_reason_up_title": "Why is this worth recommending?",
        "feedback_reason_down_title": "Why is this not a fit?",
        "feedback_reason_up_help": "Describe the content-quality signal OmniSource should learn from.",
        "feedback_reason_down_help": "Tell OmniSource what made this irrelevant, stale, shallow, or misranked.",
        "feedback_reason_placeholder": "e.g. Strong systems paper with real deployment evidence, not just another benchmark.",
        "feedback_reason_save": "Save feedback",
        "feedback_reason_sync": "Save and sync to my fork",
        "feedback_reason_cancel": "Cancel",
        "feedback_reason_required": "Add a short reason so OmniSource can learn your preference.",
        "feedback_repository_prompt": "Enter your fork as owner/repository. Feedback will open as a GitHub Issue for your confirmation.",
        "feedback_repository_invalid": "Use the GitHub owner/repository format, for example alice/OmniSource.",
        "personalization": "Personalize",
        "feedback_action": "Action",
        "feedback_action_like": "👍 Like",
        "feedback_action_ignore": "🚫 Ignore",
        "feedback_action_lower_similar": "⬇️ Show fewer like this",
        "feedback_action_follow_author": "🔔 Follow author",
        "feedback_follow_author": "🔔 Follow {author}",
        "feedback_open": "🎯 Like / ignore / show fewer / follow author",
        "feedback_select_one": "Select exactly one action by changing its checkbox to `[x]`.",
        "feedback_confirm_help": "Submit this Issue to apply the preference to future reports. The hidden metadata below is read only from Issues created by the repository owner.",
        "future_title": "Voice blog — coming later",
        "future_copy": "Audio briefings are planned for a future release.",
    },
    "zh": {
        "paper": "📄 论文",
        "repo": "💻 开源项目",
        "blog": "📝 实验室动态",
        "social": "💬 社区动态",
        "watchlist": "🔔 论文作者名单",
        "topic_dist": "本周主题分布",
        "why": "为什么值得看",
        "abstract": "摘要",
        "method_brief": "方法解读",
        "method_brief_show": "显示方法解读",
        "method_brief_hide": "隐藏方法解读",
        "method_problem": "问题",
        "method_method": "方法",
        "method_difference": "差异",
        "method_evidence": "证据",
        "authors": "作者",
        "link": "链接",
        "code": "代码",
        "category": "分类",
        "topic_area": "方向",
        "topic_focus": "主题",
        "signals": "条",
        "source_signal": "来源信号",
        "sources": "来源",
        "llm_name": "中文",
        "potential": "潜力",
        "review": "专家评审",
        "dim_novelty": "新颖度",
        "dim_insight_contribution": "洞见",
        "dim_open_source_completeness": "开源度",
        "dim_paper_presentation": "呈现",
        "dim_institution_signal": "机构信号",
        "dim_momentum": "增长势头",
        "dim_maturity": "成熟度",
        "dim_relevance": "相关度",
        "dim_adoption": "采用度",
        "dim_substance": "实质",
        "dim_authority": "权威度",
        "dim_freshness": "新鲜度",
        "graph_paper": "论文",
        "graph_author": "作者",
        "graph_collab": "合作线",
        "graph_same_inst": "同色=同机构；缺失按作者着色",
        "language": "语言",
        "read_in": "阅读中文",
        "track_picker": "选择一个 track 查看对应的论文、社区动态、博客和开源项目",
        "hero_copy": "AI-Driven Open Research Community",
        "report_hero_title": "今日值得研读的\n研究信号",
        "report_hero_copy": "跨来源去重、筛选与排序，把真正相关的进展编排成当天的阅读流。",
        "priority_stream": "优先阅读流",
        "section_papers": "论文",
        "section_blogs": "实验室动态",
        "section_repos": "开源项目",
        "section_social": "社区动态",
        "graph_show": "展开合作网络",
        "graph_hide": "收起合作网络",
        "graph_authors": "位作者",
        "graph_institutions": "所机构",
        "graph_links": "条合作线",
        "favorite": "收藏",
        "favorite_add": "收藏这条内容",
        "favorite_remove": "取消收藏",
        "home": "首页",
        "reports": "日报",
        "theme": "主题",
        "theme_dark": "暗色主题",
        "theme_light": "亮色主题",
        "settings": "设置",
        "tools": "工具雷达",
        "feedback_up": "值得推送",
        "feedback_down": "不该推送",
        "feedback": "推荐反馈",
        "feedback_export": "导出反馈事件",
        "feedback_copied": "反馈已复制",
        "feedback_reason_up_title": "为什么值得推送？",
        "feedback_reason_down_title": "为什么不适合推送？",
        "feedback_reason_up_help": "写下 OmniSource 应该学习的内容质量信号。",
        "feedback_reason_down_help": "告诉 OmniSource 它为什么不相关、过时、太浅，或排序不该这么高。",
        "feedback_reason_placeholder": "例如：是真正的系统论文，有部署证据，不只是普通 benchmark。",
        "feedback_reason_save": "保存反馈",
        "feedback_reason_sync": "保存并同步到我的 Fork",
        "feedback_reason_cancel": "取消",
        "feedback_reason_required": "请写一句原因，这才是 OmniSource 学习偏好的依据。",
        "feedback_repository_prompt": "请输入你的 Fork，格式为 owner/repository。随后会打开 GitHub Issue 供你确认提交。",
        "feedback_repository_invalid": "请使用 GitHub owner/repository 格式，例如 alice/OmniSource。",
        "personalization": "个性化",
        "feedback_action": "操作",
        "feedback_action_like": "👍 喜欢",
        "feedback_action_ignore": "🚫 忽略",
        "feedback_action_lower_similar": "⬇️ 降低此类",
        "feedback_action_follow_author": "🔔 关注作者",
        "feedback_follow_author": "🔔 关注 {author}",
        "feedback_open": "🎯 喜欢 / 忽略 / 降低此类 / 关注作者",
        "feedback_select_one": "请只选一项，把对应复选框改为 `[x]`。",
        "feedback_confirm_help": "提交这条 Issue 后，偏好会应用到后续报告。隐藏元数据只会从仓库所有者创建的 Issue 中读取。",
        "future_title": "语音博客：未来实现",
        "future_copy": "完整日报语音播报正在规划中，后续版本再加入。",
    },
}


def norm_lang(language: str | None) -> str:
    return "zh" if (language or "").strip().lower() in _ZH else "en"


def strings(language: str | None) -> dict[str, str]:
    return STRINGS[norm_lang(language)]


def output_languages(output: dict | None) -> list[str]:
    output = output or {}
    raw = output.get("languages")
    if isinstance(raw, str):
        langs = [raw]
    elif isinstance(raw, list):
        langs = [str(item) for item in raw]
    else:
        langs = [str(output.get("language") or "English")]

    normalized: list[str] = []
    for lang in langs:
        norm = norm_lang(lang)
        if norm not in normalized:
            normalized.append(norm)
    return normalized or ["en"]


def track_display_name(track: dict, language: str | None = None) -> str:
    lang = norm_lang(language or (track.get("output", {}) or {}).get("language"))
    names = track.get("display_names") or {}
    if isinstance(names, dict) and names.get(lang):
        return str(names[lang])
    if lang == "en" and track.get("display_name_en"):
        return str(track["display_name_en"])
    return str(track.get("display_name") or track.get("name") or "report")


def track_description(track: dict, language: str | None = None) -> str:
    lang = norm_lang(language or (track.get("output", {}) or {}).get("language"))
    descriptions = track.get("descriptions") or {}
    if isinstance(descriptions, dict) and descriptions.get(lang):
        return str(descriptions[lang])
    if lang == "en" and track.get("description_en"):
        return str(track["description_en"])
    return str(track.get("description") or "")
