from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from learning.api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
)
from learning.database.models import (
    DeliveryPartner,
    Shipment,
    ShipmentStatus,
)
from learning.services.user import UserService


class DeliveryPartnerService(UserService):

    def __init__(self, session: AsyncSession):
        super().__init__(
            DeliveryPartner,
            session,
        )

    async def add(
        self,
        delivery_partner: DeliveryPartnerCreate,
    ):

        data = delivery_partner.model_dump()

        return await self._add_user(data)

    async def get_active_shipment_count(self, partner_id: UUID) -> int:
        result = await self.session.scalar(
            select(func.count(Shipment.id))
            .where(
                Shipment.delivery_partner_id == partner_id,
                Shipment.status != ShipmentStatus.delivered,
            )
        )

        return result or 0

    async def get_partner_by_zipcode(
        self,
        zipcode: int,
    ) -> Sequence[DeliveryPartner]:

        result = await self.session.scalars(
            select(DeliveryPartner).where(
                DeliveryPartner.serviceable_zip_codes.any(
                    zipcode
                )
            )
        )

        return result.all()

    async def assign_shipment(self, shipment: Shipment) -> DeliveryPartner:
        eligible_partners = await self.get_partner_by_zipcode(
            shipment.destination
        )

        for partner in eligible_partners:
            active_count = await self.get_active_shipment_count(partner.id)

            if active_count < partner.max_handling_capacity:
                return partner

        raise HTTPException(
            status_code=406,
            detail="No delivery partner available",
        )

    async def update(
        self,
        partner: DeliveryPartner,
    ) -> DeliveryPartner:

        return await self._update(partner)

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

        partner = await self._get(id)

        if partner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery partner not found",
            )

        await self._delete(partner)

        return {
            "detail": (
                f"Delivery partner with id #{id} "
                "deleted successfully"
            )
        }