from fastapi import APIRouter
from .apply import router as apply_router

# This `api_router` matches the pattern used in your existing user router
api_router = APIRouter()
# no additional prefix so ai_chat route remains available at /api/ai-chat (main adds /api)
# api_router.include_router(ai_chat_router)
api_router.include_router(apply_router, prefix="/apply", tags=["apply"])