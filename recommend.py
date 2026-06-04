import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pickle
from redis_client import redis_client
from datetime import datetime

movies = pd.read_csv("ml-latest-small\ml-latest-small\movies.csv")

history = pd.read_csv("user_history.csv")

EMBEDDING_TTL = 600
RECOMMENDATION_TTL = 90

history["timestamp"] = pd.to_datetime(
    history["timestamp"]
)

embeddings = np.load(
    "movie_embeddings.npy"
).astype("float32")

faiss.normalize_L2(
    embeddings
)

index = faiss.read_index(
    "movie_index.faiss"
)

movie_to_idx = {
    movie_id: idx
    for idx, movie_id
    in enumerate(
        movies["movieId"]
    )
}
def get_cached_embedding(user_id):

    data = redis_client.get(
        f"user:{user_id}"
    )

    if data is None:
        return None

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

    data = redis_client.get(
        f"recommendations:user:{user_id}"
    )

    if data is None:
        return None

    return pickle.loads(data)
def cache_recommendations(
    user_id,
    recommendations
):

    redis_client.set(
        f"recommendations:user:{user_id}",
        pickle.dumps(
            recommendations
        )
    )

def build_user_embedding(
    user_id
):

    user_data = history[
        history["userId"] == user_id
    ].copy()

    if len(user_data) == 0:
        return None

    # newest first
    user_data = user_data.sort_values(
        by="timestamp",
        ascending=False
    )

    embeddings_list = []

    weights = []

    # weight:
    # newest movie gets highest weight

    n = len(user_data)

    for rank, row in enumerate(
        user_data.itertuples()
    ):

        movie_id = row.movieId

        if movie_id not in movie_to_idx:
            continue

        idx = movie_to_idx[
            movie_id
        ]

        embeddings_list.append(
            embeddings[idx]
        )

        weight = (
            n - rank
        ) / n

        weights.append(
            weight
        )

    if len(
        embeddings_list
    ) == 0:
        return None

    user_embedding = np.average(
        embeddings_list,
        axis=0,
        weights=weights
    )

    user_embedding = (
        user_embedding
        .reshape(1, -1)
        .astype("float32")
    )

    faiss.normalize_L2(
        user_embedding
    )
    print(f"Built embedding for user {user_id}")
    return user_embedding
   
def recommend_user(
    user_id,
    top_k=10
):
    recommendations = (
            get_cached_recommendations(
                user_id
            )
        )

    if recommendations is not None:

        print(
            f"REC CACHE HIT {user_id}"
        )

        return recommendations

    print(
        f"REC CACHE MISS {user_id}"
    )

    user_embedding = (
        get_cached_embedding(
            user_id
        )
    )

    if user_embedding is None:

        print(
            f"EMBEDDING MISS {user_id}"
        )

        user_embedding = (
            build_user_embedding(
                user_id
            )
        )

        cache_embedding(
            user_id,
            user_embedding
        )

    else:

        print(
            f"EMBEDDING HIT {user_id}"
        )
    
    scores, ids = index.search(
        user_embedding,
        top_k * 3
    )

    watched_movies = set(

        history[
            history["userId"]
            == user_id
        ]["movieId"]

    )

    recommendations = []

    for movie_id in ids[0]:

        if movie_id == -1:
            continue

        if movie_id in watched_movies:
            continue

        movie_row = movies[
            movies["movieId"]
            == movie_id
        ]

        if len(movie_row) == 0:
            continue

        recommendations.append(
            {
                "movieId":
                int(movie_id),

                "title":
                movie_row.iloc[0]["title"],

                "genres":
                movie_row.iloc[0]["genres"]
            }
        )

        if (
            len(
                recommendations
            )
            >= top_k
        ):
            break

    return recommendations

def record_watch_event(
    user_id,
    movie_id
):

    global history

    new_row = pd.DataFrame(
        [
            {
                "userId": user_id,
                "movieId": movie_id,
                "timestamp":
                datetime.now()
            }
        ]
    )

    history = pd.concat(
        [
            history,
            new_row
        ],
        ignore_index=True
    )

    history.to_csv(
        "user_history.csv",
        index=False
    )

    redis_client.delete(f"user:{user_id}")

    redis_client.delete(f"recommendations:user:{user_id}")

    print(
        f"Cache invalidated for user {user_id}"
    )

# without cache
# def recommend_user(user_id,top_k=10):

#     user_embedding = (
#         build_user_embedding(
#             user_id
#         )
#     )

#     if user_embedding is None:

#         return {
#             "error":
#             "user not found"
#         }

#     scores, ids = index.search(
#         user_embedding,
#         top_k * 3
#     )

#     watched_movies = set(

#         history[
#             history["userId"]
#             == user_id
#         ]["movieId"]

#     )

#     recommendations = []

#     for movie_id in ids[0]:

#         if movie_id == -1:
#             continue

#         if movie_id in watched_movies:
#             continue

#         movie_row = movies[
#             movies["movieId"]
#             == movie_id
#         ]

#         if len(movie_row) == 0:
#             continue

#         recommendations.append(
#             {
#                 "movieId":
#                 int(movie_id),

#                 "title":
#                 movie_row.iloc[0]["title"],

#                 "genres":
#                 movie_row.iloc[0]["genres"]
#             }
#         )

#         if (
#             len(
#                 recommendations
#             )
#             >= top_k
#         ):
#             break

#     return recommendations

if __name__ == "__main__":

    recs = recommend_user(
        101
    )

    for movie in recs:
        print(movie)

# -------------------------
# MovieId -> embedding row
# -------------------------

movie_to_idx = {
    movie_id: idx
    for idx, movie_id
    in enumerate(
        movies["movieId"]
    )
}

# -------------------------
# Movie Recommendation
# -------------------------

movies = pd.read_csv("ml-latest-small/ml-latest-small/movies.csv")

embeddings = np.load("movie_embeddings.npy")
embeddings = embeddings.astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
faiss.normalize_L2(
    embeddings
)
index.add(
    embeddings
)
faiss.write_index(
    index,
    "movie_index.faiss"
)

def get_similar_movies(movie_id,top_k=10):

    idx = movies[movies["movieId"] == movie_id].index[0]

    query = embeddings[idx]

    query = np.expand_dims(query, axis=0)

    scores, indices = index.search(query,top_k + 1)

    return (movies.iloc[indices[0][1:]]["title"].tolist())

def get_similar_movies(movie_id):
    query_embedding = embeddings[movie_id]

    similarities = cosine_similarity(
        [query_embedding],
        embeddings
    )[0]

    top_idx = similarities.argsort()[-11:-1][::-1]

    return (movies.iloc[top_idx]["title"].tolist())

# Example usage:
# movie_id = 1  # The movie ID for which you want recommendations
# print(f"Recommendations for movie {movie_id}:{movies.iloc[movie_id]['title']}") 
# similar_movies = get_similar_movies(movie_id)
# print(similar_movies)  

