# app/api/ai_router.py
from fastapi import APIRouter
from .ai_chat import router as ai_chat_router

# This `api_router` matches the pattern used in your existing user router
api_router = APIRouter()
# no additional prefix so ai_chat route remains available at /api/ai-chat (main adds /api)
# api_router.include_router(ai_chat_router)
api_router.include_router(ai_chat_router, prefix="/ai-chat", tags=["AI Chat"])