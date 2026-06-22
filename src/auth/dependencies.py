from typing import Any
from fastapi import HTTPException, Request, status,Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from src.db.models import User
from src.errors import InvalidToken


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Any:
        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token",
                },
            )

        token = creds.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token",
                },
            )

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token",
                },
            )

        jti = token_data.get("jti")
        if jti is None or await token_in_blocklist(jti):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get a new token",
                },
            )

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        if token_data is None:
            return False
        return True

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        # if token_data is None or token_data.get('refresh', False):
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide access token")
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide refresh token",
            )

async def get_current_user(token_details:dict = Depends(AccessTokenBearer()), session:AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']
    
    user = await user_service.get_user_by_email(user_email,session)
    
    return user

#check role
class RoleChecker:
    def __init__(self,allowed_roles:list[str]) -> None:
        self.allowed_roles = allowed_roles
        
        
    def __call__(self,current_user:User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Access denied')
        
