from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from learning.core.security import (
    oauth2_scheme_partner,
    oauth2_scheme_seller,
)
from learning.database.models import (
    DeliveryPartner,
    Seller,
)
from learning.database.redis import is_jti_blacklisted
from learning.database.session import get_session
from learning.services.delivery_partner import (
    DeliveryPartnerService,
)
from learning.services.seller import SellerService
from learning.services.shipment import ShipmentService
from learning.utils import decode_access_token

SessionDep = Annotated[
    AsyncSession,
    Depends(get_session),
]


async def _get_access_token(
    token: str,
) -> dict:

    data = decode_access_token(token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    jti = data.get("jti")

    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if await is_jti_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return data


async def get_seller_access_token(
    token: Annotated[
        str,
        Depends(oauth2_scheme_seller),
    ],
) -> dict:

    return await _get_access_token(token)


async def get_partner_access_token(
    token: Annotated[
        str,
        Depends(oauth2_scheme_partner),
    ],
) -> dict:

    return await _get_access_token(token)


async def get_current_seller(
    token_data: Annotated[
        dict,
        Depends(get_seller_access_token),
    ],
    session: SessionDep,
) -> Seller:

    user_id = token_data["user"]["id"]

    seller = await session.get(
        Seller,
        UUID(user_id),
    )

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller not found",
        )

    return seller


async def get_current_partner(
    token_data: Annotated[
        dict,
        Depends(get_partner_access_token),
    ],
    session: SessionDep,
) -> DeliveryPartner:

    user_id = token_data["user"]["id"]

    partner = await session.get(
        DeliveryPartner,
        UUID(user_id),
    )

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Delivery partner not found",
        )

    return partner


def get_shipment_service(
    session: SessionDep,
):

    return ShipmentService(
        session,
        DeliveryPartnerService(session),
    )


def get_seller_service(
    session: SessionDep,
):

    return SellerService(session)


def get_delivery_partner_service(
    session: SessionDep,
):

    return DeliveryPartnerService(session)


SellerDep = Annotated[
    Seller,
    Depends(get_current_seller),
]

DeliveryPartnerDep = Annotated[
    DeliveryPartner,
    Depends(get_current_partner),
]

ShipmentServiceDep = Annotated[
    ShipmentService,
    Depends(get_shipment_service),
]

SellerServiceDep = Annotated[
    SellerService,
    Depends(get_seller_service),
]

DeliveryPartnerServiceDep = Annotated[
    DeliveryPartnerService,
    Depends(get_delivery_partner_service),
]