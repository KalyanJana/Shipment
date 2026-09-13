from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from learning.api.dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep
from learning.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from learning.database.models import Shipment

router = APIRouter(prefix="/shipment", tags=["Shipment"])


@router.get("/{id}", response_model=Shipment)
async def get_shipment(
    id: UUID,
    seller: SellerDep,
    service: ShipmentServiceDep,
):

    shipment = await service.get(id)

    if shipment is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    # Important:
    # Seller should only see his own shipment.
    if shipment.seller_id != seller.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this shipment",
        )

    return shipment


@router.post("/", response_model=ShipmentRead, status_code=status.HTTP_201_CREATED)
async def submit_shipment(
    shipment: ShipmentCreate,
    seller: SellerDep,
    service: ShipmentServiceDep,
):
    return await service.add(shipment, seller)


@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,
    service: ShipmentServiceDep,
):

    # update data with given fields
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, shipment_update, partner)


@router.delete("/")
async def delete_shipment(
    id: UUID,
    seller: SellerDep,
    service: ShipmentServiceDep,
):

    shipment = await service.get(id)

    if shipment is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    if shipment.seller_id != seller.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete this shipment",
        )

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}


@router.get("/{id}/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    seller: SellerDep,
    service: ShipmentServiceDep,
):

    return await service.cancel(id, seller)
