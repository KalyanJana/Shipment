from redis.asyncio import Redis

from learning.config import db_settings

_token_backlisted = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,
    decode_responses=True,
    protocol=2,
)

async def add_jti_blacklist(jti: str, expire_seconds: int = 54000) -> None:
    await _token_backlisted.set(name=jti, value="blacklisted", ex=expire_seconds)

async def is_jti_backlisted(jti: str) -> bool:
    return bool(await _token_backlisted.exists(jti))


