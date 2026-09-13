from learning.database.models import Shipment, ShipmentEvent, ShipmentStatus
from learning.services.base import BaseService


class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)
    
    def get_latest_event(self, shipment: Shipment) -> ShipmentEvent | None:
        if not shipment.timeline: return None

        return max(shipment.timeline, key=lambda event: event.created_at)

        # timeline = shipment.timeline
        # timeline.sort(key=lambda event: event.created_at)
        # return timeline[-1]

    async def add(
        self,
        shipment: Shipment,
        location: int | None = None,
        status: ShipmentStatus | None = None,
        description: str | None = None,
        commit: bool = True
    ) -> ShipmentEvent:

        last_event = self.get_latest_event(shipment)

        # If this is not the first event, inherit missing values # from the previous event. 
        if last_event: 
            if location is None: 
                location = last_event.location 
            
            if status is None: 
                status = last_event.status 
            
        if status is None:
            raise ValueError( "Shipment event status cannot be None" ) 
            
        if location is None: 
            raise ValueError( "Shipment event location cannot be None" )

        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=(
                description
                if description is not None
                else self._generate_description(status, location)
            ),
            shipment_id=shipment.id,
        )

        return await self._add(new_event, commit=commit)

    def _generate_description(
        self,
        status: ShipmentStatus,
        location: int | None,
    ) -> str:

        match status:
            case ShipmentStatus.placed:
                return "Shipment created and delivery partner assigned"

            case ShipmentStatus.in_transit:
                return f"Shipment scanned at {location}"

            case ShipmentStatus.out_for_delivery:
                return "Shipment is out for delivery"

            case ShipmentStatus.delivered:
                return "Shipment delivered successfully"

            case ShipmentStatus.cancelled:
                return "Shipment cancelled by the seller"

            case _:
                return "Shipment status updated"
