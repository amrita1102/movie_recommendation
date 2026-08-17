import faiss
import numpy as np
import pandas as pd


class DataStore:

    def __init__(self):

        self.movies = pd.read_csv("movies.csv")

        self.embeddings = np.load(
            "movie_embeddings.npy"
        ).astype("float32")

        faiss.normalize_L2(
            self.embeddings
        )

        self.index = faiss.read_index(
            "movie_index.faiss"
        )

        self.movie_to_idx = {
            movie_id: idx
            for idx, movie_id in enumerate(
                self.movies["movieId"]
            )
        }

        self.idx_to_movie = {
            idx: movie_id
            for movie_id, idx in self.movie_to_idx.items()
        }

        self.movie_titles = (
            self.movies
            .set_index("movieId")["title"]
            .to_dict()
        )


data_store = DataStore()