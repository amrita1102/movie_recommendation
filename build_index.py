import pandas as pd
import numpy as np
import faiss

# Load data
movies = pd.read_csv("ml-latest-small/ml-latest-small/movies.csv")

embeddings = np.load("movie_embeddings.npy").astype("float32")

# Normalize
faiss.normalize_L2(embeddings)

# Movie IDs
movie_ids = movies["movieId"].values.astype(np.int64)

dimension = embeddings.shape[1]

# Base index
base_index = faiss.IndexFlatIP(dimension)

# Wrap with IDMap
index = faiss.IndexIDMap(base_index)

# Add vectors with explicit IDs
index.add_with_ids(
    embeddings,
    movie_ids
)

# Save
faiss.write_index(
    index,
    "movie_index.faiss"
)

print(type(index))
print(index.ntotal)
