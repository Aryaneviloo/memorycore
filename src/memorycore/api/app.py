from fastapi import FastAPI
from memorycore.api.routes import router


VERSION = "0.1.0"

def create_app() -> FastAPI:
    """
    Application factory: creates and configures the FASTAPI app
    
    Using a factory function (rather than module level app) makes it easier to test, tests can call create_app()
    to get a fresh instanace with test dependencies injected
    """

    app = FastAPI(
        title="MemoryCore API",
        description="Open-source memory infrastructure for AI agents",
        version=VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(router)

    return  app

app = create_app