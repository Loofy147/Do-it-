
## 2026-03-06 - [Caching Hashing Embeddings]
**Learning:** The `make_embedding` function is a character n-gram hashing algorithm that is deterministic and frequently called with the same inputs (e.g., domain labels, bridge vocabulary, and idea names during graph building). By memoizing this function, we can reduce repeated O(N*K) computations to O(1) hash lookups.
**Action:** Use `functools.lru_cache` on deterministic embedding functions. Ensure return types are immutable (e.g., `tuple` instead of `list`) to satisfy `lru_cache` requirements and prevent accidental mutation of cached values.

## 2026-03-06 - [Optimizing Bridge Proposals]
**Learning:** Profiling revealed that `propose_ideas` was spending ~90% of its time in NetworkX's algebraic connectivity (Fiedler value) calculations, which are O(N^3) in the worst case and not required for semantic bridge generation. Additionally, redundant NumPy matrix allocations for domain affinity matching were adding O(B*D) overhead.
**Action:** Decouple expensive topological metrics from structural reasoning. Use optional flags to skip heavy metrics in cold paths. Pre-calculate lookup matrices for batch semantic comparisons to avoid O(N) allocation loops.
