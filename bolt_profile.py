import cProfile
import pstats
from idea_graph import propose_ideas
from models import Idea

def profile_propose():
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

    profiler = cProfile.Profile()
    profiler.enable()
    propose_ideas(ideas, k=5)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats(20)

if __name__ == "__main__":
    profile_propose()
