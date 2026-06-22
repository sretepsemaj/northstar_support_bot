from fastapi import FastAPI
from backend.api.routes import chat, health
from backend.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health.router)
    app.include_router(chat.router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} API is running"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("backend.main:app", host=settings.app_host, port=settings.app_port, reload=True)
