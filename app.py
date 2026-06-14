from fastapi import FastAPI
from recommend import recommend_user, record_watch_event
import logging
import time
import faiss
from pydantic import BaseModel
import redis_client

logging.basicConfig(filename="app.log",level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

index = faiss.read_index(
    "movie_index.faiss"
)

app = FastAPI()

class WatchEvent(BaseModel):

    user_id: int

    movie_id: int
@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
@app.get("/health/redis")
def redis_health():

    redis_client.ping()

    return {
        "redis":"up"
    }

@app.post("/watch")
def watch_movie(
    event: WatchEvent
):

    record_watch_event(
        event.user_id,
        event.movie_id
    )

    return {
        "status":
        "success"
    }

@app.get("/recommend/{movie_id}")


def recommend(movie_id:int):
    try:
        logging.info(f"Movie requested: {movie_id}")
        start = time.time()    
        movies = get_similar_movies(movie_id)
        latency = round(time.time() - start,5)
        logging.info(f"Recommendations for movie {movie_id}: {movies}")
        logging.info(
            f"movie_id={movie_id}, latency={latency}s"
        )
        return {"recommendations": movies}  
    except Exception as e:
        logging.error(
        f"movie_id={movie_id}, error={str(e)}"
    )
        return {"error":"movie not found"}
    


@app.get("/recommend/user/{user_id}")
def get_recommendations(user_id:int):
    try:
        logging.info(f"Recommendations requested for user: {user_id}")
        start = time.time()    
        recommendations = recommend_user(user_id)
        latency = round(time.time() - start,5)
        logging.info(f"Recommendations for user {user_id}: {recommendations}")
        logging.info(
            f"user_id={user_id}, latency={latency}s"
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logging.error(
            f"user_id={user_id}, error={str(e)}"
        )
        return {"error":"user not found"}

