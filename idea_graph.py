"""
idea_graph.py — Bridge between Idea Lab and ThoughtGraph

The portfolio of ideas IS a knowledge graph.
Every idea is a node. Domain affinity creates edges.
Cross-references create bridges. Think() finds blind spots.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from thought_graph import ThoughtGraph, make_embedding
import numpy as np
from collections import defaultdict, Counter

DOMAIN_NODE_TYPE = {
    "deep_research": "meta", "philosophy": "meta", "methodology": "active",
    "technology": "active", "science": "active", "business": "active",
    "qa": "child", "mathematics": "child", "education": "child",
    "law": "active", "social": "child", "creative": "child", "project": "child",
}

DOMAIN_AFFINITY = {
    "philosophy": ["methodology", "deep_research", "science"],
    "methodology": ["philosophy", "technology", "education"],
    "technology": ["methodology", "science", "project"],
    "science": ["mathematics", "technology", "deep_research"],
    "mathematics": ["science", "philosophy"],
    "business": ["social", "technology", "project"],
    "education": ["social", "methodology"],
    "law": ["philosophy", "social", "business"],
    "social": ["education", "business", "law"],
    "deep_research": ["philosophy", "science", "methodology"],
    "qa": ["methodology", "deep_research"],
    "creative": ["education", "social"],
    "project": ["technology", "business", "methodology"],
}

def idea_importance(idea) -> float:
    if idea.killed: return 0.3
    iv = idea.idea_value()
    if iv >= 40: return 5.0
    if iv > 0: return 1.0 + (iv / 48.0) * 4.0
    if idea.test and idea.test.result == "pass": return 1.5
    if idea.total_score >= 10: return 1.2
    return 0.6 + (idea.total_score / 12.0) * 0.8

def idea_node_type(idea) -> str:
    if idea.killed: return "potential"
    if idea.executed and idea.idea_value() > 0:
        return DOMAIN_NODE_TYPE.get(idea.domain, "active")
    if idea.verdict == "STRONG": return "active"
    if idea.verdict == "CONDITIONAL": return "child"
    return "potential"

def sync_to_graph(ideas: dict, g: ThoughtGraph = None) -> tuple:
    if g is None: g = ThoughtGraph(persist=False)
    node_map = {}
    domain_nodes = defaultdict(list)
    for idea_id, idea in ideas.items():
        node = g.add_node(
            label=idea.name, node_type=idea_node_type(idea),
            importance=idea_importance(idea),
            tags=[idea.domain, idea.knowledge_status, idea.verdict],
            origin="idea_lab",
        )
        node_map[idea_id] = node.id
        domain_nodes[idea.domain].append((idea_id, node.id, idea))

    for domain, entries in domain_nodes.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                _, na, ia = entries[i]; _, nb, ib = entries[j]
                strength = 0.75 if (ia.idea_value() > 0 and ib.idea_value() > 0) else 0.55
                g.connect(na, nb, strength=strength)

    domain_anchors = {d: max(e, key=lambda x: (x[2].idea_value(), x[2].total_score))[1] for d, e in domain_nodes.items() if e}

    # Connect affiliated domains
    for d, affs in DOMAIN_AFFINITY.items():
        if d in domain_anchors:
            for a in affs:
                if a in domain_anchors: g.connect(domain_anchors[d], domain_anchors[a], strength=0.50)

    all_nodes = list(node_map.items())
    if len(all_nodes) >= 2:
        embs = np.array([g.get_node(nid).embedding for _, nid in all_nodes], dtype=np.float32)
        sims = (embs @ embs.T + 1) / 2
        for i in range(len(all_nodes)):
            for j in range(i+1, len(all_nodes)):
                ida, nodea = all_nodes[i]; idb, nodeb = all_nodes[j]
                if ideas[ida].domain != ideas[idb].domain:
                    s = float(sims[i,j])
                    if s > 0.78: g.connect(nodea, nodeb, strength=round(s-0.2, 2))
    g._topo_dirty = True
    g.record_snapshot()
    return g, node_map

def portfolio_insights(ideas: dict) -> dict:
    g, node_map = sync_to_graph(ideas); rev = {v: k for k, v in node_map.items()}
    topo = g.get_topology(); h = g.graph_health_score(); a = g.graph_analytics()
    thought = g.think(k_bridges=12)

    top_ideas = [{"id":rev.get(nid), "name":ideas[rev[nid]].name, "pagerank":s, "iv":int(ideas[rev[nid]].idea_value()), "domain":ideas[rev[nid]].domain}
                 for nid, s in sorted(topo["pagerank"].items(), key=lambda x: -x[1])[:10] if rev.get(nid)]

    com_groups = defaultdict(list)
    for iid, nid in node_map.items():
        cid = topo["communities"].get(nid, -1)
        if cid >= 0: com_groups[cid].append({"name":ideas[iid].name, "domain":ideas[iid].domain, "iv":int(ideas[iid].idea_value())})

    clusters = [{"community_id":cid, "size":len(m), "domains":list(set(x["domain"] for x in m)), "members":sorted(m, key=lambda x: -x["iv"])[:4]}
                for cid, m in sorted(com_groups.items())]

    dups = []
    for d in g.find_duplicates(threshold=0.88):
        aid, bid = rev.get(d["node_a_id"]), rev.get(d["node_b_id"])
        if aid and bid: dups.append({"idea_a":ideas[aid].name, "idea_b":ideas[bid].name, "similarity":d["similarity"]})

    critical = []
    bridges = topo.get("bridges", [])
    if bridges:
        for u, v in bridges:
            for nid in (u, v):
                iid = rev.get(nid)
                if iid and not any(x["id"]==iid for x in critical):
                    critical.append({"id":iid, "name":ideas[iid].name, "domain":ideas[iid].domain})
    else:
        btw = topo.get("betweenness", {})
        sorted_btw = sorted(btw.items(), key=lambda x: -x[1])
        for nid, score in sorted_btw[:3]:
            iid = rev.get(nid)
            if iid and score > 0:
                critical.append({"id":iid, "name":ideas[iid].name, "domain":ideas[iid].domain})

    return {
        "graph_health": {"graph_health":h["score"], "grade":h["grade"], "connectivity":h["breakdown"].get("connectivity",0), "community_score":h["breakdown"].get("community",0), "diversity":h["breakdown"].get("diversity",0), "small_world":a.get("small_world_index",0), "modularity":a.get("modularity",0), "n_bridges":len(bridges), "interpretation":("Portfolio is well-connected — " if h["grade"] in ("A","B") else "Portfolio has structural gaps — ") + f"health {h['score']:.0f}/100"},
        "top_ideas": top_ideas, "clusters": clusters, "think_insight": thought.get("insight",""), "think_bridges": thought.get("bridges",[])[:3], "health_advice": g.graph_health_advice()[:3], "total_ideas": len(ideas), "active_ideas": sum(1 for i in ideas.values() if not i.killed), "executed_ideas": sum(1 for i in ideas.values() if i.executed), "value_ideas": sum(1 for i in ideas.values() if i.idea_value() > 0), "duplicate_pairs": dups, "critical_bridges": critical[:5]
    }

def propose_ideas(ideas: dict, domain: str = None, k: int = 5) -> list:
    from domains import DOMAINS, get_domain
    g, node_map = sync_to_graph(ideas); thought = g.think(k_bridges=k*2); proposals = []
    for br in thought.get("bridges", []):
        concept = br["proposed_concept"]; c_emb = np.array(make_embedding(concept), dtype=np.float32)
        best_d, best_s = "methodology", -1.0
        for d in DOMAINS.keys():
            d_ideas = [i for i in ideas.values() if i.domain == d and not i.killed]
            if not d_ideas: continue
            d_embs = np.array([make_embedding(i.name) for i in d_ideas], dtype=np.float32)
            mean_s = float(((d_embs @ c_emb + 1) / 2).mean())
            if mean_s > best_s: best_s, best_d = mean_s, d
        if domain: best_d = domain
        dom_cfg = get_domain(best_d)
        proposals.append({"concept":concept, "domain":best_d, "domain_label":dom_cfg["label"], "idea_noun":dom_cfg["idea_noun"], "bridge_score":br["bridge_score"], "anchor_a":br["anchor_a"], "anchor_b":br["anchor_b"], "rationale":f"Bridges '{br['anchor_a']}' and '{br['anchor_b']}'. Fit: {dom_cfg['label']} (sim={best_s:.3f}).", "type":br.get("type","proposal")})
    return proposals[:k]

def domain_gap_report(ideas: dict) -> dict:
    from domains import DOMAINS
    covered = defaultdict(list)
    for i in ideas.values(): covered[i.domain].append(i)
    report = []
    for d in DOMAINS.keys():
        active = [i for i in covered[d] if not i.killed]; val = [i for i in active if i.idea_value() > 0]
        status = "ABSENT" if not covered[d] else "ALL_KILLED" if not active else "UNTESTED" if not val else "THIN" if len(active) == 1 else "COVERED"
        report.append({"domain":d, "label":DOMAINS[d]["label"], "status":status, "count":len(active), "executed":sum(1 for i in active if i.executed), "value_ideas":len(val), "action":{"ABSENT":f"No ideas yet. Add {DOMAINS[d]['idea_noun']}.", "ALL_KILLED":"All killed. Revisit.", "UNTESTED":"Run MVT.", "THIN":"Add diversity.", "COVERED":"Healthy coverage."}[status]})
    return {"by_domain":sorted(report, key=lambda x: x["count"]), "absent_count":sum(1 for r in report if r["status"]=="ABSENT"), "untested_count":sum(1 for r in report if r["status"]=="UNTESTED"), "covered_count":sum(1 for r in report if r["status"]=="COVERED")}

def path_between_ideas(ideas: dict, ida: str, idb: str) -> dict:
    g, node_map = sync_to_graph(ideas); rev = {v: k for k, v in node_map.items()}
    na, nb = node_map.get(ida), node_map.get(idb)
    if na is None or nb is None: return {"found":False}
    res = g.concept_path(na, nb)
    if not res["found"]: return res
    hops = []
    for i, h in enumerate(res["hops"]):
        iid = rev.get(h["node_id"]); idea = ideas.get(iid)
        strength = h.get("edge_strength")
        reason = ""
        if i > 0:
            sim = h.get("semantic_sim", 0)
            if sim > 0.8: reason = f"Semantic similarity ({sim:.2f})"
            elif strength >= 0.7: reason = "Same domain synergy"
            elif strength >= 0.5: reason = "Domain affinity bridge"
            else: reason = "Weak exploratory link"
        hops.append({"label":h["label"], "domain":idea.domain if idea else "unknown", "iv":int(idea.idea_value()) if idea else 0, "edge_strength":strength, "reason":reason})
    return {"found":True, "length":res["length"], "hops":hops, "total_cost":res["total_cost"], "explanation":" → ".join(h["label"] for h in hops)}
