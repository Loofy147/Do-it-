"""
benchmark.py — Domain-aware benchmarking phases
"""

import uuid
from datetime import datetime
from models import Idea, TestDesign, save_one
from domains import DOMAINS, list_domains, get_domain
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                     print_idea_summary, VERDICT_COLOR, RESET)


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"  {prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return val if val else default


def ask_score(dim_def: dict) -> int:
    print()
    print(f"  {b(dim_def['name'])}")
    print(f"  {dim(dim_def['question'])}")
    print()
    for score_val, desc in dim_def["scores"].items():
        color = grn if score_val == 2 else (ylw if score_val == 1 else red)
        print(f"    {color(str(score_val))})  {desc}")
    print()
    while True:
        raw = ask("Score (0 / 1 / 2)", "1")
        if raw in ("0", "1", "2"):
            return int(raw)
        print(red("  Enter 0, 1, or 2."))


# ── PHASE 1 — CAPTURE ─────────────────────────────────────────────────────────

def phase_capture() -> Idea:
    header("Phase 1 — Capture & Classify")

    # Domain selection
    print(b("  Choose the domain of your idea:\n"))
    domains = list_domains()
    for i, (key, label, desc) in enumerate(domains, 1):
        print(f"    {cyn(str(i).rjust(2))})  {b(label.ljust(26))} {dim(desc)}")
    print()

    while True:
        raw = ask("Domain number", "1")
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(domains):
                domain_key = domains[idx][0]
                dom = get_domain(domain_key)
                print(f"\n  {grn('✔')} Domain: {b(dom['label'])}")
                print(f"  {dim('Test means:')}  {dim(dom['test_guide'][:80]+'...')}")
                print(f"  {dim('Executed means:')} {dim(dom['execute_guide'][:80])}")
                break
        except ValueError:
            pass
        print(red(f"  Enter a number 1–{len(domains)}."))

    print()
    idea_noun = dom["idea_noun"]
    name = ask(f"{idea_noun} name (short label)")
    if not name:
        name = f"Unnamed {idea_noun}"
    description = ask("Describe it in one sentence")

    return Idea(
        id=str(uuid.uuid4())[:8],
        name=name,
        description=description,
        domain=domain_key,
    )


# ── PHASE 2 — BENCHMARK ───────────────────────────────────────────────────────

def phase_benchmark(idea: Idea) -> bool:
    dom      = get_domain(idea.domain)
    kill_dim = dom["kill_dim"]

    header(f"Phase 2 — Benchmark: 6 Dimensions for {dom['label']}")
    print(dim("  Score ruthlessly. The system only works when you are honest.\n"))

    for key, dim_def in dom["dimensions"].items():
        score = ask_score(dim_def)
        idea.scores[key] = score

        if score == 0 and key == kill_dim:
            print()
            print(red(f"  ☠  KILL CONDITION: {dim_def['name']} scored 0."))
            print(red(f"  This is the foundation dimension for this domain."))
            print(red(f"  You cannot build on an unconfirmed foundation. STOP."))
            idea.compute_score()
            idea.killed = True
            idea.kill_reason = f"Kill condition triggered: {dim_def['name']} scored 0."
            save_one(idea)
            return False

    idea.compute_score()
    return True


# ── PHASE 3 — VERDICT ─────────────────────────────────────────────────────────

def phase_verdict(idea: Idea) -> bool:
    header("Phase 3 — Verdict")
    vc = VERDICT_COLOR.get(idea.verdict, "")

    print(f"\n  Total Score : {b(str(idea.total_score))}/12")
    print(f"  Verdict     : {vc}{b(idea.verdict)}{RESET}")
    print(f"  Action      : {idea.verdict_action}\n")

    dom  = get_domain(idea.domain)
    dims = dom["dimensions"]
    dim_keys = list(dims.keys())

    weakest_key = min(idea.scores, key=idea.scores.get)
    weakest_val = idea.scores[weakest_key]
    weakest_name = dims[weakest_key]["name"]
    print(f"  Weakest dimension: {red(weakest_name)} (scored {weakest_val}/2)")
    print(f"  {dim('Resolve this first if you proceed.')}\n")

    if idea.verdict == "STOP":
        print(red("  This idea should not proceed to test design as stated."))
        confirm = ask("Kill this idea? (y/n)", "y")
        if confirm.lower() == "y":
            idea.killed = True
            idea.kill_reason = f"Verdict STOP — score {idea.total_score}/12."
            save_one(idea)
            print(red("\n  Killed and recorded.\n"))
            return False
    return True


# ── PHASE 4 — TEST DESIGN ─────────────────────────────────────────────────────

def phase_test_design(idea: Idea):
    dom = get_domain(idea.domain)

    header(f"Phase 4 — Design the Minimum Test  [{dom['label']}]")
    print(dim(f"  What a valid test looks like in this domain:"))
    print(f"  {ylw(dom['test_guide'])}\n")
    print(dim("  Rules: Cheap. Fast. Binary. Define failure BEFORE you run it.\n"))

    print(b("  Step 1 — Critical Assumption"))
    print(dim("  What single assumption does everything else depend on?"))
    print(dim("  If wrong, this idea collapses regardless of other factors."))
    assumption = ask("\n  Assumption")

    print()
    print(b("  Step 2 — Test Method"))
    print(dim("  Cheapest and fastest way to stress-test that assumption."))
    test_method = ask("\n  Test method")

    print()
    print(b("  Step 3 — Pass Condition  (define BEFORE running)"))
    print(dim("  Specific, measurable result that means this assumption holds."))
    success_criteria = ask("\n  Pass if")

    print()
    print(b("  Step 4 — Fail Condition  (define BEFORE running)"))
    print(dim("  Specific result that means stop. No negotiating after the fact."))
    failure_criteria = ask("\n  Fail if")

    print()
    print(b("  Step 5 — Deadline"))
    print(dim("  No deadline = not a test. It is an open-ended project."))
    deadline = ask("\n  Deadline")

    idea.test = TestDesign(
        assumption=assumption,
        test_method=test_method,
        success_criteria=success_criteria,
        failure_criteria=failure_criteria,
        deadline=deadline,
    )
    save_one(idea)

    print()
    print(grn("  ✔ Test contract locked.\n"))
    print(b("  CONTRACT:"))
    print(f"    Assumption  : {assumption}")
    print(f"    Method      : {test_method}")
    print(f"    PASS if     : {grn(success_criteria)}")
    print(f"    FAIL if     : {red(failure_criteria)}")
    print(f"    Deadline    : {ylw(deadline)}")
    print()
    print(red("  You cannot change pass/fail criteria after this point."))


# ── PHASE 5A — RECORD TEST RESULT ─────────────────────────────────────────────

def phase_record_result(idea: Idea):
    dom = get_domain(idea.domain)
    header(f"Phase 5 — Record Test Result  [{dom['label']}]")

    if not idea.test:
        print(red("  No test designed. Run the full benchmark first."))
        return

    t = idea.test
    print(f"  Assumption  : {dim(t.assumption)}")
    print(f"  PASS if     : {grn(t.success_criteria)}")
    print(f"  FAIL if     : {red(t.failure_criteria)}")
    print(f"  Deadline    : {ylw(t.deadline)}")
    print()

    while True:
        raw = ask("Result (pass / fail)").lower()
        if raw in ("pass", "fail"):
            break
        print(red("  Enter 'pass' or 'fail'."))

    t.result      = raw
    t.result_date = datetime.now().strftime("%Y-%m-%d")
    t.result_notes = ask("Notes")
    save_one(idea)

    print()
    if raw == "pass":
        print(grn("  ✔ TEST PASSED."))
        print(grn(f"  What execution means in {dom['label']}: {dom['execute_guide']}"))
        print(b("  Now execute."))
    else:
        print(red("  ✘ TEST FAILED."))
        print(red("  The idea as stated is wrong."))
        print()
        print(b("  Two legitimate options:"))
        print("    1) PIVOT  — change one variable, redesign the test")
        print("    2) KILL   — record the learning, move on")
        print()
        choice = ask("Kill this idea? (y/n)", "y")
        if choice.lower() == "y":
            idea.killed     = True
            idea.kill_reason = f"Test failed on: {t.assumption}"
            save_one(idea)
            print(red("\n  Killed. Learning recorded.\n"))
        else:
            print(ylw("  Kept open for pivot. Redesign the test before continuing."))


# ── PHASE 5B — MARK AS EXECUTED ───────────────────────────────────────────────

def phase_execute(idea: Idea):
    dom = get_domain(idea.domain)
    header(f"Mark As Executed  [{dom['label']}]")
    print(dim(f"  Execution in this domain means: {dom['execute_guide']}\n"))

    if not idea.test or idea.test.result != "pass":
        print(red("  This idea has not passed its test."))
        print(red("  Executing without a passed test gives Idea Value = 0 by formula."))
        confirm = ask("Proceed anyway? (y/n)", "n")
        if confirm.lower() != "y":
            return

    notes      = ask("Execution notes — what was built, proven, published, deployed, or enacted")
    idea.executed       = True
    idea.execution_notes = notes
    save_one(idea)

    iv   = idea.idea_value()
    vals = list(idea.scores.values())
    a    = vals[0] * vals[1] * vals[2]
    bv   = vals[3] + vals[4] + vals[5]
    tp   = 1 if idea.test and idea.test.result == "pass" else 0

    print()
    print(grn("  ✔ Marked as executed."))
    print()
    print(b("  IDEA VALUE:"))
    print(f"    GroupA (dim1 × dim2 × dim3) = {a}")
    print(f"    GroupB (dim4 + dim5 + dim6) = {bv}")
    print(f"    Test passed                 = {tp}")
    print(f"    Executed                    = 1")
    print()
    color = grn if iv > 0 else red
    print(f"    Value = {a} × {bv} × {tp} × 1 = {color(b(str(int(iv))))}")
