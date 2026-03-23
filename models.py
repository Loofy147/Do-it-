"""
models.py — Domain-aware data structures and storage
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "ideas.json")

VERDICTS = {
    (10, 12): ("STRONG",      "Design your minimum test immediately."),
    (8,  9):  ("CONDITIONAL", "Identify the weak dimension. Resolve it before proceeding."),
    (5,  7):  ("RISKY",       "Don't invest resources. Run a cheap test on the weakest dimension first."),
    (0,  4):  ("STOP",        "Too many unresolved assumptions. Redesign or abandon."),
}


@dataclass
class TestDesign:
    assumption: str = ""
    test_method: str = ""
    success_criteria: str = ""
    failure_criteria: str = ""
    deadline: str = ""
    result: Optional[str] = None       # "pass" | "fail" | None
    result_date: Optional[str] = None
    result_notes: str = ""


@dataclass
class Idea:
    id: str
    name: str
    description: str
    domain: str                        # key into DOMAINS registry
    scores: dict = field(default_factory=dict)
    total_score: int = 0
    verdict: str = ""
    verdict_action: str = ""
    test: Optional[TestDesign] = None
    executed: bool = False
    execution_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    killed: bool = False
    kill_reason: str = ""

    def compute_score(self):
        s = sum(self.scores.values())
        self.total_score = s
        for (lo, hi), (verdict, action) in VERDICTS.items():
            if lo <= s <= hi:
                self.verdict = verdict
                self.verdict_action = action
                break

    def idea_value(self) -> float:
        """
        IdeaValue = GroupA × GroupB × test_passed × executed

        GroupA = first three dimension scores multiplied  (precision/validity/falsifiability)
        GroupB = last three dimension scores summed        (reach + resistance + fit)

        If any multiplier is 0 → total value = 0.
        This enforces the core principle: untested or unexecuted = zero.
        """
        vals = list(self.scores.values())
        if len(vals) < 6:
            return 0.0
        group_a = vals[0] * vals[1] * vals[2]
        group_b = vals[3] + vals[4] + vals[5]
        test_passed = 1 if (self.test and self.test.result == "pass") else 0
        exe = 1 if self.executed else 0
        return group_a * group_b * test_passed * exe

    def to_dict(self):
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        test_data = d.pop("test", None)
        idea = cls(**d)
        if test_data:
            idea.test = TestDesign(**test_data)
        return idea


# ── STORAGE ────────────────────────────────────────────────────────────────────

def load_all() -> dict:
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH) as f:
        raw = json.load(f)
    return {k: Idea.from_dict(v) for k, v in raw.items()}


def save_all(ideas: dict):
    with open(DB_PATH, "w") as f:
        json.dump({k: v.to_dict() for k, v in ideas.items()}, f, indent=2)


def save_one(idea: Idea):
    ideas = load_all()
    idea.updated_at = datetime.now().isoformat()
    ideas[idea.id] = idea
    save_all(ideas)
