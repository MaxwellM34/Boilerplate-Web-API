from fastapi import Depends, FastAPI
from tortoise.contrib.fastapi import register_tortoise

from auth import authenticate
from config import Config
from routers import users_router

app = FastAPI(title="Base API", debug=Config.DEBUG)
app.include_router(users_router, prefix=Config.API_PREFIX)
register_tortoise(
    app,
    config=Config.TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a placeholder response for a starting project."""
    return {"message": "Base API is running."}


@app.get("/health")
def health(current_user=Depends(authenticate)) -> dict[str, str]:
    """Simple authenticated endpoint for verifying auth."""
    return {"status": "ok", "user": current_user.email}
