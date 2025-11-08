from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from perplexity import Perplexity
import pymysql
from datetime import datetime, timedelta

# --- Initialize Perplexity client ---
client = Perplexity(api_key=os.environ.get("PERPLEXITY_API_KEY"))

router = APIRouter()

def get_db_connection():
    return pymysql.connect(
        host='192.168.0.153',  # IP only
        port=3306,
        user='root',
        password='secret',
        database='vaccination'
    )

def get_weekly_sums(vaccine_id=None, center_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.today()
    weekly_sums = []

    # Loop for last 10 weeks
    for i in range(10, 0, -1):  # 10 weeks ago to 1 week ago
        end_date = today - timedelta(weeks=i-1)
        start_date = end_date - timedelta(weeks=1)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Build WHERE clause
        conditions = ["vaccination_date >= %s", "vaccination_date < %s"]
        params = [start_str, end_str]

        if vaccine_id is not None:
            conditions.append("vaccine_id = %s")
            params.append(vaccine_id)
        if center_id is not None:
            conditions.append("center_id = %s")
            params.append(center_id)

        where_clause = " AND ".join(conditions)

        # Count appointments
        cursor.execute(f"SELECT COUNT(*) FROM appointment WHERE {where_clause}", tuple(params))
        appt_count = cursor.fetchone()[0]
        weekly_sums.append(appt_count)

    # Use Perplexity API to predict next week's value
    completion = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "user",
                "content": f"Here is the value of last 10 weeks vaccination for a specific area, starting from 10 week to last week: {weekly_sums}. Predict the vaccination demand for next week, only the value, nothing else. not even a dot or comma, just give me the value, not a word extra"
            }
        ]
    )
    predicted_value = int(completion.choices[0].message.content.strip())

    weekly_sums.append(predicted_value)  

    cursor.close()
    conn.close()

    return weekly_sums


# --- Pydantic model for request ---
class PredictionRequest(BaseModel):
    center_id: int
    vaccine_id: int

# --- Main endpoint ---
@router.post("")
async def prediction(request: PredictionRequest):
    if not request.center_id or not request.vaccine_id:
        raise HTTPException(status_code=400, detail="Missing 'center_id' or 'vaccine_id'")

    answer = get_weekly_sums(request.center_id, request.vaccine_id)
    return {"predicted_value": answer}
