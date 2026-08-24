import numpy as np
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pickle
from redis_client import redis_client
from datetime import datetime
from logger import logger
import time
from history_repository import history_repository
from watch_repository import watch_repository
from metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    EMBEDDING_CACHE_HITS,
    EMBEDDING_CACHE_MISSES,
    RECOMMENDATION_CACHE_HITS,
    RECOMMENDATION_CACHE_MISSES,
    FAISS_SEARCHES
)
from datastore import data_store
movies = data_store.movies
# movies = pd.read_csv("movies.csv")

EMBEDDING_TTL = 600
RECOMMENDATION_TTL = 90

# history = pd.read_csv("user_history.csv")

# history["timestamp"] = pd.to_datetime(
#     history["timestamp"]
# )

# embeddings = np.load(
#     "movie_embeddings.npy"
# ).astype("float32")
embeddings = data_store.embeddings
faiss.normalize_L2(
    embeddings
)
index = data_store.index
# index = faiss.read_index(
#     "movie_index.faiss"
# )
movie_to_idx = data_store.movie_to_idx
idx_to_movie = data_store.idx_to_movie
movie_titles = data_store.movie_titles
# movie_to_idx = {
#     movie_id: idx
#     for idx, movie_id
#     in enumerate(
#         movies["movieId"]
#     )
# }
# idx_to_movie = {
#     idx: movie_id
#     for movie_id, idx
#     in movie_to_idx.items()
# }
# movie_titles = (
#     movies
#     .set_index("movieId")["title"]
#     .to_dict()
# )
def get_cached_embedding(user_id):

    data = redis_client.get(
        f"user:{user_id}"
    )

    if data is None:
        EMBEDDING_CACHE_MISSES.inc()
        logger.info(
            f"EMBEDDING_CACHE_MISS user={user_id}"
        )

        return None
    EMBEDDING_CACHE_HITS.inc()
    logger.info(
        f"EMBEDDING_CACHE_HIT user={user_id}"
    )

    return pickle.loads(data)

def cache_embedding(
    user_id,
    embedding
):

    redis_client.set(
        f"user:{user_id}",
        pickle.dumps(
            embedding
        ),
        ex=EMBEDDING_TTL
    )

def get_cached_recommendations(
    user_id
):
    start_time = time.perf_counter()

    data = redis_client.get(
        f"recommendations:user:{user_id}"
    )
    
    latency = time.perf_counter() - start_time

    REQUEST_LATENCY.observe(latency)

    if data is None:
        RECOMMENDATION_CACHE_MISSES.inc()
        return None
    RECOMMENDATION_CACHE_HITS.inc()
    return pickle.loads(data)
def cache_recommendations(
    user_id,
    recommendations
):

    redis_client.set(
        f"recommendations:user:{user_id}",
        pickle.dumps(
            recommendations
        ), ex = RECOMMENDATION_TTL
    )
    

def build_user_embedding(user_id):

    user_data = (
        history_repository.get_user_history(
            user_id
        )
    )

    if not user_data:
        return None

    # newest first
    embeddings_list = []

    weights = []

    n = len(user_data)

    for rank, row in enumerate(user_data):

        movie_id = row.movie_id

        if movie_id not in movie_to_idx:
            continue

        idx = movie_to_idx[movie_id]

        embeddings_list.append(
            embeddings[idx]
        )

        weight = (n - rank) / n

        weights.append(weight)


    if len(embeddings_list) == 0:
        return None

    user_embedding = np.average(embeddings_list, axis=0, weights=weights)

    user_embedding = (user_embedding.reshape(1, -1).astype("float32"))

    faiss.normalize_L2(user_embedding)
    print(f"Built embedding for user {user_id}")
    return user_embedding
   
def recommend_user(
    user_id,
    top_k=10
):

    try:
        start_time = time.perf_counter()

        REQUEST_COUNT.inc()

        logger.info(
            f"Recommendations requested for user: {user_id}"
        )

        # =====================
        # Recommendation Cache
        # =====================

        cached_recs = (
            get_cached_recommendations(
                user_id
            )
        )

        if cached_recs is not None:

            logger.info(
                f"Returning recommendation cache for user={user_id}"
            )

            return cached_recs

        # =====================
        # Embedding Cache
        # =====================

        user_embedding = (
            get_cached_embedding(
                user_id
            )
        )

        if user_embedding is None:

            logger.info(
                f"Building embedding user={user_id}"
            )

            user_embedding = (
                build_user_embedding(
                    user_id
                )
            )

            if user_embedding is None:

                logger.error(
                    f"User not found: {user_id}"
                )

                return {
                    "error":
                    "User not found"
                }

            cache_embedding(
                user_id,
                user_embedding
            )

        # =====================
        # FAISS Search
        # =====================
    #     FAISS_SEARCHES.inc()
    #     scores, indices = (
    #         index.search(
    #             user_embedding,
    #             top_k
    #         )
    #     )

    #     recommendations = []

    #     for idx in indices[0]:

    #         movie_id = idx_to_movie[idx]
    #         title = movie_titles[movie_id]

    #         recommendations.append(
    #     {
    #         "movieId": int(movie_id),
    #         "title": movie_titles[movie_id]
    #     }
    # )
        # =====================
        # Candidate Retrieval
        # =====================


        candidates = retrieve_candidates(
            user_embedding,
            candidate_k=max(top_k * 10, 100)
        )

        logger.info(
            f"Retrieved {len(candidates)} candidates "
            f"for user={user_id}"
        )

        # =====================
        # Candidate Filtering
        # =====================

        watched_movies = get_watched_movies(
            user_id
        )

        recommendations = filter_candidates(
            candidates,
            watched_movies,
            top_k=top_k
        )

        logger.info(
            f"After filtering: "
            f"{len(recommendations)} recommendations "
            f"for user={user_id}"
        )
            

        # =====================
        # Store Recommendation Cache
        # =====================

        cache_recommendations(
            user_id,
            recommendations
        )
        start_time = time.perf_counter()
        latency = time.perf_counter() - start_time

        REQUEST_LATENCY.observe(latency)

        logger.info(
            f"user_id={user_id}, latency={latency:.4f}s"
        )

        return recommendations

    except Exception as e:

        logger.error(
            f"user_id={user_id}, error={e}"
        )

        return {
            "error":
            str(e)
        }

def record_watch_event(
    user_id: int,
    movie_id: int
):
    watch_repository.add_watch_event(
        user_id=user_id,
        movie_id=movie_id
    )

    # User embedding is now stale
    redis_client.delete(
        f"user:{user_id}"
    )

    # Recommendations based on the old embedding/history
    # are also stale
    redis_client.delete(
        f"recommendations:user:{user_id}"
    )

    logger.info(
        f"WATCH_EVENT user={user_id} movie={movie_id}"
    )

    return {
        "status": "success"
    }

def retrieve_candidates(user_embedding, candidate_k=100):
    """
    Retrieve a larger candidate pool from FAISS.

    FAISS returns the nearest candidate_k movies.
    Filtering happens separately.
    """

    FAISS_SEARCHES.inc()

    scores, indices = data_store.index.search(
        user_embedding,
        candidate_k
    )

    candidates = []

    for score, idx in zip(scores[0], indices[0]):

        # FAISS can return -1 when there aren't enough results
        if idx == -1:
            continue

        if idx not in data_store.idx_to_movie:
            continue

        movie_id = data_store.idx_to_movie[idx]

        candidates.append({
            "movieId": int(movie_id),
            "title": data_store.movie_titles[movie_id],
            "score": float(score)
        })

    return candidates
def get_watched_movies(user_id):
    """
    Return movie IDs already watched by the user.
    """

    # user_history = history[
    #     history["userId"] == user_id
    # ]

    # return set(
    #     user_history["movieId"].astype(int)
    # )
    watched_movies = (
    history_repository
    .get_watched_movie_ids(user_id)
)
    return watched_movies
def filter_candidates(
    candidates,
    watched_movies,
    top_k=10
):
    """
    Remove already-watched movies and return
    the highest-scoring remaining candidates.
    """

    recommendations = []

    for candidate in candidates:

        movie_id = candidate["movieId"]

        if movie_id in watched_movies:
            continue

        recommendations.append({
            "movieId": movie_id,
            "title": candidate["title"]
        })

        if len(recommendations) >= top_k:
            break

    return recommendations

