# IDEA LAB — Multi-Domain Benchmarking System

Idea Lab is a high-precision framework for evaluating, stress-testing, and executing ideas across 13 distinct domains. It enforces the principle: **an idea is worth zero until tested positive and executed.**

## 🧪 Core Principle: The IdeaValue Formula

The system uses a non-linear, multiplicative formula to calculate real-world value:

```
IdeaValue = (d1 × d2 × d3) × (d4 + d5 + d6) × test_passed × executed
```

- **Group A (Multiplied)**: Foundational dimensions (Precision, Validity, Falsifiability). If any score is 0, the entire value collapses to 0.
- **Group B (Summed)**: Scale and Fit dimensions (Reach, Resistance, Authority). These provide the magnitude of value.
- **T & E (Binary/Multiplier)**: Value remains 0 until a minimum test is passed and the idea is marked as executed.

### Scaling Factor
The formula uses a **16× scaling factor**. Doubling all dimension scores (from 1 to 2) increases the potential value from 3 to 48.

## 🔄 Recursive Weighted Pivots
Unlike static scoring systems, Idea Lab supports iterative refinement through **Recursive Weighted Pivots**. When updating a dimension, you can specify a **Weight of Evidence (w)**:

`NewScore = (1 - w) * OldScore + w * InputScore`

This allows for granular confidence building as research deepens.

## 🎓 Knowledgeable Status
Ideas mature through four stages of "Knowledgeable Status":
1. **UNRESEARCHED**: Default state.
2. **EXPLORING**: Research notes recorded.
3. **KNOWLEDGEABLE**: Significant research (>100 words) or passed test.
4. **EXPERT**: Idea fully executed.

## 🛠 Usage

```bash
python3 idea_lab.py new         # Benchmark a new idea
python3 idea_lab.py list        # List all ideas
python3 idea_lab.py view <id>   # Detailed view of an idea
python3 idea_lab.py pivot <id>  # Refine a dimension with weighted input
python3 idea_lab.py research <id> # Record deep research findings
python3 idea_lab.py report      # Portfolio performance and weaknesses
```

## 🏗 Supported Domains (13)
- Deep Research
- Question / Answer
- Methodology
- Project
- Law / Policy
- Mathematics
- Scientific Hypothesis
- Philosophy / Argument
- Business / Startup
- Educational Concept
- Technology / Engineering
- Social / Behavioral
- Creative / Artistic

## 🛡 System Integrity
The system includes a robust stress test suite covering 69 edge cases, performance benchmarks, and formula boundary conditions.
Run tests: `python3 "stress_test (1).py"`
