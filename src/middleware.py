from fastapi import FastAPI,status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    # log middleware

    @app.middleware("http")
    async def custom_login(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        processing_time = time.time() - start_time

        client = request.client
        host = getattr(client, "host", "unknown") if client is not None else "unknown"
        port = getattr(client, "port", "unknown") if client is not None else "unknown"
        message = f"{host}:{port} {request.method} - {request.url.path} - {response.status_code} - completed after {processing_time}s"
        print(message)
        return response

    # authorization middleware
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "Please provide right credentials to proceed",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
            
    #     response = await call_next(request)
    #     return response
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ['*'],
        allow_methods = ['*'],
        allow_headers = ['*'],
        allow_credentials = True,
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = ['localhost','127.0.0.1']
    )
