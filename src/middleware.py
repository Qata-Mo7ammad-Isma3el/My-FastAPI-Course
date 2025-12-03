from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import time
import logging


logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        message = f"Request: {request.method} - {request.url.path} - {response.status_code} completed in {process_time:.4f} seconds |"
        length = len(message)
        print("*" * (length))
        print(" " * (length - 1) + "|")
        print(message)
        print(" " * (length - 1) + "|")
        print("*" * (length))
        # logging.info(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


## simple authorization middleware example
# > @app.middleware("http")
# > async def authorization(request: Request, call_next):
# >     if "Authorization" not in request.headers:
# >         return JSONResponse(
# >             status_code=status.HTTP_401_UNAUTHORIZED,
# >             content={
# >                 "message": "Not authorized",
# >                 "resolution": "Please Provide Authorization header",
# >             },
# >         )
# >     response = await call_next(request)
# >     return response
