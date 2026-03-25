"""
idea_lab.py — Idea Lab CLI
Enhanced with ThoughtGraph integration.
"""

import sys
import os
import json
from collections import Counter, defaultdict
from models import load_all, save_one, Idea, TestDesign
from display import (header, section, hr, b, dim, red, grn, ylw, cyn,
                    print_idea_summary, print_idea_card)
from domains import list_domains, get_domain

# ── GRAPH INTEGRATION ─────────────────────────────────────────────────────────

def _graph_module():
    """Lazy import of graph module to avoid heavy dependencies if not used."""
    try:
        import idea_graph as ig
        return (ig.portfolio_insights, ig.propose_ideas,
                ig.domain_gap_report, ig.path_between_ideas,
                ig.sync_to_graph)
    except ImportError as e:
        print(red(f"\n  ThoughtGraph not found: {e}"))
        print(dim("  Ensure thought_graph.py and idea_graph.py are in the same directory.\n"))
        sys.exit(1)

# ── UTILS ────────────────────────────────────────────────────────────────────

def find_idea(idea_id: str):
    ideas = load_all()
    return ideas.get(idea_id)

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"  {prompt}{suffix}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print("\n  Aborted.")
        sys.exit(0)

def ask_score(dim_def: dict) -> int:
    print(f"\n  {b(dim_def['name'])}")
    print(f"  {dim(dim_def['question'])}")
    for val, desc in dim_def["scores"].items():
        print(f"    {val}: {desc}")

    while True:
        try:
            choice = input(f"  Score (0-2): ").strip()
            if choice == "": return 0
            val = int(choice)
            if 0 <= val <= 2: return val
        except ValueError:
            pass
        print(red("  Enter 0, 1, or 2."))

# ── COMMANDS ─────────────────────────────────────────────────────────────────

def cmd_new():
    header("NEW IDEA BENCHMARK")
    name = ask("Idea Name")
    if not name: return
    desc = ask("Short Description")
    print("\n  Available Domains:")
    doms = list_domains()
    for i, (key, label, _) in enumerate(doms, 1):
        print(f"    {i}. {label.ljust(25)} ({key})")
    choice = ask("Select Domain (number or key)", "1")
    domain_key = "business"
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(doms): domain_key = doms[idx][0]
    else: domain_key = choice if choice in dict((d[0], d[1]) for d in doms) else "business"
    dom_cfg = get_domain(domain_key)
    print(f"\n  Scoring {b(dom_cfg['label'])}...")
    scores = {}
    for key, dim_def in dom_cfg["dimensions"].items():
        scores[key] = ask_score(dim_def)
    idea = Idea(id=name.lower().replace(" ", "_")[:24], name=name, description=desc, domain=domain_key, scores=scores)
    idea.compute_score()
    kd = dom_cfg.get("kill_dim")
    if kd and scores.get(kd) == 0:
        idea.killed = True
        idea.kill_reason = f"Kill condition fired: {dom_cfg['dimensions'][kd]['name']} scored 0."
        print(red(f"\n  ☠  IDEA KILLED: {idea.kill_reason}"))
    save_one(idea)
    print_idea_summary(idea)
    print(grn(f"  ✔ Idea '{idea.id}' saved.\n"))

def cmd_list():
    header("IDEA PORTFOLIO")
    ideas = load_all()
    if not ideas:
        print(ylw("  No ideas yet.\n"))
        return
    sorted_ideas = sorted(ideas.values(), key=lambda x: -x.idea_value())
    for i, idea in enumerate(sorted_ideas, 1):
        print_idea_card(idea, i)
    print()

def cmd_view(idea_id: str):
    idea = find_idea(idea_id)
    if not idea:
        print(red(f"\n  Idea '{idea_id}' not found.\n"))
        return
    header(f"IDEA DETAIL: {idea.id}")
    print_idea_summary(idea)

def cmd_pivot(idea_id: str):
    idea = find_idea(idea_id)
    if not idea: return
    dom_cfg = get_domain(idea.domain)
    print(f"\n  Pivoting {b(idea.name)} ({dom_cfg['label']})")
    dims = list(dom_cfg["dimensions"].keys())
    for i, k in enumerate(dims, 1):
        print(f"    {i}. {dom_cfg['dimensions'][k]['name']}")
    choice = ask("Select dimension to re-score")
    if not choice.isdigit(): return
    idx = int(choice) - 1
    if not (0 <= idx < len(dims)): return
    dim_key = dims[idx]
    old_score = idea.scores.get(dim_key, 0)
    new_val = ask_score(dom_cfg["dimensions"][dim_key])
    weight = float(ask("Weight (0.0 to 1.0)", "0.5"))
    updated_score = (1 - weight) * old_score + weight * new_val
    idea.scores[dim_key] = round(updated_score, 2)
    idea.compute_score()
    save_one(idea)
    print(grn(f"\n  ✔ Updated to {idea.scores[dim_key]}"))

def cmd_research(idea_id: str):
    idea = find_idea(idea_id)
    if not idea: return
    print(f"\n  Adding research notes for {b(idea.name)}...")
    lines = []
    while True:
        line = input("  > ");
        if not line: break
        lines.append(line)
    if lines:
        idea.research_notes = (idea.research_notes + "\n\n" + "\n".join(lines)).strip()
        save_one(idea)
        print(grn("  ✔ Research recorded.\n"))

def cmd_result(idea_id: str):
    idea = find_idea(idea_id)
    if not idea: return
    if not idea.test:
        idea.test = TestDesign(assumption=ask("Core Assumption"), test_method=ask("Minimum Test Method"), success_criteria=ask("Success Criteria"), failure_criteria=ask("Failure Criteria"), deadline=ask("Deadline"))
    res = ask("Test Result (pass/fail/pending)", "pass").lower()
    if res in ("pass", "fail", "pending"):
        idea.test.result = res if res != "pending" else None
        idea.test.result_notes = ask("Result Notes")
        idea.test.result_date = Idea(id="temp",name="",description="",domain="").created_at[:10]
        save_one(idea)
        print(grn(f"  ✔ Result recorded.\n"))

def cmd_execute(idea_id: str):
    idea = find_idea(idea_id)
    if not idea: return
    idea.executed = True
    idea.execution_notes = ask("Execution Notes")
    save_one(idea)
    print(grn(f"  ✔ Marked as EXECUTED.\n"))

def cmd_kill(idea_id: str):
    idea = find_idea(idea_id)
    if not idea: return
    idea.killed = True
    idea.kill_reason = ask("Reason for killing")
    save_one(idea)
    print(red(f"  ☠  Idea '{idea.id}' killed.\n"))

def cmd_report():
    header("PORTFOLIO REPORT")
    ideas = load_all()
    if not ideas: return
    active = [i for i in ideas.values() if not i.killed]
    gh_summary = ""
    try:
        ins_fn, _, _, _, _ = _graph_module()
        ins = ins_fn(ideas)
        gh = ins["graph_health"]
        gc = grn if gh["grade"] in ("A","B") else (ylw if gh["grade"] in ("C","D") else red)
        gh_summary = f" | Graph Health: {gc(b(str(gh['graph_health'])+'/100 '+gh['grade']))}"
    except: pass
    section("Pipeline Stats")
    print(f"    Total: {b(len(ideas))} | Active: {grn(len(active))} | Killed: {red(sum(1 for i in ideas.values() if i.killed))}{gh_summary}")
    section("Highest Scorer")
    valued = sorted(active, key=lambda x: -x.idea_value())
    for i in valued[:5]:
        val = int(i.idea_value())
        col = grn if val > 40 else (ylw if val > 0 else dim)
        print(f"    {col(str(val).rjust(3))}  {b(i.name[:40].ljust(40))} [{i.domain}]")
    print()

def cmd_domains():
    header("ADAPTIVE DOMAINS")
    for k, label, desc in list_domains():
        print(f"  {b(label.ljust(25))} ({k})\n  {dim(desc)}\n")

# ── GRAPH COMMANDS ───────────────────────────────────────────────────────────

def cmd_graph(export_html=False):
    insights_fn, _, gap_fn, _, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas found. Add some first.\n"))
        return
    header("PORTFOLIO GRAPH ANALYSIS")
    print("  Loading graph", end="", flush=True)
    insights = insights_fn(ideas)
    print(f"\r  {grn('✔')} Graph built: {insights['total_ideas']} ideas\n")
    gh = insights["graph_health"]
    grade_color = {"A": grn, "B": grn, "C": ylw, "D": ylw, "F": red}.get(gh["grade"], ylw)
    section("Portfolio Graph Health")
    print(f"    Score        : {grade_color(b(str(gh['graph_health']))+'/'+'100')} {grade_color(b(gh['grade']))}")
    print(f"    Connectivity : {gh['connectivity']:.1f}/25")
    print(f"    Community    : {gh['community_score']:.1f}/25")
    print(f"    Diversity    : {gh['diversity']:.1f}/15")
    print(f"    Small-world  : {gh['small_world']:.3f}")
    print(f"    Modularity   : {gh['modularity']:.3f}")
    print(f"    Bridges      : {gh['n_bridges']}\n")
    print(f"    {dim(gh['interpretation'])}")
    if insights.get("health_advice"):
        print(f"\n    {b('Top improvements:')}")
        for adv in insights["health_advice"][:3]:
            pc = red if adv["priority"] == "HIGH" else (ylw if adv["priority"] == "MEDIUM" else cyn)
            print(f"    [{pc(adv['priority'])}] {adv['area'].upper()}: {adv['issue']}\n           → {adv['action']}")
    section("Most Influential Ideas (PageRank)")
    for i, t in enumerate(insights["top_ideas"], 1):
        ic = grn if t["iv"] > 0 else red
        print(f"    {b(str(i)+'.'):<4} {b(t['name'][:36].ljust(36))} PR={cyn(f'{t['pagerank']:.4f}')} IV={ic(b(str(t['iv'])))} [{t['domain']}]")
    section("Community Clusters")
    for c in insights["clusters"]:
        print(f"    Cluster {c['community_id']} ({c['size']} ideas) [{cyn(' + '.join(c['domains'][:3]))}]")
        for m in c["members"][:3]:
            ivc = grn if m["iv"] > 0 else dim
            print(f"      → {m['name'][:40].ljust(40)} IV={ivc(str(m['iv']))}")
    section("Domain Gaps")
    gap = gap_fn(ideas)
    if gap["covered_count"] == 13: print(f"    {grn('✔')} All 13 domains covered.")
    else:
        print(f"    {red(str(gap['absent_count']))} domains absent | {ylw(str(gap.get('untested_count', 0)))} untested | {grn(str(gap['covered_count']))} covered\n")
        for r in gap["by_domain"]:
            if r["status"] == "ABSENT": print(f"    {red('✗')} {b(r['label'][:24].ljust(24))} {dim(r['action'])}")
            elif r["status"] in ("UNTESTED", "THIN"): print(f"    {ylw('~')} {r['label'][:24].ljust(24)} [{r['status']}] {dim(r['action'])}")
    section("Graph Think — What the Portfolio Needs")
    print(f"    {insights['think_insight']}\n")
    if insights["think_bridges"]:
        print(f"    {b('Top bridge proposals:')}")
        for br in insights["think_bridges"]:
            bt = grn("CONNECT") if br["type"] == "connection" else cyn("PROPOSE")
            print(f"    [{bt}] \"{b(br.get('proposed_concept', br.get('concept')))}\"\n             bridges {br['anchor_a']} ↔ {br['anchor_b']}")
    if insights.get("critical_bridges"):
        section("Critical Bridge Ideas")
        print(dim("    Removing these would disconnect segments of the portfolio graph.\n"))
        for br in insights["critical_bridges"][:3]:
            print(f"    {red('⚡')} {b(br['name'][:40].ljust(40))} [{br['domain']}]")
    if insights.get("duplicate_pairs"):
        section("Potential Redundancy")
        for dup in insights["duplicate_pairs"]:
            print(f"    {ylw('~')} {dup['idea_a'][:30]} ↔ {dup['idea_b'][:30]} (sim={dup['similarity']:.3f})")
    print()
    if export_html: cmd_export()

def cmd_propose(domain_filter: str = None):
    _, prop_fn, _, _, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet.\n"))
        return
    header("PROPOSE NEW IDEAS")
    print(dim("  The graph finds structural gaps in your portfolio.\n"))
    for i, p in enumerate(prop_fn(ideas, domain=domain_filter, k=6), 1):
        bt = grn("WIRE") if p["type"] == "connection" else cyn("NEW")
        print(f"  {b(str(i)+'.')} [{bt}] {b(p['concept'])}\n       Domain  : {cyn(p['domain_label'])}\n       Bridges : {p['anchor_a']} ↔ {p['anchor_b']}\n       Score   : {p['bridge_score']:.3f}\n       Why     : {dim(p['rationale'])}\n")

def cmd_topology():
    inf_fn, _, gap_fn, _, _ = _graph_module()
    ideas = load_all()
    if not ideas:
        print(ylw("\n  No ideas yet.\n"))
        return
    ins = inf_fn(ideas)
    header("PORTFOLIO TOPOLOGY")
    section("Metrics")
    gh = ins["graph_health"]
    for k, v in [("Health", f"{gh['graph_health']}/100 {gh['grade']}"), ("Connectivity", f"{gh['connectivity']:.1f}"), ("Community", f"{gh['community_score']:.1f}"), ("Diversity", f"{gh['diversity']:.1f}")]:
        print(f"    {k.ljust(15)}: {b(v)}")
    section("Domain Status")
    gap = gap_fn(ideas)
    for r in gap["by_domain"]:
        col = grn if r["status"] == "COVERED" else (ylw if r["status"] in ("THIN","UNTESTED") else red)
        print(f"    {col(r['status'].ljust(12))} {r['label'].ljust(25)} {r['count']} ideas")
    section("Influence Ranking")
    for i, t in enumerate(ins["top_ideas"], 1):
        print(f"    {i}. {t['name'][:40].ljust(40)} PR={t['pagerank']:.5f} IV={t['iv']}")

def cmd_connect(ida: str, idb: str):
    _, _, _, path_fn, _ = _graph_module()
    ideas = load_all()
    header(f"PATH: {ida} → {idb}")
    res = path_fn(ideas, ida, idb)
    if not res["found"]: print(red("  No path found.\n")); return
    print(f"  {grn('Path found')} | length {res['length']} | cost {res['total_cost']:.3f}\n")
    for i, h in enumerate(res["hops"]):
        reason = f" {dim('['+h['reason']+']')}" if h.get("reason") else ""
        print(f"  {'START' if i==0 else '   ↓ '} {b(h['label'].ljust(40))} [{h['domain']}] IV={h['iv']}{reason}")
    print(f"\n  {dim(res['explanation'])}\n")

def cmd_export():
    _, _, _, _, sync_fn = _graph_module()
    ideas = load_all()
    g, _ = sync_fn(ideas)
    nodes = [{"id": n.id, "label": n.label, "group": n.node_type, "value": n.importance} for n in g._nodes.values()]
    edges = [{"from": e.from_id, "to": e.to_id, "value": e.strength} for e in g._edges]
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Idea Lab Portfolio Graph</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #mynetwork {{ width: 100%; height: 800px; border: 1px solid lightgray; background: #222; }}
        body {{ font-family: sans-serif; background: #111; color: #eee; }}
    </style>
</head>
<body>
    <h2 style="padding: 20px;">Idea Lab Portfolio Graph</h2>
    <div id="mynetwork"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{ shape: 'dot', font: {{ color: '#eee', size: 14 }} }},
            edges: {{ color: {{ inherit: 'from' }}, opacity: 0.5 }},
            groups: {{
                meta: {{ color: {{ background: '#96c', border: '#74a' }}, size: 40 }},
                active: {{ color: {{ background: '#4c4', border: '#2a2' }}, size: 30 }},
                potential: {{ color: {{ background: '#888', border: '#666' }}, size: 20 }},
                child: {{ color: {{ background: '#49c', border: '#27a' }}, size: 20 }}
            }},
            physics: {{ forceAtlas2Based: {{ gravitationalConstant: -50, centralGravity: 0.01, springLength: 100, springConstant: 0.08 }}, maxVelocity: 50, solver: 'forceAtlas2Based', stabilization: {{ iterations: 150 }} }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""
    with open("portfolio_graph.html", "w") as f: f.write(html)
    print(grn(f"\n  ✔ Exported to portfolio_graph.html\n"))

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd  = args[0].lower() if args else ""
    dispatch = {"new": cmd_new, "list": cmd_list, "report": cmd_report, "domains": cmd_domains, "graph": lambda: cmd_graph("--export" in args), "propose": lambda: cmd_propose(args[1] if len(args) > 1 else None), "topology": cmd_topology}
    if cmd in dispatch: dispatch[cmd]()
    elif cmd == "view" and len(args) > 1: cmd_view(args[1])
    elif cmd == "pivot" and len(args) > 1: cmd_pivot(args[1])
    elif cmd == "research" and len(args) > 1: cmd_research(args[1])
    elif cmd == "result" and len(args) > 1: cmd_result(args[1])
    elif cmd == "execute" and len(args) > 1: cmd_execute(args[1])
    elif cmd == "kill" and len(args) > 1: cmd_kill(args[1])
    elif cmd == "connect" and len(args) > 2: cmd_connect(args[1], args[2])
    else: cmd_menu()
