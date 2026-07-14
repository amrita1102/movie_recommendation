from fastapi import APIRouter
from redis_client import redis_client
from recommend import index

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}

@router.get("/health/redis")
def redis_health():
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/health/faiss")
def faiss_health():
    return {
        "status": "healthy",
        "vectors": index.ntotal,
        "dimension": index.d
    }