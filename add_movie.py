import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

movies = pd.read_csv("ml-latest-small/ml-latest-small/movies.csv")
movies = movies.sort_values(by="movieId").reset_index(drop=True)
print(movies.movieId.max() + 1)
new_movieId = movies.movieId.max() + 1
new_movie = {
    "movieId": new_movieId,
    "title": "Project Hail Mary",
    "genres": "Sci-Fi|Adventure"
}

model = SentenceTransformer("all-MiniLM-L6-v2")

text = (new_movie["title"]+ " "+ new_movie["genres"])

new_embedding = model.encode([text])

new_embedding = np.array(new_embedding,dtype="float32")

faiss.normalize_L2(new_embedding)


index = faiss.read_index("movie_index.faiss")
print(type(index))

index.add_with_ids(new_embedding,np.array([new_movie["movieId"]],dtype=np.int64))

faiss.write_index(index,"movie_index.faiss")

embeddings = np.load("movie_embeddings.npy")

embeddings = np.vstack([embeddings,new_embedding])

np.save("movie_embeddings.npy",embeddings)

movies = pd.concat([movies,pd.DataFrame([new_movie])],ignore_index=True)

movies.to_csv("movies.csv",index=False)

print("Movie Added Successfully")