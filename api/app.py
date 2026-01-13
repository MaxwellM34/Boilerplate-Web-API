from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from auth import authenticate
from config import Config
from routers import users_router


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=Config.TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if Config.DEBUG:
            print("Using DB config:", Config.TORTOISE_ORM)
        yield

    app = FastAPI(title="Base API", debug=Config.DEBUG, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_router, prefix=Config.API_PREFIX)

    init_db(app)

    @app.get("/")
    def read_root() -> dict[str, str]:
        """Return a placeholder response for a starting project."""
        return {"message": "Base API is running."}

    @app.get("/health")
    def health(current_user=Depends(authenticate)) -> dict[str, str]:
        """Simple authenticated endpoint for verifying auth."""
        return {"status": "ok", "user": current_user.email}

    return app
