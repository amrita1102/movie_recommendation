from sqlalchemy import select

from database import SessionLocal
from models import Movie


class MovieRepository:

    def exists(self, movie_id: int) -> bool:

        db = SessionLocal()

        try:
            stmt = (
                select(Movie.id)
                .where(Movie.id == movie_id)
            )

            return db.scalar(stmt) is not None

        finally:
            db.close()

    def get_movie(self, movie_id: int):

        db = SessionLocal()

        try:
            stmt = (
                select(Movie)
                .where(Movie.id == movie_id)
            )

            return db.scalar(stmt)

        finally:
            db.close()


movie_repository = MovieRepository()   