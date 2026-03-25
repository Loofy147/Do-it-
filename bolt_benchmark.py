import time
from thought_graph import make_embedding
from idea_graph import propose_ideas
from models import Idea

def benchmark_make_embedding():
    print("Benchmarking make_embedding...")
    labels = ["AI Ethics", "Quantum Computing", "Sustainable Energy", "Space Exploration", "Biotechnology"] * 100

    start_time = time.time()
    for label in labels:
        make_embedding(label)
    end_time = time.time()

    print(f"Time taken for {len(labels)} calls (with repeats): {end_time - start_time:.4f} seconds")

def benchmark_propose_ideas():
    print("\nBenchmarking propose_ideas...")
    # Create 50 dummy ideas
    ideas = {}
    for i in range(50):
        iid = f"id_{i}"
        ideas[iid] = Idea(
            id=iid,
            name=f"Idea Number {i}",
            description=f"Description for idea {i}",
            domain="technology" if i % 2 == 0 else "business",
            scores={"problem_reality": 1, "market_readiness": 1, "technical_feasibility": 1,
                    "strategic_alignment": 1, "resource_availability": 1, "risk_level": 1}
        )
        ideas[iid].compute_score()

    start_time = time.time()
    propose_ideas(ideas, k=5)
    end_time = time.time()

    print(f"Time taken for propose_ideas with 50 ideas: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    benchmark_make_embedding()
    benchmark_propose_ideas()
