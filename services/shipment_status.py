from fastapi import HTTPException, status 
from learning.database.models import ShipmentStatus 

# Defines every valid next status for the current status. 
ALLOWED_TRANSITIONS: dict[ShipmentStatus, set[ShipmentStatus]] = { 
    ShipmentStatus.placed: { ShipmentStatus.in_transit, ShipmentStatus.cancelled, }, 
    ShipmentStatus.in_transit: { ShipmentStatus.out_for_delivery, ShipmentStatus.cancelled, }, 
    ShipmentStatus.out_for_delivery: { ShipmentStatus.delivered, ShipmentStatus.cancelled, }, 
    ShipmentStatus.delivered: set(), ShipmentStatus.cancelled: set(),
} 
    
def validate_status_transition( current_status: ShipmentStatus, new_status: ShipmentStatus, ) -> None: 
    if current_status == new_status: 
        raise HTTPException( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Shipment is already {current_status.value}", 
        ) 
        allowed_statuses = ALLOWED_TRANSITIONS.get(current_status, set()) 
        if new_status not in allowed_statuses: 
            raise HTTPException( 
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=( f"Invalid status transition: " f"{current_status.value} -> {new_status.value}" ), 
            )