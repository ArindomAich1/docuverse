import uuid
import redis
from app.config.config import settings

# Module-level singleton — one connection pool for the entire app
_redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Lua script: atomically check value then delete
# Prevents releasing a lock you don't own
_RELEASE_LOCK_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

CHAT_LOCK_TTL_SECONDS = 120


def acquire_chat_lock(document_id: int) -> str | None:
    """
    Attempts to acquire a lock for the given document's chat.
    Returns the lock token (UUID) if acquired, None if already locked.
    """
    lock_key   = f"chat_lock:doc_{document_id}"
    lock_token = str(uuid.uuid4())

    acquired = _redis_client.set(
        lock_key,
        lock_token,
        nx=True,                        # SET only if Not eXists
        ex=CHAT_LOCK_TTL_SECONDS        # TTL as safety net
    )
    return lock_token if acquired else None


def release_chat_lock(document_id: int, lock_token: str) -> None:
    """
    Releases the lock only if we are still the owner.
    Uses a Lua script for atomic check-and-delete.
    """
    lock_key = f"chat_lock:doc_{document_id}"
    _redis_client.eval(_RELEASE_LOCK_SCRIPT, 1, lock_key, lock_token)