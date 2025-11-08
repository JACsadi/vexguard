from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
import pymysql

router = APIRouter()

def get_db_connection():
    return pymysql.connect(
        host='192.168.0.153',
        port=3306,
        user='root',
        password='secret',
        database='vaccination',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

# All fields required, vaccination_date is a date
class AppointmentCreate(BaseModel):
    appointment_id: int
    user_id: int
    vaccine_id: str
    dose_id: str
    vaccination_date: date
    status: str
    center_id: int
    staff_id: int

@router.post("")
async def insert_appointment(request: AppointmentCreate):
    # Build SQL (all fields are provided)
    sql = """
        INSERT INTO appointment (
            appointment_id,
            user_id,
            vaccine_id,
            dose_id,
            vaccination_date,
            status,
            center_id,
            staff_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        request.appointment_id,
        request.user_id,
        request.vaccine_id,
        request.dose_id,
        request.vaccination_date.strftime("%Y-%m-%d"),  # date -> string for MySQL
        request.status,
        request.center_id,
        request.staff_id,
    )

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        return {"success": 1}
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return {"success": 0, "error": str(e)}
    finally:
        if conn:
            conn.close()
