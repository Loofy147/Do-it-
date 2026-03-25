# IDEA LAB v2 — Benchmarking + ThoughtGraph

Idea Lab is a high-precision framework for evaluating and executing ideas across 13 distinct domains. It enforces the principle: **an idea is worth zero until tested positive and executed.**

v2 introduces the **ThoughtGraph Merger**: a natural integration between structured benchmarking and topological analysis. While the original system scored individual ideas, ThoughtGraph reveals the structure, influence, and gaps of the entire portfolio.

## 🧪 The IdeaValue Formula
Value is calculated using a non-linear, multiplicative formula:
`IdeaValue = (d1 × d2 × d3) × (d4 + d5 + d6) × test_passed × executed`
This corrects for "Good Idea, No Market" or "Good Idea, No Skill" failure modes by making foundational dimensions multiplicative.

## 🧠 ThoughtGraph Integration
The two systems complement each other exactly: Idea Lab tells you whether an idea is worth pursuing; ThoughtGraph tells you how your ideas relate, what's missing, and what to pursue next.

- **Portfolio Topology**: View your ideas as a knowledge graph where PageRank reveals structural load-bearers.
- **Community Clustering**: Louvain algorithm groups ideas by semantic and domain affinity.
- **Domain Gap Detection**: Automatically identifies absent domains in your portfolio.
- **Graph Think**: The graph reasons about structural gaps and proposes new bridge candidates.

## 🔄 Recursive Weighted Pivots
Refine scores as research deepens: `NewScore = (1 - w) * OldScore + w * InputScore`. Prevent knee-jerk changes from single pieces of evidence.

## 🛠 Usage

```bash
# BENCHMARKING
python3 idea_lab.py new          # New idea benchmark
python3 idea_lab.py list         # List all ideas
python3 idea_lab.py pivot <id>   # Weighted refinement
python3 idea_lab.py report       # Portfolio performance

# TOPOLOGY
python3 idea_lab.py graph        # Portfolio topology + insights
python3 idea_lab.py graph --export # Generate HTML visualizer
python3 idea_lab.py propose      # Graph reasons about new ideas
python3 idea_lab.py topology     # Full numeric metrics
python3 idea_lab.py connect <a> <b> # Conceptual path tracing
```

## 🛡 System Integrity
Includes a 69-test stress suite covering integrity, formula boundaries, and performance.
Run tests: `python3 "stress_test (1).py"`
