from jose import jwt, JWTError
from fastapi import Header, HTTPException
import base64

SECRET_KEY_STR = "148ea99d07eaf5c012e37afac84eeeef4f9af015ae40eaebf67c9ac348594adb"

# Base64 decode the key
SECRET_KEY = base64.b64decode(SECRET_KEY_STR)
ALGORITHM = "HS256"

def get_user_id_from_token(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")  # extract user_id claim
        if not user_id:
            raise HTTPException(status_code=401, detail="user_id not found in token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
