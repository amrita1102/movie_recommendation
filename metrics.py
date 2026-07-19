from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "requests_total",
    "Total API Requests"
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Recommendation request latency"
)

EMBEDDING_CACHE_HITS = Counter(
    "embedding_cache_hits_total",
    "Embedding Cache Hits"
)

EMBEDDING_CACHE_MISSES = Counter(
    "embedding_cache_misses_total",
    "Embedding Cache Misses"
)

RECOMMENDATION_CACHE_HITS = Counter(
    "recommendation_cache_hits_total",
    "Recommendation Cache Hits"
)

RECOMMENDATION_CACHE_MISSES = Counter(
    "recommendation_cache_misses_total",
    "Recommendation Cache Misses"
)

FAISS_SEARCHES = Counter(
    "faiss_searches_total",
    "Number of FAISS Searches"
)