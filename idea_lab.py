#!/usr/bin/env python3
"""
idea_lab.py — Multi-domain Idea Benchmarking System

USAGE:
    python idea_lab.py                  # Help menu
    python idea_lab.py new              # Benchmark a new idea (full flow)
    python idea_lab.py list             # List all ideas
    python idea_lab.py view   <id>      # Full detail on one idea
    python idea_lab.py pivot  <id>      # Re-score a dimension
    python idea_lab.py research <id>    # Add deep research notes
    python idea_lab.py result <id>      # Record test result
    python idea_lab.py execute <id>     # Mark as executed
    python idea_lab.py report           # Portfolio report + funnel
    python idea_lab.py kill   <id>      # Kill an idea manually
    python idea_lab.py domains          # List all available domains
"""

import sys
import os, subprocess
from collections import Counter
from models import load_all, save_one
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                     print_idea_summary, print_idea_card, RESET)
from benchmark import (phase_capture, phase_benchmark, phase_verdict,
                       phase_test_design, phase_record_result, phase_execute, ask, ask_score)
from domains import list_domains, get_domain


def find_idea(idea_id: str):
    ideas   = load_all()
    matches = [i for k, i in ideas.items() if k.startswith(idea_id)]
    return matches[0] if matches else None


# ── COMMANDS ──────────────────────────────────────────────────────────────────

def cmd_new():
    header("IDEA LAB — Full Benchmark Workflow")
    print(dim("  Principle: zero value until tested positive and executed.\n"))

    idea    = phase_capture()
    alive   = phase_benchmark(idea)
    if not alive:
        return
    save_one(idea)

    proceed = phase_verdict(idea)
    if not proceed:
        return

    if idea.verdict in ("STOP", "RISKY"):
        cont = ask("\nRISKY/STOP verdict. Continue to test design anyway? (y/n)", "n")
        if cont.lower() != "y":
            print(ylw(f"  Saved. ID: {idea.id}\n"))
            return

    phase_test_design(idea)

    if ask("\nRecord test result now? (y/n)", "n").lower() == "y":
        phase_record_result(idea)

    if idea.test and idea.test.result == "pass":
        if ask("Mark as executed now? (y/n)", "n").lower() == "y":
            phase_execute(idea)

    print()
    print(grn(f"  ✔ Saved. ID: {b(idea.id)}"))
    print(dim(f"  python idea_lab.py result  {idea.id}"))
    print(dim(f"  python idea_lab.py execute {idea.id}"))
    print(dim(f"  python idea_lab.py view    {idea.id}"))
    print()


def cmd_list():
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet. Run: python idea_lab.py new\n"))
        return

    header(f"All Ideas ({len(ideas)})")
    active = [i for i in ideas.values() if not i.killed]
    killed = [i for i in ideas.values() if i.killed]
    print(dim(f"  {'#':>3}  {'NAME':28} {'DOMAIN':14}  {'VERDICT':12} SCORE  TEST EXE  VALUE"))
    hr()

    for idx, idea in enumerate(sorted(active, key=lambda x: x.total_score, reverse=True), 1):
        print_idea_card(idea, idx)

    if killed:
        print()
        print(red(f"  ── KILLED ({len(killed)}) ──"))
        for idx, idea in enumerate(killed, 1):
            print_idea_card(idea, idx)
    print()


def cmd_view(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return

    header(f"Idea Detail — {idea.id}")
    print_idea_summary(idea)

    dom  = get_domain(idea.domain)

    if idea.test:
        t = idea.test
        section("Test Design")
        print(f"    Assumption  : {t.assumption}")
        print(f"    Method      : {t.test_method}")
        print(f"    Pass if     : {grn(t.success_criteria)}")
        print(f"    Fail if     : {red(t.failure_criteria)}")
        print(f"    Deadline    : {ylw(t.deadline)}")
        if t.result:
            color = grn if t.result == "pass" else red
            print(f"    Result      : {color(t.result.upper())}  ({t.result_date})")
        if t.result_notes:
            print(f"    Notes       : {dim(t.result_notes)}")

    if idea.research_notes:
        section("Research Notes")
        print(f"    {idea.research_notes}")

    if idea.execution_notes:
        section("Execution Notes")
        print(f"    {idea.execution_notes}")

    if idea.killed:
        section("Kill Record")
        print(f"    {red(idea.kill_reason)}")

    section("Idea Value Calculation")
    vals = list(idea.scores.values())
    if len(vals) == 6:
        a  = vals[0] * vals[1] * vals[2]
        bv = vals[3] + vals[4] + vals[5]
        tp = 1 if idea.test and idea.test.result == "pass" else 0
        ex = 1 if idea.executed else 0
        iv = idea.idea_value()
        dim_names = list(dom["dimensions"].keys())
        print(f"    GroupA  ({dim_names[0]} × {dim_names[1]} × {dim_names[2]}) = {a}")
        print(f"    GroupB  ({dim_names[3]} + {dim_names[4]} + {dim_names[5]}) = {bv}")
        print(f"    Test passed = {tp}  |  Executed = {ex}")
        print()
        color = grn if iv > 0 else red
        print(f"    {b('Idea Value')}  =  {a} × {bv} × {tp} × {ex}  =  {color(b(str(int(iv))))}")
    print()


def cmd_pivot(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return

    dom = get_domain(idea.domain)
    header(f"Pivot — {idea.name}")
    print(f"  Domain: {cyn(dom['label'])}")
    print(dim("  Recursive Weighted Pivot: NewScore = (1-w)*OldScore + w*InputScore\n"))

    dims = list(dom["dimensions"].items())
    for i, (key, dim_def) in enumerate(dims, 1):
        current = idea.scores.get(key, 0)
        print(f"    {cyn(str(i))}) {dim_def['name']:28} (current: {ylw(f'{current:.2f}')})")

    while True:
        raw = ask("\n  Pick a dimension to re-score (1–6)", "1")
        try:
            idx = int(raw) - 1
            if 0 <= idx < 6:
                key, dim_def = dims[idx]
                break
        except ValueError: pass
        print(red("  Enter a number 1–6."))

    input_score = ask_score(dim_def)

    while True:
        w_raw = ask("  Weight of Evidence (0.0 to 1.0)", "1.0")
        try:
            weight = float(w_raw)
            if 0.0 <= weight <= 1.0: break
        except ValueError: pass
        print(red("  Enter a float between 0.0 and 1.0."))

    old_score = idea.scores.get(key, 0)
    new_score = (1 - weight) * old_score + weight * input_score

    idea.scores[key] = new_score
    idea.compute_score()
    save_one(idea)

    print(grn(f"\n  ✔ Updated. New total score: {b(f'{idea.total_score:.2f}')}/12\n"))
def cmd_research(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return

    header(f"Record Research — {idea.name}")
    print(dim("  Add deep research findings, citations, or domain evidence.\n"))

    if idea.research_notes:
        print(f"  {b('Current Research')}:")
        print(f"    {idea.research_notes}\n")

    notes = ask("New research notes (will append)")
    if idea.research_notes:
        idea.research_notes += "\n" + notes
    else:
        idea.research_notes = notes

    save_one(idea)
    print(grn("\n  ✔ Research recorded.\n"))


def cmd_result(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return
    phase_record_result(idea)


def cmd_execute(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return
    phase_execute(idea)


def cmd_kill(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return
    reason     = ask("Kill reason")
    idea.killed     = True
    idea.kill_reason = reason
    save_one(idea)
    print(red(f"\n  '{idea.name}' killed.\n"))


def cmd_domains():
    header("Available Domains")
    for i, (key, label, desc) in enumerate(list_domains(), 1):
        print(f"  {cyn(str(i).rjust(2))})  {b(label.ljust(26))}  {dim(desc)}")
    print()


def cmd_report():
    ideas     = load_all()
    if not ideas:
        print(ylw("\n  No ideas to report on.\n"))
        return

    all_ideas  = list(ideas.values())
    active     = [i for i in all_ideas if not i.killed]
    killed     = [i for i in all_ideas if i.killed]
    tested     = [i for i in all_ideas if i.test and i.test.result]
    passed     = [i for i in all_ideas if i.test and i.test.result == "pass"]
    failed     = [i for i in all_ideas if i.test and i.test.result == "fail"]
    executed   = [i for i in all_ideas if i.executed]
    with_value = [i for i in all_ideas if i.idea_value() > 0]

    header("PORTFOLIO REPORT")

    # Knowledge status breakdown
    knowledge_counts = Counter(i.knowledge_status for i in all_ideas)
    section("Knowledge Status")
    for status in ["EXPERT", "KNOWLEDGEABLE", "EXPLORING", "UNRESEARCHED"]:
        count = knowledge_counts.get(status, 0)
        bar_w = int((count / max(len(all_ideas), 1)) * 30)
        bar   = "█" * bar_w + "░" * (30 - bar_w)
        print(f"    {status.ljust(15)} {grn(bar)} {b(str(count))}")

    section("Pipeline Stats")
    print(f"    Total ideas         : {b(str(len(all_ideas)))}")
    print(f"    Active              : {grn(str(len(active)))}")
    print(f"    Killed              : {red(str(len(killed)))}")
    print(f"    Tests run           : {str(len(tested))}")
    print(f"    Tests passed        : {grn(str(len(passed)))}")
    print(f"    Tests failed        : {red(str(len(failed)))}")
    if tested:
        rate  = int(len(passed) / len(tested) * 100)
        color = grn if rate >= 50 else (ylw if rate >= 30 else red)
        print(f"    Pass rate           : {color(str(rate)+'%')}")
    print(f"    Executed            : {grn(str(len(executed)))}")
    print(f"    Ideas with value >0 : {grn(str(len(with_value)))}")

    # Breakdown by domain
    domain_counts = Counter(i.domain for i in all_ideas)
    if len(domain_counts) > 1:
        section("By Domain")
        for domain_key, count in domain_counts.most_common():
            dom   = get_domain(domain_key)
            alive = sum(1 for i in all_ideas if i.domain == domain_key and not i.killed)
            val   = sum(1 for i in all_ideas if i.domain == domain_key and i.idea_value() > 0)
            print(f"    {dom['label'].ljust(28)} total:{b(str(count))}  active:{grn(str(alive))}  value>0:{grn(str(val))}")

    if with_value:
        section("Ideas With Non-Zero Value")
        for idea in sorted(with_value, key=lambda x: x.idea_value(), reverse=True):
            dom = get_domain(idea.domain)
            print(f"    {b(idea.name[:30].ljust(30))}  [{dom['label'][:16]}]  Value: {grn(b(str(int(idea.idea_value()))))}")

    section("Idea Value — All")
    for idea in sorted(all_ideas, key=lambda x: x.idea_value(), reverse=True):
        vals = list(idea.scores.values())
        if len(vals) == 6:
            a  = vals[0] * vals[1] * vals[2]
            bv = vals[3] + vals[4] + vals[5]
            tp = 1 if idea.test and idea.test.result == "pass" else 0
            ex = 1 if idea.executed else 0
            iv = idea.idea_value()
            color = grn if iv > 0 else red
            print(f"    {b(idea.name[:22].ljust(22))}  {a}×{bv}×{tp}×{ex} = {color(b(str(int(iv))))}")

    # Weakness aggregation
    weaknesses = Counter()
    for idea in all_ideas:
        dom = get_domain(idea.domain)
        for key, score in idea.scores.items():
            if score < 2:
                dim_name = dom["dimensions"].get(key, {}).get("name", key)
                weaknesses[dim_name] += 1

    if weaknesses:
        section("Common Weaknesses")
        print(dim("    Dimensions scoring < 2 across the portfolio:"))
        for dim_name, count in weaknesses.most_common(5):
            print(f"      {red('→')} {dim_name:28} {b(str(count))} ideas")

    section("Portfolio Optimization (ROI Ranking)")
    roi_ranked = sorted(all_ideas, key=lambda x: x.roi(), reverse=True)
    for idea in roi_ranked[:10]:
        iv = idea.idea_value()
        roi = idea.roi()
        if iv > 0:
            print(f"      {grn('→')} {b(idea.name[:28].ljust(28))}  Val:{b(str(int(iv)).rjust(4))}  Cost:{b(str(idea.estimated_cost).rjust(4))}  ROI:{grn(b(str(round(roi, 1)).rjust(5)))}")

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
        bar_w = int((count / max(n, 1)) * 30)
        bar   = "█" * bar_w + "░" * (30 - bar_w)
        pct   = int(count / n * 100)
        print(f"    {label.ljust(18)} {grn(bar)} {b(str(count))}/{n}  ({pct}%)")
    print()


def cmd_assessment():
    path = os.path.join(os.path.dirname(__file__), "honest_assessment.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            print(f.read())
    else:
        print("Assessment file not found.")


def cmd_self_eval():
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "self_eval.py")])


def cmd_menu():
    header("IDEA LAB — Multi-Domain Benchmark & Execute")
    print(dim("  An idea is worth zero until tested positive and executed.\n"))
    print(f"  {cyn('new')}              Full benchmark (any domain)")
    print(f"  {cyn('list')}             All ideas")
    print(f"  {cyn('view')}    <id>     Full detail")
    print(f"  {cyn('pivot')}    <id>     Re-score a dimension")
    print(f"  {cyn('research')} <id>     Add deep research notes")
    print(f"  {cyn('result')}  <id>     Record test result")
    print(f"  {cyn('execute')} <id>     Mark as executed")
    print(f"  {cyn('kill')}    <id>     Kill an idea")
    print(f"  {cyn('report')}           Portfolio report")
    print(f"  {cyn('domains')}          List all 13 domains")
    print(f"  {cyn('self-eval')}        Run system self-evaluation")
    print(f"  {cyn('assessment')}       View the latest honest assessment")
    print()


# ── ENTRY ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd  = args[0].lower() if args else ""

    dispatch = {
        "new":     cmd_new,
        "list":    cmd_list,
        "report":  cmd_report,
        "domains": cmd_domains,
        "research": cmd_research,
        "self-eval": cmd_self_eval,
        "assessment": cmd_assessment,
    }

    if cmd in dispatch:
        dispatch[cmd]()
    elif cmd == "view"    and len(args) > 1: cmd_view(args[1])
    elif cmd == "pivot"   and len(args) > 1: cmd_pivot(args[1])
    elif cmd == "research" and len(args) > 1: cmd_research(args[1])
    elif cmd == "result"  and len(args) > 1: cmd_result(args[1])
    elif cmd == "execute" and len(args) > 1: cmd_execute(args[1])
    elif cmd == "kill"    and len(args) > 1: cmd_kill(args[1])
    else:
        cmd_menu()
