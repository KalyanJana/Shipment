from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from learning.api.dependencies import (
    SellerServiceDep,
    get_seller_access_token,
)
from learning.api.schemas.seller import (
    SellerCreate,
    SellerRead,
)
from learning.database.redis import add_jti_blacklist

router = APIRouter(
    prefix="/seller",
    tags=["Seller"],
)


@router.post(
    "/signup",
    response_model=SellerRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_seller(
    seller: SellerCreate,
    service: SellerServiceDep,
):

    return await service.add(seller)


@router.delete("/{id}")
async def delete_seller(
    id: UUID,
    service: SellerServiceDep,
):

    return await service.delete(id)


@router.post("/token")
async def login_seller(
    request_form: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: SellerServiceDep,
):

    token = await service.token(
        request_form.username,
        request_form.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout_seller(
    token_data: Annotated[
        dict,
        Depends(get_seller_access_token),
    ],
):

    await add_jti_blacklist(
        token_data["jti"]
    )

    return {
        "detail": "Successfully logged out"
    }