from fastapi import APIRouter
from . import dashboard 
api_router = APIRouter()

# Include each router with optional prefix and tags
# api_router.include_router(items.router)       # items.py has its own prefix
api_router.include_router(dashboard.router)        