import pandas as pd
from sqlalchemy import select

from database import SessionLocal
from models import Movie


CSV_PATH = "movies.csv"


def import_movies():
    df = pd.read_csv(CSV_PATH)

    db = SessionLocal()

    try:
        existing_ids = set(
            db.scalars(
                select(Movie.id)
            ).all()
        )

        movies_to_add = []

        for row in df.itertuples(index=False):

            movie_id = int(row.movieId)

            if movie_id in existing_ids:
                continue

            movies_to_add.append(
                Movie(
                    id=movie_id,
                    title=str(row.title),
                    genres=str(row.genres)
                )
            )

        if movies_to_add:
            db.add_all(movies_to_add)
            db.commit()

        print(
            f"Imported {len(movies_to_add)} movies."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_movies()