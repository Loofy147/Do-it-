"""
idea_graph.py — Bridge between Idea Lab and ThoughtGraph

The portfolio of ideas IS a knowledge graph.
Every idea is a node. Domain affinity creates edges.
Cross-references create bridges. Think() finds blind spots.

This module provides:
  sync_to_graph()         — Load all ideas into a ThoughtGraph
  portfolio_insights()    — Graph topology → portfolio analysis
  propose_ideas()         — think() → new Idea candidates by domain
  domain_gap_report()     — Which domains are under-represented?
  path_between_ideas()    — How two ideas connect through the portfolio
  duplicate_ideas()       — Redundant ideas to kill or merge
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from thought_graph import ThoughtGraph, make_embedding
import numpy as np
from collections import defaultdict, Counter

# ── DOMAIN → NODE TYPE MAPPING ──────────────────────────────────────────────
# deep_research and philosophy are meta-level — they govern other domains
# technology / methodology are active — they produce things
# everything else is active or child based on knowledge_status

DOMAIN_NODE_TYPE = {
    "deep_research": "meta",
    "philosophy":    "meta",
    "methodology":   "active",
    "technology":    "active",
    "science":       "active",
    "business":      "active",
    "qa":            "child",
    "mathematics":   "child",
    "education":     "child",
    "law":           "active",
    "social":        "child",
    "creative":      "child",
    "project":       "child",
}

# Domains whose ideas should be strongly connected (intellectual siblings)
DOMAIN_AFFINITY = {
    "philosophy":    ["methodology", "deep_research", "science"],
    "methodology":   ["philosophy", "technology", "education"],
    "technology":    ["methodology", "science", "project"],
    "science":       ["mathematics", "technology", "deep_research"],
    "mathematics":   ["science", "philosophy"],
    "business":      ["social", "technology", "project"],
    "education":     ["social", "methodology"],
    "law":           ["philosophy", "social", "business"],
    "social":        ["education", "business", "law"],
    "deep_research": ["philosophy", "science", "methodology"],
    "qa":            ["methodology", "deep_research"],
    "creative":      ["education", "social"],
    "project":       ["technology", "business", "methodology"],
}


def idea_importance(idea) -> float:
    """
    Map IdeaValue and total_score to ThoughtGraph importance [0.5 → 5.0].
    High-value executed ideas get max importance.
    Killed ideas get 0.3 (ghost nodes — still useful structurally).
    """
    if idea.killed:
        return 0.3
    iv = idea.idea_value()
    if iv >= 40:
        return 5.0
    if iv > 0:
        return 1.0 + (iv / 48.0) * 4.0
    # Tested or partially known ideas get partial weight
    if idea.test and idea.test.result == "pass":
        return 1.5
    if idea.total_score >= 10:
        return 1.2
    return 0.6 + (idea.total_score / 12.0) * 0.8


def idea_node_type(idea) -> str:
    """
    Map Idea state to ThoughtGraph node type.
    Executed + value → active
    Killed → potential (grayed out but still connected)
    Strong score, not yet executed → active
    Low score → potential
    """
    if idea.killed:
        return "potential"
    if idea.executed and idea.idea_value() > 0:
        return DOMAIN_NODE_TYPE.get(idea.domain, "active")
    if idea.verdict == "STRONG":
        return "active"
    if idea.verdict == "CONDITIONAL":
        return "child"
    return "potential"


def sync_to_graph(ideas: dict, g: ThoughtGraph = None) -> tuple:
    """
    Load all Idea Lab entries into a ThoughtGraph.

    Returns (graph, node_map) where node_map = {idea_id: node_id}
    """
    if g is None:
        g = ThoughtGraph(persist=False)

    node_map = {}   # idea_id → ThoughtNode.id
    domain_nodes = defaultdict(list)  # domain → [node_ids]

    # ── Pass 1: Add all idea nodes ───────────────────────────────────────
    for idea_id, idea in ideas.items():
        importance = idea_importance(idea)
        ntype      = idea_node_type(idea)

        tags = [
            idea.domain,
            idea.knowledge_status,
            idea.verdict,
            f"score:{idea.total_score:.0f}",
            f"iv:{int(idea.idea_value())}",
        ]
        if idea.killed:
            tags.append("killed")
        if idea.executed:
            tags.append("executed")

        node = g.add_node(
            label      = idea.name,
            node_type  = ntype,
            importance = importance,
            tags       = tags,
            origin     = "idea_lab",
        )
        node_map[idea_id] = node.id
        domain_nodes[idea.domain].append((idea_id, node.id, idea))

    # ── Pass 2: Same-domain edges ────────────────────────────────────────
    for domain, entries in domain_nodes.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                _, na, ia = entries[i]
                _, nb, ib = entries[j]
                # Stronger edge if both are executed and valuable
                both_valuable = ia.idea_value() > 0 and ib.idea_value() > 0
                strength = 0.75 if both_valuable else 0.55
                g.connect(na, nb, strength=strength, edge_type="connection")

    # ── Pass 3: Cross-domain affinity edges ─────────────────────────────
    # Connect the highest-PR node of each domain to highest-PR of affiliated domains
    domain_anchors = {}
    for domain, entries in domain_nodes.items():
        if entries:
            # Best idea in domain = highest idea_value, then score
            best = max(entries, key=lambda e: (e[2].idea_value(), e[2].total_score))
            domain_anchors[domain] = best[1]   # node_id of anchor

    for domain, affiliates in DOMAIN_AFFINITY.items():
        if domain not in domain_anchors:
            continue
        for aff in affiliates:
            if aff in domain_anchors:
                g.connect(
                    domain_anchors[domain],
                    domain_anchors[aff],
                    strength=0.50,
                    edge_type="connection",
                )

    # ── Pass 4: Explicit cross-idea references (semantic) ───────────────
    # Find pairs of ideas from different domains that are semantically close
    all_nodes_in_map = [(idea_id, node_map[idea_id], ideas[idea_id])
                        for idea_id in ideas]
    if len(all_nodes_in_map) >= 2:
        embs = np.array([
            g.get_node(n).embedding
            for _, n, _ in all_nodes_in_map
        ], dtype=np.float32)
        sim_matrix = (embs @ embs.T + 1) / 2

        for i, (ai, an, ia) in enumerate(all_nodes_in_map):
            for j, (bi, bn, ib) in enumerate(all_nodes_in_map):
                if i >= j:
                    continue
                if ia.domain == ib.domain:
                    continue   # already connected
                sim = float(sim_matrix[i, j])
                if sim > 0.72:
                    g.connect(an, bn, strength=round(sim - 0.3, 2), edge_type="connection")

    g._topo_dirty = True
    g.record_snapshot()
    return g, node_map


def portfolio_insights(ideas: dict) -> dict:
    """
    Use ThoughtGraph topology to analyze the idea portfolio.
    Returns a rich insight dict with actionable findings.
    """
    g, node_map = sync_to_graph(ideas)
    reverse_map = {v: k for k, v in node_map.items()}   # node_id → idea_id

    topo    = g.get_topology()
    pr      = topo["pagerank"]
    coms    = topo["communities"]
    a       = g.graph_analytics()
    h       = g.graph_health_score()
    advice  = g.graph_health_advice()
    thought = g.think(k_bridges=5)
    bridges = g.find_bridges()
    recs    = g.recommend_exploration(k=5)

    # ── Most influential ideas (by PageRank) ─────────────────────────────
    ranked = sorted(
        [(idea_id, pr.get(node_map[idea_id], 0)) for idea_id in node_map],
        key=lambda x: -x[1]
    )
    top_ideas = []
    for idea_id, pagerank in ranked[:5]:
        idea = ideas.get(idea_id)
        if idea:
            top_ideas.append({
                "id":       idea_id,
                "name":     idea.name,
                "domain":   idea.domain,
                "pagerank": round(pagerank, 4),
                "iv":       int(idea.idea_value()),
                "verdict":  idea.verdict,
            })

    # ── Community clusters (which ideas group together?) ─────────────────
    com_groups = defaultdict(list)
    for idea_id, node_id in node_map.items():
        cid = coms.get(node_id, -1)
        idea = ideas.get(idea_id)
        if idea and cid >= 0:
            com_groups[cid].append({
                "id":     idea_id,
                "name":   idea.name,
                "domain": idea.domain,
                "iv":     int(idea.idea_value()),
            })

    clusters = []
    for cid, members in sorted(com_groups.items()):
        domains_in_cluster = list(set(m["domain"] for m in members))
        clusters.append({
            "community_id": cid,
            "size":         len(members),
            "domains":      domains_in_cluster,
            "members":      sorted(members, key=lambda m: -m["iv"])[:4],
            "label":        ", ".join(domains_in_cluster[:2]),
        })
    clusters.sort(key=lambda c: -c["size"])

    # ── Domain gaps (which domains have no ideas?) ───────────────────────
    all_domains = set(DOMAIN_NODE_TYPE.keys())
    covered     = set(ideas[iid].domain for iid in ideas if not ideas[iid].killed)
    gaps        = all_domains - covered
    weak        = [
        d for d in covered
        if sum(1 for iid in ideas if ideas[iid].domain == d and ideas[iid].idea_value() > 0) == 0
    ]

    # ── Critical bridges (ideas whose removal would disconnect the graph) ─
    critical = []
    for b in bridges[:5]:
        for idea_id, node_id in node_map.items():
            if node_id in (b["from_id"], b["to_id"]):
                idea = ideas.get(idea_id)
                if idea and not any(c["id"] == idea_id for c in critical):
                    critical.append({
                        "id":     idea_id,
                        "name":   idea.name,
                        "domain": idea.domain,
                    })

    # ── Duplicate / redundant ideas ──────────────────────────────────────
    dups = g.find_duplicates(threshold=0.82)
    dup_pairs = []
    for d in dups[:5]:
        a_idea_id = reverse_map.get(d["node_a_id"])
        b_idea_id = reverse_map.get(d["node_b_id"])
        if a_idea_id and b_idea_id:
            dup_pairs.append({
                "idea_a": ideas[a_idea_id].name if a_idea_id in ideas else d["node_a_label"],
                "idea_b": ideas[b_idea_id].name if b_idea_id in ideas else d["node_b_label"],
                "similarity": d["similarity"],
                "recommendation": d["recommendation"],
            })

    # ── Portfolio health mapping ──────────────────────────────────────────
    health_map = {
        "graph_health":    round(h["score"], 1),
        "grade":           h["grade"],
        "connectivity":    round(h["breakdown"].get("connectivity", 0), 1),
        "community_score": round(h["breakdown"].get("community", 0), 1),
        "diversity":       round(h["breakdown"].get("diversity", 0), 1),
        "small_world":     round(a.get("small_world_index", 0), 3),
        "modularity":      round(a.get("modularity", 0), 3),
        "n_bridges":       a.get("n_bridges", 0),
        "interpretation":  (
            "Portfolio is well-connected with diverse domains — "
            if h["grade"] in ("A", "B") else
            "Portfolio has structural gaps — ideas are siloed — "
        ) + f"health {h['score']:.0f}/100",
    }

    return {
        "graph_health":     health_map,
        "top_ideas":        top_ideas,
        "clusters":         clusters,
        "domain_gaps":      sorted(gaps),
        "weak_domains":     weak,
        "critical_bridges": critical,
        "duplicate_pairs":  dup_pairs,
        "think_insight":    thought.get("insight", ""),
        "think_bridges":    thought.get("bridges", [])[:3],
        "health_advice":    advice[:3],
        "total_ideas":      len(ideas),
        "active_ideas":     sum(1 for i in ideas.values() if not i.killed),
        "executed_ideas":   sum(1 for i in ideas.values() if i.executed),
        "value_ideas":      sum(1 for i in ideas.values() if i.idea_value() > 0),
    }


def propose_ideas(ideas: dict, domain: str = None, k: int = 5) -> list:
    """
    Use ThoughtGraph's think() to propose new Idea Lab candidates.

    If domain is specified: bias proposals toward that domain.
    Returns list of {concept, domain, rationale, bridge_score}.
    """
    from domains import DOMAINS, get_domain

    g, node_map = sync_to_graph(ideas)
    thought     = g.think(k_bridges=k * 2)
    all_domains = list(DOMAINS.keys())

    proposals = []

    for bridge in thought.get("bridges", []):
        concept = bridge["proposed_concept"]
        anchor_a = bridge["anchor_a"]
        anchor_b = bridge["anchor_b"]

        # Guess which domain this concept belongs in
        # by finding highest semantic similarity to domain anchor ideas
        concept_emb = np.array(make_embedding(concept), dtype=np.float32)
        best_domain = "methodology"   # default
        best_sim    = -1.0

        for d in all_domains:
            domain_ideas = [
                i for i in ideas.values()
                if i.domain == d and not i.killed
            ]
            if not domain_ideas:
                continue
            d_embs = np.array([make_embedding(i.name) for i in domain_ideas], dtype=np.float32)
            sims   = (d_embs @ concept_emb + 1) / 2
            mean_s = float(sims.mean())
            if mean_s > best_sim:
                best_sim    = mean_s
                best_domain = d

        if domain and best_domain != domain:
            # Force domain if caller specified
            best_domain = domain

        dom_cfg = get_domain(best_domain)
        proposals.append({
            "concept":      concept,
            "domain":       best_domain,
            "domain_label": dom_cfg["label"],
            "idea_noun":    dom_cfg["idea_noun"],
            "bridge_score": bridge["bridge_score"],
            "anchor_a":     anchor_a,
            "anchor_b":     anchor_b,
            "rationale":    (
                f"Bridges '{anchor_a}' and '{anchor_b}' (score {bridge['bridge_score']:.3f}). "
                f"Best domain fit: {dom_cfg['label']} "
                f"(semantic similarity {best_sim:.3f})."
            ),
            "type":         bridge.get("type", "proposal"),
        })

    # Deduplicate and limit
    seen = set()
    unique = []
    for p in proposals:
        if p["concept"] not in seen:
            seen.add(p["concept"])
            unique.append(p)
        if len(unique) >= k:
            break

    return unique


def domain_gap_report(ideas: dict) -> dict:
    """
    Identify which domains are missing, weak, or untested.
    Returns actionable priority list.
    """
    from domains import DOMAINS

    covered  = defaultdict(list)   # domain → [ideas]
    for iid, idea in ideas.items():
        covered[idea.domain].append(idea)

    all_domains = list(DOMAINS.keys())
    report = []

    for domain in all_domains:
        dom_ideas  = covered.get(domain, [])
        active     = [i for i in dom_ideas if not i.killed]
        executed   = [i for i in active if i.executed]
        with_value = [i for i in active if i.idea_value() > 0]

        if not dom_ideas:
            status = "ABSENT"
            priority = 1
        elif not active:
            status = "ALL_KILLED"
            priority = 2
        elif not with_value:
            status = "UNTESTED"
            priority = 3
        elif len(active) == 1:
            status = "THIN"
            priority = 4
        else:
            status = "COVERED"
            priority = 5

        report.append({
            "domain":      domain,
            "label":       DOMAINS[domain]["label"],
            "status":      status,
            "priority":    priority,
            "count":       len(active),
            "executed":    len(executed),
            "value_ideas": len(with_value),
            "action":      {
                "ABSENT":     f"No ideas yet. Add your first {DOMAINS[domain]['idea_noun']}.",
                "ALL_KILLED": "All ideas killed. Worth revisiting with new angle.",
                "UNTESTED":   "Ideas exist but none tested. Run your MVT.",
                "THIN":       "Only one idea. Add diversity or depth.",
                "COVERED":    "Healthy coverage.",
            }.get(status, ""),
        })

    report.sort(key=lambda r: r["priority"])
    return {
        "by_domain":      report,
        "absent_count":   sum(1 for r in report if r["status"] == "ABSENT"),
        "untested_count": sum(1 for r in report if r["status"] == "UNTESTED"),
        "covered_count":  sum(1 for r in report if r["status"] == "COVERED"),
    }


def path_between_ideas(ideas: dict, idea_id_a: str, idea_id_b: str) -> dict:
    """
    Use Dijkstra on the idea graph to find the conceptual path between two ideas.
    """
    g, node_map = sync_to_graph(ideas)
    reverse     = {v: k for k, v in node_map.items()}

    na = node_map.get(idea_id_a)
    nb = node_map.get(idea_id_b)
    if not na or not nb:
        return {"found": False, "error": "One or both idea IDs not found"}

    result = g.concept_path(na, nb)
    if not result["found"]:
        return {"found": False, "length": -1, "hops": []}

    # Annotate hops with idea data
    hops = []
    for hop in result["hops"]:
        idea_id = reverse.get(hop["node_id"])
        idea    = ideas.get(idea_id) if idea_id else None
        hops.append({
            "node_id":    hop["node_id"],
            "label":      hop["label"],
            "domain":     ideas[idea_id].domain if idea else "unknown",
            "iv":         int(ideas[idea_id].idea_value()) if idea else 0,
            "edge_strength": hop.get("edge_strength"),
            "semantic_sim":  hop.get("semantic_sim"),
        })

    return {
        "found":       True,
        "length":      result["length"],
        "hops":        hops,
        "total_cost":  result["total_cost"],
        "explanation": " → ".join(h["label"] for h in hops),
    }
