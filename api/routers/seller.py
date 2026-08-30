from fastapi import APIRouter

from learning.api.dependencies import SellerServiceDep
from learning.api.schemas.seller import SellerCreate, SellerRead

router = APIRouter(prefix="/seller", tags=["Seller"])

@router.post("/signup", response_model= SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)