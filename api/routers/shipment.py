from uuid import UUID

from fastapi import APIRouter, status

from learning.api.dependencies import (
    DeliveryPartnerDep,
    SellerDep,
    ShipmentServiceDep,
)
from learning.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
)
from learning.database.models import Shipment


router = APIRouter(
    prefix="/shipment",
    tags=["Shipment"],
)


@router.get(
    "/{id}",
    response_model=Shipment,
)
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


@router.post(
    "/",
    response_model=Shipment,
    status_code=status.HTTP_201_CREATED,
)
async def submit_shipment(
    shipment: ShipmentCreate,
    seller: SellerDep,
    service: ShipmentServiceDep,
):

    return await service.add(
        shipment,
        seller.id,
    )


@router.patch(
    "/{id}",
    response_model=Shipment,
)
async def patch_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
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
            detail="You cannot update this shipment",
        )

    return await service.update(
        id,
        shipment_update,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
)
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

    return {
        "detail": f"Shipment with id #{id} is deleted!"
    }