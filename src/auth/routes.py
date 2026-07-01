from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserResponseModel, UserLoginModel,UserBooksModel,EmailModel,PasswordResetRequestModel,PasswordResetConfirmModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, verify_password,create_url_safe_token,decode_url_safe_token,generate_password_hash
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer, AccessTokenBearer,get_current_user,RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.mail import mail, create_message
from src.config import Config

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post('/send_mail')
async def send_mail(emails:EmailModel):
    addresses = emails.addresses
    html = "<h1>Welcome to Our App</h1><p>This is a test email sent from FastAPI.</p>"
    message = create_message(recipients=addresses, subject="Test Email", body=html)
    try:
        await mail.send_message(message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(e)}"
    )
    return JSONResponse(content={"message": "Email sent successfully", "recipients": addresses}, status_code=status.HTTP_200_OK)


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists!",
        )

    new_user = await user_service.create_user(user_data, session)
    
    token = create_url_safe_token({"email":email})
    
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    
    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    message = create_message(recipients=[email], subject="Verify Email", body=html_message)
    
    await mail.send_message(message)

    # return new_user
    return {
        "message":"Account Created! Check your email to verify",
        "user": new_user
    }
    
    
@auth_router.get('/verify/{token}')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_email = token_data.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_service.update_user(user,{'is_verified':True},session)
    
    return JSONResponse(
        content={"message": "Email verified successfully"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid),'role':user.role}
            )
            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password"
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_detail: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_detail["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_detail["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get('/me',response_model=UserBooksModel)
async def get_user(user = Depends(get_current_user),_:bool=Depends(role_checker)):
    return user


@auth_router.get("/logout")
async def revoke_token(token_detail: dict = Depends(AccessTokenBearer())):
    jti = token_detail["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Loggout out successfully"}, status_code=status.HTTP_200_OK
    )


"""
1. Provide the email -> password reset request
2. Send password link
3. Reset password -> password reset confirmation

"""

@auth_router.post('/password-reset-request')
async def password_reset_request(email_data:PasswordResetRequestModel,session:AsyncSession = Depends(get_session)):
    email = email_data.email
    
    user_exists = await user_service.user_exists(email, session)

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email doesn't exist on our database!",
        )

    
    token = create_url_safe_token({"email":email})
    
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    
    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> reset your password</p>
    """
    message = create_message(recipients=[email], subject="Reset your password", body=html_message)
    
    await mail.send_message(message)

    return JSONResponse(
        content={
            "message":"Please check your email to reset your password",
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token: str, passwords:PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if  new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
        
    
    token_data = decode_url_safe_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_email = token_data.get('email')

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    passwd_hash = generate_password_hash(new_password)

    await user_service.update_user(user,{'password_hash': passwd_hash},session)
    
    return JSONResponse(
        content={"message": "Password reset successfully"},
        status_code=status.HTTP_200_OK,
    )


