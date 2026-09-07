from fastapi.security import OAuth2PasswordBearer

# from fastapi.security import HTTPBearer
# from fastapi import HTTPException
# from typing import Annotated


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/seller/token")
# class AccessTokenBearer(HTTPBearer):
#     async def ____(self, request):
#         # request.headers.get("Authrozation").split("")[1]
#         auth_credentials = await super().__call__(request)
#         token = auth_credentials.credentials

#         token_data = decode_access_token(token)

#         if token_data is None:
#             raise HTTPException(
#                 status_code: 401,
#                 detail="Not authorized"
#             )

#         return token_data

# acces_token_bearer = AccessTokenBearer()

# manual_scheme = Annotated[dict, Depends(access_token_bearer)]
