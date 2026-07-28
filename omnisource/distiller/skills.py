"""Expert skill prompts for taxonomy leaves."""
from __future__ import annotations

from pathlib import Path

from ..config import ROOT
from .models import ExpertSkill, Taxonomy

SKILL_DIR = ROOT / "omnisource" / "expert_skills"


def load_skill_library(taxonomy: Taxonomy, skill_root: Path | None = None) -> dict[str, ExpertSkill]:
    skill_root = skill_root or SKILL_DIR / taxonomy.version.replace("-", "_")
    skills: dict[str, ExpertSkill] = {}
    for leaf_id, leaf in taxonomy.leaves.items():
        path = skill_root / f"{leaf_id}.md"
        if path.exists():
            prompt = path.read_text(encoding="utf-8").strip()
        else:
            prompt = f"你是{leaf.name}领域专家，按统一 rubric 审查论文质量、证据和复现性。"
            path = None
        skills[leaf_id] = ExpertSkill(leaf_id=leaf_id, prompt=prompt, path=path)
    return skills
