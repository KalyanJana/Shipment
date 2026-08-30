from fastapi import APIRouter, HTTPException, status

from learning.api.dependencies import ShipmentServiceDep
from learning.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from learning.database.models import Shipment

router = APIRouter(prefix="/shipment", tags=["Shipment"])


@router.get("/", response_model=Shipment)
async def get_shipment(id: int, service: ShipmentServiceDep):
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id does not exist!"
        )

    return shipment


@router.post("/")
async def submit_shipment(shipment: ShipmentCreate, service: ShipmentServiceDep) -> Shipment:
    try:
        return await service.add(shipment)
    except Exception as exc:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating shipment: {exc}",
        ) from exc


@router.patch("/", response_model=Shipment)
async def patch_shipment(id: int, shipment_update: ShipmentUpdate, service: ShipmentServiceDep):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update"
        )

    shipment = await service.update(id, update)

    return shipment


@router.delete("/")
async def delete_shipment(id: int, service: ShipmentServiceDep) -> dict[str, str]:

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}
