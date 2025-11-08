from fastapi import APIRouter, Header, HTTPException
import pymysql
from datetime import datetime, timedelta
import os
from perplexity import Perplexity
from jose import jwt, JWTError

# --- Perplexity client ---
client = Perplexity(api_key=os.environ.get("PERPLEXITY_API_KEY"))

# --- JWT config ---
import base64

SECRET_KEY_STR = "148ea99d07eaf5c012e37afac84eeeef4f9af015ae40eaebf67c9ac348594adb"

# Base64 decode the key
SECRET_KEY = base64.b64decode(SECRET_KEY_STR)
ALGORITHM = "HS256"

# --- Router ---
router = APIRouter(prefix="/user", tags=["user"])

# --- Database connection ---
def get_db_connection():
    return pymysql.connect(
        host='192.168.0.153',  # IP only
        port=3306,             # port separately
        user='root',
        password='secret',
        database='vaccination'
    )

# --- JWT helper ---
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

# --- Core logic ---
def get_completed(nid_or_birth_registration_no):
    conn = get_db_connection()
    cursor = conn.cursor()
#     completed_sql = """
#     select count(*) from appointment
#     where status = %s and nid_or_birth_registration_no = %s
#     """
#     cursor.execute(completed_sql,("completed",nid_or_birth_registration_no))
#     completed_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return 2
    # return completed_count

def get_full_name(nid_or_birth_registration_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
    SELECT full_name 
    FROM users
    WHERE nid_or_birth_registration_no = %s
    """
    cursor.execute(sql, (nid_or_birth_registration_no,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        return result[0]  # full_name
    else:
        return None  # if nid_or_birth_registration_no does not exist

def get_upcomingdose(nid_or_birth_registration_no):
    """
    Returns the number of upcoming/scheduled doses for a given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        SELECT COUNT(*) 
        FROM appointment
        WHERE user_id = %s AND status = %s
    """
    cursor.execute(sql, (nid_or_birth_registration_no, "scheduled"))
    upcoming_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return upcoming_count

def get_urgent_dose(nid_or_birth_registration_no):
    """
    Returns the number of upcoming doses for a user that are scheduled within the next 7 days.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate today's date and date 7 days from now
    today = datetime.today().date()
    week_later = today + timedelta(days=7)
    
    sql = """
        SELECT COUNT(*)
        FROM appointment
        WHERE user_id = %s
          AND status = %s
          AND vaccination_date >= %s
          AND vaccination_date <= %s
    """
    cursor.execute(sql, (nid_or_birth_registration_no, "scheduled", today, week_later))
    urgent_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return urgent_count

def get_history(nid_or_birth_registration_no):
    """
    Returns a list of all completed appointments for a given user.
    Each appointment is returned as a dictionary.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor returns rows as dicts
    
    sql = """
        SELECT *
        FROM appointment
        WHERE user_id = %s AND status = %s
        ORDER BY vaccination_date DESC
    """
    cursor.execute(sql, (nid_or_birth_registration_no, "completed"))
    history = cursor.fetchall()  # This will be a list of dictionaries
    
    cursor.close()
    conn.close()
    
    return history
def get_upcomin(nid_or_birth_registration_no):
    """
    Returns a list of all upcoming/scheduled appointments for a given user.
    Each appointment is returned as a dictionary.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor returns rows as dicts
    
    sql = """
        SELECT *
        FROM appointment
        WHERE user_id = %s AND status = %s
        ORDER BY vaccination_date ASC
    """
    cursor.execute(sql, (nid_or_birth_registration_no, "scheduled"))
    upcoming = cursor.fetchall()  # This will be a list of dictionaries
    
    cursor.close()
    conn.close()
    
    return upcoming
# --- API endpoint ---
@router.get("/dashboard")
async def dashboard(authorization: str = Header(...)):
    # nid_or_birth_registration_no = 1
    nid_or_birth_registration_no = get_nid_or_birth_registration_no_from_token(authorization)
    # insert_appointment(nid_or_birth_registration_no)
    comp = get_completed(nid_or_birth_registration_no)
    full_name = get_full_name(nid_or_birth_registration_no)
    upcoming = get_upcomingdose(nid_or_birth_registration_no)
    urgent = get_urgent_dose(nid_or_birth_registration_no)
    history = get_history(nid_or_birth_registration_no)
    future = get_upcomin(nid_or_birth_registration_no)
    return {"full_name":full_name, "nid_or_birth_registration_no": nid_or_birth_registration_no, "completed": comp,"upcoming":upcoming, "urgent": urgent, "history":history, "future":future}
    # return {"weekly_sums": predicted, "nid_or_birth_registration_no": nid_or_birth_registration_no}
    # return 2
