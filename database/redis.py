from redis.asyncio import Redis

from learning.config import db_settings


token_blacklist = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,
    decode_responses=True,
    protocol=2,
    socket_timeout=5.0,
)


async def add_jti_blacklist(
    jti: str,
    expire_seconds: int = 5400,
) -> None:

    await token_blacklist.set(
        name=f"blacklist:{jti}",
        value="1",
        ex=expire_seconds,
    )


async def is_jti_blacklisted(
    jti: str,
) -> bool:

    return bool(
        await token_blacklist.exists(
            f"blacklist:{jti}"
        )
    )