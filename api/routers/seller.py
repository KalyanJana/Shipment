from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from learning.api.dependencies import SellerServiceDep, get_access_token
from learning.api.schemas.seller import SellerCreate, SellerRead
from learning.database.redis import add_jti_blacklist

router = APIRouter(prefix="/seller", tags=["Seller"])


@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


@router.delete("/{id}")
def delete_seller(id: int):
    pass


@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)

    # Standard OAuth2 response requires 'token_type' set to 'bearer'
    return {"access_token": token, "token_type": "bearer"}


@router.get("/logout")
async def logout_seller(token_data: Annotated[dict, Depends(get_access_token)]):
    print("jti", token_data["jti"])
    await add_jti_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out"
    }
