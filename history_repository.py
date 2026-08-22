from sqlalchemy import select

from database import SessionLocal
from models import User, WatchHistory


class HistoryRepository:

    def get_user_history(self, user_id: int):

        db = SessionLocal()

        try:
            stmt = (
                select(WatchHistory)
                .where(
                    WatchHistory.user_id == user_id
                )
                .order_by(
                    WatchHistory.watched_at.desc()
                )
            )

            return db.scalars(stmt).all()

        finally:
            db.close()

    def get_watched_movie_ids(self, user_id: int):

        db = SessionLocal()

        try:
            stmt = select(
                WatchHistory.movie_id
            ).where(
                WatchHistory.user_id == user_id
            )

            return set(
                db.scalars(stmt).all()
            )

        finally:
            db.close()

    def user_exists(self, user_id: int) -> bool:

        db = SessionLocal()

        try:
            stmt = (
                select(User.id)
                .where(
                    User.id == user_id
                )
            )

            return db.scalar(stmt) is not None

        finally:
            db.close()


history_repository = HistoryRepository()