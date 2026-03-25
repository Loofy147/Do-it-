
## 2026-03-06 - [Caching Hashing Embeddings]
**Learning:** The `make_embedding` function is a character n-gram hashing algorithm that is deterministic and frequently called with the same inputs (e.g., domain labels, bridge vocabulary, and idea names during graph building). By memoizing this function, we can reduce repeated O(N*K) computations to O(1) hash lookups.
**Action:** Use `functools.lru_cache` on deterministic embedding functions. Ensure return types are immutable (e.g., `tuple` instead of `list`) to satisfy `lru_cache` requirements and prevent accidental mutation of cached values.
