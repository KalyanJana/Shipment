from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from learning.api.schemas.seller import SellerCreate
from learning.database.models import Seller

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Get database session to perform databse operations

    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            **credentials.model_dump(exclude=["password"]),
            password_hash=password_context.hash(
                credentials.password
            ),  # passwrod hashed and stored in seller
        )

        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller
