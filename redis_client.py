import os
import redis
import logger
import pickle

REC_TTL = 3600  # 1 hour

REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "localhost"
)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=False
)


def get_cached_recommendations(
    user_id
):

    key = f"recommendations:user:{user_id}"

    data = redis_client.get(key)

    if data is None:

        logger.info(
            f"REC_CACHE_MISS user={user_id}"
        )

        return None

    logger.info(
        f"REC_CACHE_HIT user={user_id}"
    )

    return pickle.loads(data)


def cache_recommendations(
    user_id,
    recommendations
):

    key = f"recommendations:user:{user_id}"

    redis_client.set(
        key,
        pickle.dumps(
            recommendations
        ),
        ex=REC_TTL
    )

    logger.info(
        f"REC_CACHE_WRITE user={user_id}"
    )


def invalidate_recommendations(
    user_id
):

    key = f"recommendations:user:{user_id}"

    redis_client.delete(key)

    logger.info(
        f"REC_CACHE_DELETE user={user_id}"
    )