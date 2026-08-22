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


movie_repository = MovieRepository()