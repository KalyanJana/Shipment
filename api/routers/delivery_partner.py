from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from learning.api.dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    get_partner_access_token,
)
from learning.api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)
from learning.database.redis import add_jti_blacklist


router = APIRouter(
    prefix="/partner",
    tags=["Delivery Partner"],
)


@router.post(
    "/signup",
    response_model=DeliveryPartnerRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_delivery_partner(
    delivery_partner: DeliveryPartnerCreate,
    service: DeliveryPartnerServiceDep,
):

    return await service.add(
        delivery_partner
    )


@router.delete("/{id}")
async def delete_delivery_partner(
    id: UUID,
    service: DeliveryPartnerServiceDep,
):

    return await service.delete(id)


@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: DeliveryPartnerServiceDep,
):

    token = await service.token(
        request_form.username,
        request_form.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.patch(
    "/",
    response_model=DeliveryPartnerRead,
)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):

    partner.sqlmodel_update(
        partner_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
    )

    return await service.update(partner)


@router.post("/logout")
async def logout_delivery_partner(
    token_data: Annotated[
        dict,
        Depends(get_partner_access_token),
    ],
):

    await add_jti_blacklist(
        token_data["jti"]
    )

    return {
        "detail": "Successfully logged out"
    }