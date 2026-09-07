from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from learning.core.security import oauth2_scheme
from learning.database.models import Seller
from learning.database.session import get_session
from learning.services.seller import SellerService
from learning.services.shipment import ShipmentService
from learning.utils import decode_access_token

#Asynchronous database session dependency annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]

#Access token data dep
def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    data = decode_access_token(token)

    if data is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    return data

#logged in seller
async def get_current_seller(
    token_data: Annotated[dict, Depends(get_access_token)],
    session: SessionDep,
) -> Seller:
    user_info = token_data.get("user")
    if not user_info or "id" not in user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token structure",
        )

    seller = await session.get(Seller, user_info["id"])

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return seller

#Shipment service dependency
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

#Seller service dependency
def get_seller_service(session: SessionDep):
    return SellerService(session)



#Seller Dep
SellerDep = Annotated[Seller, Depends(get_current_seller)]

#shipment service dependency annotation
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

#seller service dependency annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]