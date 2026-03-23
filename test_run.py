#!/usr/bin/env python3
"""
test_run.py — Automated multi-domain test.
Injects one idea per domain to prove the system works across all 12 domains.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models import Idea, TestDesign, save_all, load_all
from domains import DOMAINS, get_domain
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                     print_idea_summary, RESET)
import uuid

# Wipe
save_all({})

def mk():
    return str(uuid.uuid4())[:8]


# ── 12 DOMAIN TEST IDEAS ───────────────────────────────────────────────────────

test_ideas = [

    # 1. Q&A
    Idea(id=mk(), name="Why Do We Dream?", domain="qa",
         description="A synthesis of current scientific understanding of dream function.",
         scores={"question_clarity":2,"prior_research":2,"falsifiability":1,
                 "source_reachability":2,"answer_originality":1,"capability_fit":2},
         test=TestDesign(assumption="Memory consolidation is the primary function of REM dreaming.",
                         test_method="Cross-reference 15+ peer-reviewed papers. Find consensus and dissent.",
                         success_criteria="≥10 independent studies support the consolidation mechanism.",
                         failure_criteria="Majority of studies show no correlation.",
                         deadline="2025-08-20", result="pass",
                         result_notes="12 studies confirmed. 3 dissented. Consensus clear."),
         executed=True, execution_notes="Published 4,000-word synthesis. Cited by 3 researchers."),

    # 2. Methodology
    Idea(id=mk(), name="Async Decision Framework", domain="methodology",
         description="A structured process for making team decisions asynchronously without meetings.",
         scores={"problem_reality":2,"process_specificity":2,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":1,"capability_fit":2},
         test=TestDesign(assumption="Teams can reach decisions 40% faster without synchronous meetings.",
                         test_method="Apply to 5 real decisions at current org. Measure time-to-decision vs last quarter.",
                         success_criteria="Average decision time drops ≥35%.",
                         failure_criteria="No measurable improvement or slower.",
                         deadline="2025-09-01", result="pass",
                         result_notes="Average improvement: 41%. One decision took longer due to conflict."),
         executed=True, execution_notes="Deployed org-wide. Now standard process. Documented in handbook."),

    # 3. Project
    Idea(id=mk(), name="Internal API Gateway", domain="project",
         description="Unified API gateway to replace 7 separate service endpoints in the platform.",
         scores={"objective_clarity":2,"scope_specificity":2,"falsifiability":2,
                 "execution_reachability":1,"competition_resistance":2,"capability_fit":2},
         test=TestDesign(assumption="A unified gateway can handle all 7 service contracts without breaking changes.",
                         test_method="Build prototype supporting 3 services. Run regression tests against production traffic replay.",
                         success_criteria="Zero breaking changes on 3 services. Latency ≤ +5ms.",
                         failure_criteria="Any breaking change or latency > +10ms.",
                         deadline="2025-10-01", result=None)),

    # 4. Law / Policy
    Idea(id=mk(), name="Algorithmic Audit Mandate", domain="law",
         description="Require public audits of AI systems used in hiring decisions.",
         scores={"problem_evidence":2,"legal_specificity":1,"falsifiability":1,
                 "execution_reachability":0,"competition_resistance":1,"capability_fit":1},
         killed=True,
         kill_reason="RISKY — Legislative pathway scored 0. No institutional standing. Rebuild with a coalition first."),

    # 5. Mathematics
    Idea(id=mk(), name="Graph Coloring Bound Conjecture", domain="mathematics",
         description="A conjectured tighter bound on chromatic numbers for sparse planar graphs.",
         scores={"statement_precision":2,"novelty":2,"falsifiability":1,
                 "execution_reachability":1,"competition_resistance":2,"capability_fit":1},
         test=TestDesign(assumption="The bound holds for all planar graphs with average degree < 3.",
                         test_method="Attempt formal proof via discharging method. Check 50 known counterexample candidates.",
                         success_criteria="Proof holds for all tested cases with no counterexample found.",
                         failure_criteria="Single valid counterexample disproves the bound.",
                         deadline="2025-12-31", result=None)),

    # 6. Science
    Idea(id=mk(), name="Microplastics & Gut Permeability", domain="science",
         description="Hypothesis: repeated ingestion of 10µm microplastics increases intestinal permeability in rodents.",
         scores={"hypothesis_precision":2,"prior_evidence":1,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":2,"capability_fit":2},
         test=TestDesign(assumption="10µm particles cross the intestinal epithelium and increase permeability markers.",
                         test_method="Randomized controlled trial in 60 rats. Measure FITC-dextran flux at 4 and 8 weeks.",
                         success_criteria="≥25% increase in permeability markers vs control, p<0.05.",
                         failure_criteria="No significant difference at p<0.05.",
                         deadline="2026-03-01", result="pass",
                         result_notes="32% increase. p=0.021. Replicated in second cohort."),
         executed=True, execution_notes="Submitted to Nature Microbiology. Under review."),

    # 7. Philosophy
    Idea(id=mk(), name="Moral Obligation Without Free Will", domain="philosophy",
         description="Thesis: moral obligation remains coherent even under hard determinism.",
         scores={"thesis_clarity":2,"premise_validity":2,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":1,"capability_fit":2},
         test=TestDesign(assumption="The concept of 'could have done otherwise' is not required for moral responsibility.",
                         test_method="Test argument against Frankfurt cases and Strawson's reactive attitudes framework.",
                         success_criteria="Argument survives both without requiring compatibilist assumptions.",
                         failure_criteria="Either framework exposes an irresolvable contradiction in the thesis.",
                         deadline="2025-08-01", result="pass",
                         result_notes="Survived Frankfurt cases. Strawson required one qualification but did not defeat the thesis."),
         executed=True, execution_notes="Published in Philosophy Quarterly. 8 citations in 6 months."),

    # 8. Business
    Idea(id=mk(), name="FreightMatch AI", domain="business",
         description="Match empty truck return legs with SME shippers to cut deadhead costs.",
         scores={"problem_reality":2,"solution_specificity":2,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":1,"capability_fit":2},
         test=TestDesign(assumption="SME shippers will book through a zero-fee platform for a 15% rate reduction.",
                         test_method="Cold outreach to 30 shippers. Track booking rate.",
                         success_criteria="≥12/30 shippers complete at least one booking.",
                         failure_criteria="<6/30 complete any booking.",
                         deadline="2025-08-15", result="pass",
                         result_notes="16/30 booked. 5 asked for invoicing."),
         executed=True, execution_notes="v1 live. 3 paying lanes. $40K GMV in first month."),

    # 9. Education
    Idea(id=mk(), name="Proof-First Calculus", domain="education",
         description="Teach limits and derivatives through proof construction before formula application.",
         scores={"learning_gap":2,"concept_specificity":2,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":2,"capability_fit":2},
         test=TestDesign(assumption="Students taught proof-first retain derivative rules better after 6 weeks.",
                         test_method="Split 40 students. Group A: traditional. Group B: proof-first. Test at week 6.",
                         success_criteria="Group B scores ≥15% higher on unseen problem set.",
                         failure_criteria="No significant difference or Group A scores higher.",
                         deadline="2025-11-01", result=None)),

    # 10. Technology
    Idea(id=mk(), name="Zero-Copy Event Bus", domain="technology",
         description="In-process event bus using memory-mapped buffers to eliminate serialization overhead.",
         scores={"technical_requirement":2,"solution_specificity":2,"falsifiability":2,
                 "execution_reachability":2,"competition_resistance":2,"capability_fit":2},
         test=TestDesign(assumption="Zero-copy delivery reduces inter-service latency by ≥60% vs JSON serialization.",
                         test_method="Benchmark: 1M messages/sec on identical hardware. Measure P99 latency.",
                         success_criteria="P99 latency ≤ 0.4ms vs baseline 1.1ms.",
                         failure_criteria="Less than 40% latency reduction.",
                         deadline="2025-09-15", result="pass",
                         result_notes="P99: 0.31ms. 72% reduction. Stable at 1.5M msg/s."),
         executed=True, execution_notes="Deployed to production. Replaced Redis pub/sub in 4 services."),

    # 11. Social / Behavioral
    Idea(id=mk(), name="Default-On Privacy Settings", domain="social",
         description="Claim: opt-out privacy defaults reduce data sharing by >60% vs opt-in.",
         scores={"claim_precision":2,"evidence_base":2,"falsifiability":2,
                 "execution_reachability":1,"competition_resistance":1,"capability_fit":2},
         test=TestDesign(assumption="Users share 60%+ less data under opt-out defaults than opt-in.",
                         test_method="A/B test on 10,000 users. Measure data-sharing consent rates.",
                         success_criteria="≥55% reduction in data-sharing under opt-out.",
                         failure_criteria="<30% reduction.",
                         deadline="2025-10-01", result=None)),

    # 12. Creative
    Idea(id=mk(), name="The Memory Architect", domain="creative",
         description="A novel told entirely through objects — no dialogue, no narration, only artifact descriptions.",
         scores={"concept_clarity":2,"originality":2,"falsifiability":1,
                 "execution_reachability":2,"competition_resistance":2,"capability_fit":2},
         test=TestDesign(assumption="Readers will follow a complete narrative arc through objects alone.",
                         test_method="Share 3-chapter prototype with 20 readers. Measure chapter completion rate.",
                         success_criteria="≥14/20 complete all 3 chapters without prompting.",
                         failure_criteria="<8/20 complete all 3 chapters.",
                         deadline="2025-09-01", result="pass",
                         result_notes="17/20 completed. 3 asked when the full book releases."),
         executed=True, execution_notes="Full manuscript completed. Submitted to 6 literary agents."),
]


# ── SAVE ──────────────────────────────────────────────────────────────────────
from models import save_all as _save_all
_save_all({i.id: i for i in test_ideas})
# Compute scores
for idea in test_ideas:
    idea.compute_score()
_save_all({i.id: i for i in test_ideas})


# ── PRINT ALL SUMMARIES ───────────────────────────────────────────────────────
header("MULTI-DOMAIN TEST RUN — 12 Ideas × 12 Domains")
print(dim("  Verifying the system adapts correctly to every domain type.\n"))

for idea in test_ideas:
    print_idea_summary(idea)
    hr()


# ── PORTFOLIO REPORT ─────────────────────────────────────────────────────────
ideas      = load_all()
all_ideas  = list(ideas.values())
active     = [i for i in all_ideas if not i.killed]
killed     = [i for i in all_ideas if i.killed]
tested     = [i for i in all_ideas if i.test and i.test.result]
passed     = [i for i in all_ideas if i.test and i.test.result == "pass"]
failed     = [i for i in all_ideas if i.test and i.test.result == "fail"]
executed   = [i for i in all_ideas if i.executed]
with_value = [i for i in all_ideas if i.idea_value() > 0]

header("PORTFOLIO REPORT — ALL DOMAINS")

section("Pipeline Stats")
print(f"    Domains covered     : {b('12')}")
print(f"    Total ideas         : {b(str(len(all_ideas)))}")
print(f"    Active              : {grn(str(len(active)))}")
print(f"    Killed              : {red(str(len(killed)))}")
print(f"    Tests run           : {b(str(len(tested)))}")
print(f"    Tests passed        : {grn(str(len(passed)))}")
print(f"    Tests failed        : {red(str(len(failed)))}")
if tested:
    rate  = int(len(passed)/len(tested)*100)
    color = grn if rate >= 50 else (ylw if rate >= 30 else red)
    print(f"    Pass rate           : {color(str(rate)+'%')}")
print(f"    Executed            : {grn(str(len(executed)))}")
print(f"    Ideas with value >0 : {grn(str(len(with_value)))}")

section("Idea Value — By Domain")
for idea in sorted(all_ideas, key=lambda x: x.idea_value(), reverse=True):
    vals = list(idea.scores.values())
    dom  = get_domain(idea.domain)
    if len(vals) == 6:
        a  = vals[0]*vals[1]*vals[2]
        bv = vals[3]+vals[4]+vals[5]
        tp = 1 if idea.test and idea.test.result == "pass" else 0
        ex = 1 if idea.executed else 0
        iv = idea.idea_value()
        color = grn if iv > 0 else (ylw if iv == 0 and not idea.killed else red)
        tag   = red(" [KILLED]") if idea.killed else (ylw(" [PENDING]") if not idea.test or not idea.test.result else "")
        print(f"    {b(idea.name[:22].ljust(22))} [{dom['label'][:16].ljust(16)}]  "
              f"{a}×{bv}×{tp}×{ex} = {color(b(str(int(iv))))}{tag}")

section("Conversion Funnel")
n = len(all_ideas)
stages = [
    ("Captured",      n),
    ("Score ≥ 8",     len([i for i in all_ideas if i.total_score >= 8])),
    ("Test Designed", len([i for i in all_ideas if i.test])),
    ("Test Passed",   len(passed)),
    ("Executed",      len(executed)),
    ("Value > 0",     len(with_value)),
]
for label, count in stages:
    bar_w = int((count/max(n,1))*30)
    bar   = "█"*bar_w + "░"*(30-bar_w)
    pct   = int(count/n*100)
    print(f"    {label.ljust(18)} {grn(bar)} {b(str(count))}/{n}  ({pct}%)")

print()
print(dim("  ─────────────────────────────────────────────────────────"))
print(f"  {b('RESULT:')} {len(with_value)}/{n} ideas generated non-zero value.")
print(f"  {n - len(with_value)} were stopped or are pending — no resources wasted on unproven ideas.")
print()
