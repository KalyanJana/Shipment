from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learning.database.models import User
from learning.services.base import BaseService
from learning.utils import generate_access_token

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class UserService(BaseService):

    def __init__(
        self,
        model: type[User],
        session: AsyncSession,
    ):
        super().__init__(model, session)

    async def _add_user(self, data: dict):
        password = data.pop("password")

        user = self.model(
            **data,
            password_hash=password_context.hash(password),
        )

        return await self._add(user)

    async def _get_by_email(
        self,
        email: str,
    ) -> User | None:

        return await self.session.scalar(
            select(self.model).where(
                self.model.email == email
            )
        )

    async def _generate_token(
        self,
        email: str,
        password: str,
    ) -> str:

        user = await self._get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        password_valid = password_context.verify(
            password,
            user.password_hash,
        )

        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        token = generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                }
            }
        )

        return token

    async def delete_user(self, id):
        user = await self._get(id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await self._delete(user)

        return {
            "detail": f"User with id #{id} deleted successfully"
        }