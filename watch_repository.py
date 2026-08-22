from datetime import datetime

from database import SessionLocal
from models import WatchHistory, User


class WatchRepository:

    def add_watch_event(
        self,
        user_id: int,
        movie_id: int
    ):
        db = SessionLocal()

        try:
            event = WatchHistory(
                user_id=user_id,
                movie_id=movie_id,
                watched_at=datetime.utcnow()
            )

            db.add(event)
            db.commit()
            db.refresh(event)

            return event

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def user_exists(self, user_id: int) -> bool:

        db = SessionLocal()

        try:
            stmt = (
                select(User.id)
                .where(User.id == user_id)
            )

            return db.scalar(stmt) is not None

        finally:
            db.close()


watch_repository = WatchRepository()