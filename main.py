# app/main.py
from fastapi import FastAPI
from app.user.router import api_router as user_router
from app.api.api_router import api_router as ai_api_router  # <- note change here
from app.analysis.prediction_router import api_router as prediction_router
from app.applications.apply_router import api_router as apply_router
from app.qrcode.qr_router import api_router as qr_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My FastAPI App")

# include user routes (your existing user router)
app.include_router(user_router)
app.include_router(prediction_router, prefix="/analysis")
app.include_router(apply_router, prefix="/applications")
# include the AI routes under /api
app.include_router(ai_api_router, prefix="/api")
app.include_router(qr_router, prefix="/qrcode")
# app.include_router(ai_api_router, prefix="/api")

origins = [
    "http://localhost",  # your frontend on same machine
    "http://localhost:3000",  # if using React/Next.js dev server
    "http://192.168.0.115:3000",  # example: other device on LAN
    "http://192.168.0.115",      # just IP access
    "*"  # allow all origins (optional, for testing)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow GET, POST, etc.
    allow_headers=["*"],          # Allow all headers
)

@app.get("/")
async def read_root():
    return {"hello": "world"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    print("request recieved sucessfully")
    return {"item_id": 3, "q": 2}
