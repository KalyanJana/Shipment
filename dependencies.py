from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from learning.database.session import get_session
from learning.services.shipment import ShipmentService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session:SessionDep):
    return ShipmentService(session)

ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]