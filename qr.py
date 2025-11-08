from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.responses import StreamingResponse
import pyqrcode
import io
import base64
from jose import jwt, JWTError
router = APIRouter()
SECRET_KEY_STR = "148ea99d07eaf5c012e37afac84eeeef4f9af015ae40eaebf67c9ac348594adb"

# Base64 decode the key
SECRET_KEY = base64.b64decode(SECRET_KEY_STR)
ALGORITHM = "HS256"



def get_nid_or_birth_registration_no_from_token(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nid_or_birth_registration_no = payload.get("userId")
        if not nid_or_birth_registration_no:
            raise HTTPException(status_code=401, detail="nid_or_birth_registration_no not found in token")
        return nid_or_birth_registration_no
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.get("")

async def generate_qr(authorization: str = Header(...)):
    try:
        user_id = get_nid_or_birth_registration_no_from_token(authorization)

        # Generate QR code from user_id
        
        qr = pyqrcode.create(str(user_id))
        
        # Write to in-memory PNG
        buffer = io.BytesIO()
        qr.png(buffer, scale=6)
        buffer.seek(0)

        # Return as image/png stream
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
