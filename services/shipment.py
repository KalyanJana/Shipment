from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from learning.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
)
from learning.database.models import (
    Shipment,
    ShipmentStatus,
)
from learning.services.base import BaseService
from learning.services.delivery_partner import (
    DeliveryPartnerService,
)


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
    ):
        super().__init__(
            Shipment,
            session,
        )

        self.partner_service = partner_service

    async def get(
        self,
        id: UUID,
    ) -> Shipment | None:

        return await self._get(id)

    async def add(
        self,
        shipment_create: ShipmentCreate,
        seller_id: UUID,
    ) -> Shipment:

        new_shipment = Shipment(
            **shipment_create.model_dump(),
            seller_id=seller_id,
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now(timezone.utc) + timedelta(days=3),
        )

        partner = await self.partner_service.assign_shipment(new_shipment)

        new_shipment.delivery_partner_id = partner.id

        return await self._add(new_shipment)

    async def update(
        self,
        id: UUID,
        shipment_update: ShipmentUpdate,
    ) -> Shipment:

        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )

        update_data = shipment_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update",
            )

        shipment.sqlmodel_update(update_data)

        return await self._update(shipment)

    async def delete(
        self,
        id: UUID,
    ) -> None:

        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )

        await self._delete(shipment)
