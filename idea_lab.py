#!/usr/bin/env python3
"""
idea_lab.py — Multi-domain Idea Benchmarking System + ThoughtGraph Integration

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
    python idea_lab.py graph            # Portfolio topology + graph health
    python idea_lab.py propose          # ThoughtGraph suggests new idea candidates
    python idea_lab.py topology         # Full graph topology report
    python idea_lab.py connect <a> <b>  # Show conceptual path between two ideas
"""

import sys
import os
import subprocess
from collections import Counter
from models import load_all, save_one
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                     print_idea_summary, print_idea_card, RESET, score_bar)
from domains import list_domains, get_domain

# Lazy import — graph commands only load ThoughtGraph when needed
def _graph_module():
    try:
        from idea_graph import (portfolio_insights, propose_ideas,
                                domain_gap_report, path_between_ideas)
        return portfolio_insights, propose_ideas, domain_gap_report, path_between_ideas
    except ImportError as e:
        print(red(f"\n  ThoughtGraph not found: {e}"))
        print(dim("  Ensure thought_graph.py and idea_graph.py are in the same directory.\n"))
        sys.exit(1)


def find_idea(idea_id: str):
    ideas = load_all()
    matches = [i for k, i in ideas.items() if k.startswith(idea_id)]
    return matches[0] if matches else None


# ── ORIGINAL COMMANDS (unchanged) ────────────────────────────────────────────

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


def cmd_new():
    from benchmark import (phase_capture, phase_benchmark, phase_verdict,
                           phase_test_design, phase_record_result, phase_execute)
    header("IDEA LAB — Full Benchmark Workflow")
    print(dim("  Principle: zero value until tested positive and executed.\n"))
    idea    = phase_capture()
    alive   = phase_benchmark(idea)
    if not alive: return
    save_one(idea)
    proceed = phase_verdict(idea)
    if not proceed: return
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
    print(dim(f"  python idea_lab.py graph   # see how this idea fits the portfolio"))
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
    dom = get_domain(idea.domain)
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
    dims = list(dom["dimensions"].items()) if "dimensions" in dom else []
    if not dims:
        print(red("  No dimensions found for this domain in current stub."))
        return
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
        except ValueError:
            pass
        print(red("  Enter a number 1–6."))
    input_score = ask_score(dim_def)
    while True:
        w_raw = ask("  Weight of Evidence (0.0 to 1.0)", "1.0")
        try:
            weight = float(w_raw)
            if 0.0 <= weight <= 1.0:
                break
        except ValueError:
            pass
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
    if idea.research_notes:
        print(f"  {b('Current Research')}:\n    {idea.research_notes}\n")
    notes = ask("New research notes (will append)")
    idea.research_notes = (idea.research_notes + "\n" + notes).strip() if idea.research_notes else notes
    save_one(idea)
    print(grn("\n  ✔ Research recorded.\n"))


def cmd_result(idea_id: str):
    from benchmark import phase_record_result
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return
    phase_record_result(idea)


def cmd_execute(idea_id: str):
    from benchmark import phase_execute
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
    reason = ask("Kill reason")
    idea.killed = True
    idea.kill_reason = reason
    save_one(idea)
    print(red(f"\n  '{idea.name}' killed.\n"))


def cmd_domains():
    header("Available Domains")
    for i, (key, label, desc) in enumerate(list_domains(), 1):
        print(f"  {cyn(str(i).rjust(2))})  {b(label.ljust(26))}  {dim(desc)}")
    print()


def cmd_report():
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas to report on.\n"))
        return
    all_ideas = list(ideas.values())
    active    = [i for i in all_ideas if not i.killed]
    killed    = [i for i in all_ideas if i.killed]
    tested    = [i for i in all_ideas if i.test and i.test.result]
    passed    = [i for i in all_ideas if i.test and i.test.result == "pass"]
    executed  = [i for i in all_ideas if i.executed]
    with_value= [i for i in all_ideas if i.idea_value() > 0]
    header("PORTFOLIO REPORT")
    section("Pipeline Stats")
    print(f"    Total ideas         : {b(str(len(all_ideas)))}")
    print(f"    Active              : {grn(str(len(active)))}")
    print(f"    Killed              : {red(str(len(killed)))}")
    print(f"    Tests passed        : {grn(str(len(passed)))}/{len(tested)}")
    print(f"    Executed            : {grn(str(len(executed)))}")
    print(f"    Ideas with value >0 : {grn(str(len(with_value)))}")
    section("Idea Value — All")
    for idea in sorted(all_ideas, key=lambda x: x.idea_value(), reverse=True):
        vals = list(idea.scores.values())
        if len(vals) == 6:
            a  = vals[0]*vals[1]*vals[2]
            bv = vals[3]+vals[4]+vals[5]
            tp = 1 if idea.test and idea.test.result == "pass" else 0
            ex = 1 if idea.executed else 0
            iv = idea.idea_value()
            color = grn if iv > 0 else red
            print(f"    {b(idea.name[:22].ljust(22))}  {a}×{bv}×{tp}×{ex} = {color(b(str(int(iv))))}")
    section("Conversion Funnel")
    n = len(all_ideas)
    for label, count in [("Captured",n),("Tests Passed",len(passed)),("Executed",len(executed)),("Value > 0",len(with_value))]:
        bar_w = int((count/max(n,1))*30)
        print(f"    {label.ljust(15)} {'█'*bar_w+'░'*(30-bar_w)} {count}/{n}  ({int(count/n*100)}%)")
    print()
    print(dim("  Run 'python idea_lab.py graph' for topology-based portfolio analysis."))
    print()


# ── NEW GRAPH COMMANDS ────────────────────────────────────────────────────────

def cmd_graph():
    """
    Load portfolio into ThoughtGraph. Show topology-based insights:
    influence ranking, community clusters, domain gaps, duplicate ideas.
    """
    portfolio_insights_fn, _, domain_gap_report_fn, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet. Run: python idea_lab.py new\n"))
        return

    header("PORTFOLIO GRAPH ANALYSIS")
    print(dim("  Your ideas loaded as a knowledge graph. Topology reveals what text cannot.\n"))

    print("  Loading graph", end="", flush=True)
    insights = portfolio_insights_fn(ideas)
    print(f"\r  {grn('✔')} Graph built: {insights['total_ideas']} ideas  "
          f"{insights['active_ideas']} active  {insights['value_ideas']} with value\n")

    # ── Graph health ─────────────────────────────────────────────────────────
    gh = insights["graph_health"]
    grade_color = {
        "A": grn, "B": grn, "C": ylw, "D": ylw, "F": red
    }.get(gh["grade"], ylw)

    section("Portfolio Graph Health")
    print(f"    Score        : {grade_color(b(str(gh['graph_health']))+'/'+'100')} {grade_color(b(gh['grade']))}")
    print(f"    Connectivity : {gh['connectivity']:.1f}/25   (how tightly ideas link)")
    print(f"    Community    : {gh['community_score']:.1f}/25  (how cleanly domains cluster)")
    print(f"    Diversity    : {gh['diversity']:.1f}/15  (how many idea types present)")
    print(f"    Small-world  : {gh['small_world']:.3f}      (cross-domain shortcuts)")
    print(f"    Modularity   : {gh['modularity']:.3f}      (domain separation quality)")
    print(f"    Bridges      : {gh['n_bridges']}           (critical link points)")
    print()
    print(f"    {dim(gh['interpretation'])}")

    # ── Health advice ─────────────────────────────────────────────────────────
    if insights.get("health_advice"):
        print()
        print(f"    {b('Top improvements:')}")
        for adv in insights["health_advice"][:3]:
            pcolor = red if adv["priority"] == "HIGH" else (ylw if adv["priority"] == "MEDIUM" else cyn)
            print(f"    [{pcolor(adv['priority'])}] {adv['area'].upper()}: {adv['issue']}")
            print(f"           → {adv['action']}")

    # ── Influence ranking ─────────────────────────────────────────────────────
    section("Most Influential Ideas (PageRank)")
    print(dim("    Ideas that other ideas depend on structurally."))
    print()
    for i, t in enumerate(insights["top_ideas"], 1):
        iv_color = grn if t["iv"] > 0 else red
        pr_str   = f"{t['pagerank']:.4f}"
        iv_str   = str(t["iv"])
        name_str = t["name"][:36].ljust(36)
        print(f"    {b(str(i)+'.'):<4} {b(name_str)} "
              f"PR={cyn(pr_str)}  "
              f"IV={iv_color(b(iv_str))}  "
              f"[{t['domain']}]")

    # ── Clusters ──────────────────────────────────────────────────────────────
    section("Community Clusters")
    print(dim("    Ideas that group together by semantic + domain affinity."))
    print()
    for c in insights["clusters"]:
        domains_str = " + ".join(c["domains"][:3])
        print(f"    Cluster {c['community_id']} ({c['size']} ideas) [{cyn(domains_str)}]")
        for m in c["members"][:3]:
            iv_col = grn if m["iv"] > 0 else dim
            print(f"      → {m['name'][:40].ljust(40)} IV={iv_col(str(m['iv']))}")

    # ── Domain gaps ───────────────────────────────────────────────────────────
    section("Domain Gaps")
    gap_report = domain_gap_report_fn(ideas)
    if gap_report["absent_count"] == 0:
        print(f"    {grn('✔')} All 13 domains covered.")
    else:
        print(f"    {red(str(gap_report['absent_count']))} domains absent  "
              f"| {ylw(str(gap_report['untested_count']))} untested  "
              f"| {grn(str(gap_report['covered_count']))} covered")
        print()
        for r in gap_report["by_domain"]:
            if r["status"] == "ABSENT":
                print(f"    {red('✗')} {b(r['label'][:24].ljust(24))} {dim(r['action'])}")
            elif r["status"] in ("UNTESTED", "THIN"):
                print(f"    {ylw('~')} {r['label'][:24].ljust(24)} [{r['status']}] {dim(r['action'])}")

    # ── Think insight ─────────────────────────────────────────────────────────
    section("Graph Think — What the Portfolio Needs")
    print(f"    {insights['think_insight']}")
    print()
    if insights["think_bridges"]:
        print(f"    {b('Top bridge proposals:')}")
        for br in insights["think_bridges"]:
            btype = grn("CONNECT") if br["type"] == "connection" else cyn("PROPOSE")
            print(f"    [{btype}] \"{b(br['proposed_concept'])}\"")
            print(f"             bridges {br['anchor_a']} ↔ {br['anchor_b']}")

    # ── Duplicates ────────────────────────────────────────────────────────────
    if insights.get("duplicate_pairs"):
        section("Potential Redundancy")
        print(dim("    Ideas with high semantic similarity — consider merging or differentiating."))
        for dup in insights["duplicate_pairs"]:
            print(f"    {ylw('~')} {dup['idea_a'][:30]} ↔ {dup['idea_b'][:30]}  "
                  f"sim={dup['similarity']:.3f}  [{dup['recommendation']}]")

    # ── Critical bridges ──────────────────────────────────────────────────────
    if insights.get("critical_bridges"):
        section("Critical Bridge Ideas")
        print(dim("    Removing these would disconnect the portfolio. Protect them."))
        for br in insights["critical_bridges"][:3]:
            print(f"    {red('⚡')} {b(br['name'][:40])} [{br['domain']}]")

    print()
    print(dim("  Run 'python idea_lab.py propose' to get new idea candidates from the graph."))
    print(dim("  Run 'python idea_lab.py connect <id_a> <id_b>' to trace the path between ideas."))
    print()


def cmd_propose(domain_filter: str = None):
    """
    Use ThoughtGraph's think() to propose new Idea Lab candidates.
    Optionally filter by domain.
    """
    _, propose_fn, _, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet. Add some first.\n"))
        return

    header("PROPOSE NEW IDEAS — ThoughtGraph think()")
    print(dim("  The graph finds structural gaps in your portfolio and proposes candidates.\n"))

    if domain_filter:
        dom = get_domain(domain_filter)
        print(f"  Biased toward domain: {cyn(dom['label'])}\n")

    print("  Computing...", end="", flush=True)
    proposals = propose_fn(ideas, domain=domain_filter, k=6)
    print(f"\r  {grn('✔')} {len(proposals)} candidates identified\n")

    if not proposals:
        print(ylw("  No proposals generated. Add more diverse ideas first."))
        return

    for i, p in enumerate(proposals, 1):
        btype = grn("WIRE") if p["type"] == "connection" else cyn("NEW")
        print(f"  {b(str(i)+'.')} [{btype}] {b(p['concept'])}")
        print(f"       Domain  : {cyn(p['domain_label'])} ({p['idea_noun']})")
        print(f"       Bridges : {p['anchor_a']} ↔ {p['anchor_b']}")
        print(f"       Score   : {p['bridge_score']:.3f}")
        print(f"       Why     : {dim(p['rationale'][:90])}")
        print()

    print(dim("  To add one: python idea_lab.py new"))
    print(dim("  Then choose the suggested domain and use the proposed name as your starting point."))
    print()


def cmd_topology():
    """
    Full ThoughtGraph topology report on the portfolio.
    Exports metrics, communities, bridges, and health breakdown.
    """
    portfolio_insights_fn, _, domain_gap_report_fn, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet.\n"))
        return

    header("PORTFOLIO TOPOLOGY — Full Report")
    insights = portfolio_insights_fn(ideas)
    gh       = insights["graph_health"]
    gap      = domain_gap_report_fn(ideas)

    section("Topology Metrics")
    metrics = [
        ("Graph health",          f"{gh['graph_health']}/100 {gh['grade']}"),
        ("Connectivity",          f"{gh['connectivity']:.1f}/25"),
        ("Community quality",     f"{gh['community_score']:.1f}/25"),
        ("Diversity",             f"{gh['diversity']:.1f}/15"),
        ("Small-world σ",         str(gh['small_world'])),
        ("Modularity Q",          str(gh['modularity'])),
        ("Bridge edges",          str(gh['n_bridges'])),
        ("Total ideas",           str(insights['total_ideas'])),
        ("Active ideas",          str(insights['active_ideas'])),
        ("Executed ideas",        str(insights['executed_ideas'])),
        ("Ideas with value",      str(insights['value_ideas'])),
        ("Domain coverage",       f"{gap['covered_count']}/13 ({gap['absent_count']} absent)"),
    ]
    for label, val in metrics:
        print(f"    {label.ljust(22)}: {b(val)}")

    section("Domain Coverage Status")
    for r in gap["by_domain"]:
        status_color = grn if r["status"] == "COVERED" else (ylw if r["status"] in ("THIN","UNTESTED") else red)
        bar = "█" * r["value_ideas"] + "░" * max(0, 3 - r["value_ideas"])
        print(f"    {status_color(r['status'].ljust(12))} {r['label'][:26].ljust(26)} {bar}  "
              f"{r['count']} ideas  {r['executed']} executed")

    section("Community Breakdown")
    for c in insights["clusters"]:
        domains = " + ".join(c["domains"][:3])
        print(f"    Cluster {c['community_id']}: {c['size']} ideas  [{cyn(domains)}]")
        for m in c["members"]:
            print(f"      {m['name'][:45].ljust(45)} IV={grn(str(m['iv'])) if m['iv'] > 0 else dim('0')}")

    section("Full Influence Ranking")
    for i, t in enumerate(insights["top_ideas"], 1):
        print(f"    {str(i).rjust(2)}. {t['name'][:38].ljust(38)} "
              f"PR={t['pagerank']:.5f}  IV={t['iv']:>3}")

    section("Graph Think Analysis")
    print(f"    {insights['think_insight']}")
    print()
    if insights["think_bridges"]:
        for br in insights["think_bridges"]:
            print(f"    [{br['type'].upper():10}] {br['proposed_concept'][:38].ljust(38)} "
                  f"score={br['bridge_score']:.3f}")
    print()


def cmd_connect(idea_id_a: str, idea_id_b: str):
    """
    Show the conceptual path between two ideas through the portfolio graph.
    """
    _, _, _, path_fn = _graph_module()
    ideas = load_all()
    idea_a = find_idea(idea_id_a)
    idea_b = find_idea(idea_id_b)

    if not idea_a:
        print(red(f"\n  Idea '{idea_id_a}' not found.\n"))
        return
    if not idea_b:
        print(red(f"\n  Idea '{idea_id_b}' not found.\n"))
        return

    header(f"Conceptual Path: {idea_a.name[:30]} → {idea_b.name[:30]}")
    print("  Tracing...", end="", flush=True)
    result = path_fn(ideas, idea_a.id, idea_b.id)
    print()

    if not result["found"]:
        print(red("  No path found. These ideas may not be connected in the portfolio graph."))
        print(dim("  Try adding more ideas to bridge these domains."))
        return

    print(f"  {grn('Path found')}  |  length {b(str(result['length']))}  |  cost {result['total_cost']:.3f}")
    print()

    for i, hop in enumerate(result["hops"]):
        prefix = "  START" if i == 0 else "     ↓ "
        dom    = hop.get("domain", "?")
        iv     = hop.get("iv", 0)
        iv_str = grn(f"IV={iv}") if iv > 0 else dim(f"IV={iv}")
        strength = f" [strength={hop['edge_strength']:.2f}]" if hop.get("edge_strength") else ""
        print(f"  {prefix}  {b(hop['label'][:40].ljust(40))} [{dom}]  {iv_str}{strength}")

    print()
    print(f"  Full path: {dim(result['explanation'])}")
    print()


# ── ENTRY ────────────────────────────────────────────────────────────────────

def cmd_menu():
    header("IDEA LAB v2 — Benchmark + ThoughtGraph")
    print(dim("  An idea is worth zero until tested positive and executed.\n"))

    print(f"  {b('BENCHMARK')}")
    print(f"  {cyn('new')}              Full benchmark (any domain)")
    print(f"  {cyn('list')}             All ideas")
    print(f"  {cyn('view')}    <id>     Full detail")
    print(f"  {cyn('pivot')}   <id>     Re-score a dimension")
    print(f"  {cyn('research')} <id>    Add deep research notes")
    print(f"  {cyn('result')}  <id>     Record test result")
    print(f"  {cyn('execute')} <id>     Mark as executed")
    print(f"  {cyn('kill')}    <id>     Kill an idea")
    print(f"  {cyn('report')}           Portfolio report + funnel")
    print(f"  {cyn('domains')}          List all 13 domains")
    print()
    print(f"  {b('GRAPH (ThoughtGraph integration)')}")
    print(f"  {cyn('graph')}            Portfolio topology + graph health + clusters")
    print(f"  {cyn('propose')}          Graph suggests new idea candidates")
    print(f"  {cyn('topology')}         Full graph topology report")
    print(f"  {cyn('connect')} <a> <b>  Conceptual path between two ideas")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd  = args[0].lower() if args else ""

    dispatch = {
        "new":        cmd_new,
        "list":       cmd_list,
        "report":     cmd_report,
        "domains":    cmd_domains,
        "graph":      cmd_graph,
        "propose":    lambda: cmd_propose(args[1] if len(args) > 1 else None),
        "topology":   cmd_topology,
    }

    if cmd in dispatch:
        dispatch[cmd]()
    elif cmd == "view"     and len(args) > 1: cmd_view(args[1])
    elif cmd == "pivot"    and len(args) > 1: cmd_pivot(args[1])
    elif cmd == "research" and len(args) > 1: cmd_research(args[1])
    elif cmd == "result"   and len(args) > 1: cmd_result(args[1])
    elif cmd == "execute"  and len(args) > 1: cmd_execute(args[1])
    elif cmd == "kill"     and len(args) > 1: cmd_kill(args[1])
    elif cmd == "connect"  and len(args) > 2: cmd_connect(args[1], args[2])
    else:
        cmd_menu()
