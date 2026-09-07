from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learning.api.schemas.seller import SellerCreate
from learning.database.models import Seller
from learning.utils import generate_access_token

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

    async def token(self, email: str, password: str) -> str:
        # validate the credentials
        result = await self.session.execute(
            select(Seller).where(Seller.email == email)
        )
        # Use scalar_one_or_none() instead of scalar()
        seller = result.scalar_one_or_none()

        if seller is None or not password_context.verify(
            password, seller.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = generate_access_token(
            data={"user": {"name": seller.name, "id": seller.id}}
        )

        return token
