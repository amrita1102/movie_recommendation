import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

movies = pd.read_csv("movies.csv")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

texts = (
    movies["title"] +
    " " +
    movies["genres"]
)

embeddings = model.encode(
    texts.tolist(),
    show_progress_bar=True
)


np.save(
    "movie_embeddings.npy",
    embeddings
)