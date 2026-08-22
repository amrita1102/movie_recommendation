import pandas as pd
from sqlalchemy import select

from database import SessionLocal
from models import User, Movie, WatchHistory


CSV_PATH = "user_history.csv"


def import_history():

    df = pd.read_csv(CSV_PATH)

    db = SessionLocal()

    try:
        # --------------------------------
        # Existing users
        # --------------------------------

        existing_users = set(
            db.scalars(
                select(User.id)
            ).all()
        )

        # --------------------------------
        # Existing movies
        # --------------------------------

        existing_movies = set(
            db.scalars(
                select(Movie.id)
            ).all()
        )

        # --------------------------------
        # Create users
        # --------------------------------

        unique_users = (
            df["userId"]
            .dropna()
            .astype(int)
            .unique()
        )

        users_to_add = []

        for user_id in unique_users:

            if user_id in existing_users:
                continue

            users_to_add.append(
                User(
                    id=int(user_id),
                    username=f"user_{user_id}"
                )
            )

        if users_to_add:
            db.add_all(users_to_add)
            db.flush()

        # --------------------------------
        # Create watch history
        # --------------------------------

        history_to_add = []

        for row in df.itertuples(index=False):

            user_id = int(row.userId)
            movie_id = int(row.movieId)

            # Skip bad movie references
            if movie_id not in existing_movies:
                continue

            watched_at = pd.to_datetime(
                row.timestamp
            )

            history_to_add.append(
                WatchHistory(
                    user_id=user_id,
                    movie_id=movie_id,
                    watched_at=watched_at.to_pydatetime()
                )
            )

        if history_to_add:
            db.add_all(history_to_add)

        db.commit()

        print(
            f"Imported {len(users_to_add)} users."
        )

        print(
            f"Imported {len(history_to_add)} watch events."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_history()