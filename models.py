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
    (10, 12.1): ("STRONG",      "Design your minimum test immediately."),
    (8,  10):   ("CONDITIONAL", "Identify the weak dimension. Resolve it before proceeding."),
    (5,  8):    ("RISKY",       "Don't invest resources. Run a cheap test on the weakest dimension first."),
    (0,  5):    ("STOP",        "Too many unresolved assumptions. Redesign or abandon."),
}


@dataclass
class TestDesign:
    assumption: str = ""
    test_method: str = ""
    success_criteria: str = ""
    failure_criteria: str = ""
    deadline: str = ""
    result: Optional[str] = None
    result_date: Optional[str] = None
    result_notes: str = ""


@dataclass
class Idea:
    id: str
    name: str
    description: str
    domain: str
    scores: dict = field(default_factory=dict)
    total_score: float = 0.0
    verdict: str = ""
    verdict_action: str = ""
    test: Optional[TestDesign] = None
    executed: bool = False
    execution_notes: str = ""
    estimated_cost: float = 1.0
    research_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    killed: bool = False
    kill_reason: str = ""
    # v2: graph tracking
    graph_node_id: Optional[int] = None

    @property
    def knowledge_status(self) -> str:
        if self.executed:
            return "EXPERT"
        if self.test and self.test.result == "pass":
            return "KNOWLEDGEABLE"
        research_depth = len(self.research_notes.split()) if self.research_notes else 0
        if research_depth > 100:
            return "KNOWLEDGEABLE"
        if research_depth > 0:
            return "EXPLORING"
        return "UNRESEARCHED"

    def compute_score(self):
        s = sum(self.scores.values())
        self.total_score = s
        for (lo, hi), (verdict, action) in VERDICTS.items():
            if lo <= s < hi:
                self.verdict = verdict
                self.verdict_action = action
                break
        if s >= 12:
            self.verdict, self.verdict_action = VERDICTS[(10, 12.1)]

    def idea_value(self) -> float:
        vals = list(self.scores.values())
        if len(vals) < 6:
            return 0.0
        group_a = vals[0] * vals[1] * vals[2]
        group_b = vals[3] + vals[4] + vals[5]
        test_passed = 1 if (self.test and self.test.result == "pass") else 0
        exe = 1 if self.executed else 0
        return group_a * group_b * test_passed * exe

    def roi(self) -> float:
        if self.estimated_cost <= 0:
            return 0.0
        return self.idea_value() / self.estimated_cost

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        test_data = d.pop("test", None)
        # forward-compat: ignore unknown fields
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid}
        idea = cls(**d)
        if test_data:
            idea.test = TestDesign(**test_data)
        return idea


def load_all() -> dict:
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH) as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        import sys
        print(f"Warning: {DB_PATH} is corrupt. Returning empty dataset.", file=sys.stderr)
        return {}
    return {k: Idea.from_dict(v) for k, v in raw.items()}


def save_all(ideas: dict):
    with open(DB_PATH, "w") as f:
        json.dump({k: v.to_dict() for k, v in ideas.items()}, f, indent=2)


def save_one(idea: Idea):
    ideas = load_all()
    idea.updated_at = datetime.now().isoformat()
    ideas[idea.id] = idea
    save_all(ideas)
