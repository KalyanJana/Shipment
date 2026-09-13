from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from learning.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from learning.database.models import DeliveryPartner, Seller, Shipment, ShipmentStatus
from learning.services.base import BaseService
from learning.services.delivery_partner import DeliveryPartnerService
from learning.services.shipment_event import ShipmentEventService
from learning.services.shipment_status import validate_status_transition


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService
    ):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment | None:

        result = await self.session.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.timeline)
            )
            .where(Shipment.id == id)
        )

        return result.scalar_one_or_none()

    async def add(
        self,
        shipment_create: ShipmentCreate,
        seller: Seller,
    ) -> Shipment:

        new_shipment = Shipment(
            **shipment_create.model_dump(),
            seller_id=seller.id,
            estimated_delivery=datetime.now(timezone.utc) + timedelta(days=3),
        )

        partner = await self.partner_service.assign_shipment(new_shipment)

        new_shipment.delivery_partner_id = partner.id

        shipment = await self._add(new_shipment, commit=False)

        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name}",
            commit=False
        )
        # shipment.timeline.append(event)

        # Commit shipment + initial event together 
        await self.session.commit()
        
        return await self.get(shipment.id)

    async def update(
        self,
        id: UUID,
        shipment_update: ShipmentUpdate,
        partner: DeliveryPartner,
    ) -> Shipment:

        shipment = await self.get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this shipment",
            )

        update = shipment_update.model_dump(
            exclude_none=True
        )

        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update",
            )
        
        current_event = self.event_service.get_latest_event( shipment ) 

        if current_event is None: 
            raise HTTPException( 
                status_code=status.HTTP_409_CONFLICT, 
                detail="Shipment has no status event", ) 
        
        current_status = current_event.status

        #Shipment-level fields
        if "estimated_delivery" in update: 
            shipment.estimated_delivery = update.pop( "estimated_delivery" )

        #Event-level fields
        new_status = update.get("status") 

        if new_status is not None: 
            validate_status_transition( current_status, new_status, ) 

        # If anything remains, create a new shipment event. 
        if update: 
            event = await self.event_service.add( shipment=shipment, **update, commit=False ) 
            shipment.timeline.append(event) 
        
        # return await self._update(shipment) 
        await self.session.commit() 

        # Reload shipment + timeline 
        return await self.get(shipment.id)


    async def cancel(
        self,
        id: UUID,
        seller: Seller,
    ) -> Shipment:

        shipment = await self.get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot cancel this shipment",
            )

        current_event = self.event_service.get_latest_event(
            shipment
        )

        if current_event is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shipment has no status event",
            )

        validate_status_transition(
            current_event.status,
            ShipmentStatus.cancelled,
        )

        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
            description="Shipment cancelled by the seller",
            commit=False
        )

        # shipment.timeline.append(event)

        # return shipment
        await self.session.commit()

        return await self.get(shipment.id)

    


    async def delete(self,id: UUID) -> None:
        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found",
            )

        await self._delete(shipment)
