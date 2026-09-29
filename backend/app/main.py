from fastapi import FastAPI
from .api.v1.api import api_router
from .core.config import settings
from .core.database import engine
from .models import base

# Optional: Ensure tables are created (we already did via seed)
# base.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to Phone Management API"}
