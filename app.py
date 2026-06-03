from fastapi import FastAPI
from recommend import get_similar_movies,recommend_user
import logging
import time
import faiss

logging.basicConfig(filename="app.log",level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

index = faiss.read_index(
    "movie_index.faiss"
)

app = FastAPI()

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

