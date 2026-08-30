from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from learning.database.session import get_session
from learning.services.seller import SellerService
from learning.services.shipment import ShipmentService

#Asynchronous database session dependency annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]

#Shipment service dependency
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

#Seller service dependency
def get_seller_service(session: SessionDep):
    return SellerService(session)

#shipment service dependency annotation
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

#seller service dependency annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]