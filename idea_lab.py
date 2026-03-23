#!/usr/bin/env python3
"""
idea_lab.py — Multi-domain Idea Benchmarking System

USAGE:
    python idea_lab.py                  # Help menu
    python idea_lab.py new              # Benchmark a new idea (full flow)
    python idea_lab.py list             # List all ideas
    python idea_lab.py view   <id>      # Full detail on one idea
    python idea_lab.py result <id>      # Record test result
    python idea_lab.py execute <id>     # Mark as executed
    python idea_lab.py report           # Portfolio report + funnel
    python idea_lab.py kill   <id>      # Kill an idea manually
    python idea_lab.py domains          # List all available domains
"""

import sys
from models import load_all, save_one
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                     print_idea_summary, print_idea_card, RESET)
from benchmark import (phase_capture, phase_benchmark, phase_verdict,
                       phase_test_design, phase_record_result, phase_execute, ask)
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
    from collections import Counter
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


def cmd_menu():
    header("IDEA LAB — Multi-Domain Benchmark & Execute")
    print(dim("  An idea is worth zero until tested positive and executed.\n"))
    print(f"  {cyn('new')}              Full benchmark (any domain)")
    print(f"  {cyn('list')}             All ideas")
    print(f"  {cyn('view')}    <id>     Full detail")
    print(f"  {cyn('result')}  <id>     Record test result")
    print(f"  {cyn('execute')} <id>     Mark as executed")
    print(f"  {cyn('kill')}    <id>     Kill an idea")
    print(f"  {cyn('report')}           Portfolio report")
    print(f"  {cyn('domains')}          List all 12 domains")
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
    }

    if cmd in dispatch:
        dispatch[cmd]()
    elif cmd == "view"    and len(args) > 1: cmd_view(args[1])
    elif cmd == "result"  and len(args) > 1: cmd_result(args[1])
    elif cmd == "execute" and len(args) > 1: cmd_execute(args[1])
    elif cmd == "kill"    and len(args) > 1: cmd_kill(args[1])
    else:
        cmd_menu()
