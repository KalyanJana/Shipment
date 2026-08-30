from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from learning.database.models import ShipmentStatus
from learning.schemas.shipment import Shipment, ShipmentCreate, ShipmentUpdate


class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment | None:
        return await self.session.get(Shipment, id)

    async def add(self, shipment_create: ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
        )

        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)

        return new_shipment

    async def update(self, id: int, shipment_update: ShipmentUpdate) -> Shipment:
        shipment = await self.get(id)
        if shipment is None:
            raise ValueError(f"Shipment with id {id} not found")

        shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    async def delete(self, id: int) -> None:
        shipment = await self.get(id)
        if shipment is None:
            raise ValueError(f"Shipment with id {id} not found")

        await self.session.delete(shipment)
        await self.session.commit()
