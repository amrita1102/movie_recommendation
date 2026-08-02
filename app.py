from fastapi import FastAPI
from recommend import recommend_user, record_watch_event
import logging
import time
import faiss
from pydantic import BaseModel
import redis_client
from health import router as health_router
from metrics_router import router as metrics_router
from fastapi import HTTPException
from health import router as health_router

logging.basicConfig(filename="app.log",level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

index = faiss.read_index(
    "movie_index.faiss"
)

app = FastAPI()

app.include_router(health_router)
app.include_router(metrics_router)

class WatchEvent(BaseModel):

    user_id: int

    movie_id: int

# for route in app.routes:
#     print(route.path)
    
@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
@app.get("/health/redis")
def redis_health():

    redis_client.redis_client.ping()

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
def get_recommendations(user_id: int):
    try:
        logging.info(f"Recommendations requested for user: {user_id}")

        start = time.time()

        recommendations = recommend_user(user_id)

        if isinstance(recommendations, dict) and "error" in recommendations:
            raise HTTPException(
                status_code=404,
                detail=recommendations["error"]
            )

        latency = round(time.time() - start, 5)

        logging.info(f"Recommendations for user {user_id}: {recommendations}")

        logging.info(
            f"user_id={user_id}, latency={latency}s"
        )

        return {
            "recommendations": recommendations
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.exception(
            f"user_id={user_id}, error={e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    
# python -m pytest --cov=. --cov-report=term-missing