from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from learning.api.schemas.seller import SellerCreate
from learning.database.models import Seller
from learning.services.user import UserService


class SellerService(UserService):

    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)

    async def add(
        self,
        seller_create: SellerCreate,
    ) -> Seller:

        data = seller_create.model_dump()

        return await self._add_user(data)

    async def token(
        self,
        email: str,
        password: str,
    ) -> str:

        return await self._generate_token(
            email,
            password,
        )

    async def delete(
        self,
        id: UUID,
    ):

        return await self.delete_user(id)