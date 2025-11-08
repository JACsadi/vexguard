from flask import Flask, request, jsonify
import pymysql
from datetime import datetime, timedelta
import os
from perplexity import Perplexity

client = Perplexity(api_key=os.environ.get("PERPLEXITY_API_KEY"))

app = Flask(__name__)


# --- Database connection function ---
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Stick2002#',
        database='my_database'
    )

# --- Helper function to calculate weekly sums ---
def get_weekly_sums(vaccine_id=None, center_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.today()
    weekly_sums = []

    for i in range(10, 1, -1):  # 10 weeks ago to 1 week ago
        end_date = today - timedelta(weeks=i-1)
        start_date = end_date - timedelta(weeks=1)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Build dynamic WHERE clause
        conditions = ["date >= %s", "date < %s"]
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

        # Count waiting list
        cursor.execute(f"SELECT COUNT(*) FROM waiting_list WHERE {where_clause}", tuple(params))
        wait_count = cursor.fetchone()[0]
        # if(wait_count+appt_count==0):
            # break
        weekly_sums.append(appt_count + wait_count)
    # print(weekly_sums)
    completion = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": f"here is the value of last 10 weeks , vaccination of a specific area ,, given in order  x week ago, ...,  2 weeks ago, 1 week ago-> {weekly_sums} . predict the vaccination demand for next week, only the value nothing else . use data science and ml model to predict, please do not write anything but the value not even a comma or fullstop just the value"}
        ]
    )
    predicted_value = int(completion.choices[0].message.content.strip())

    sql = """
    UPDATE vaccine_table
    SET predicted = %s
    WHERE vaccine_id = %s AND center_id = %s;
    """

    cursor.execute(sql, (predicted_value, vaccine_id, center_id))
    conn.commit()  # make sure to commit the changes
    # cursor.execute(f"")
    # SET predicted = 150
    # WHERE vaccine_id = 1
    # AND center_id = 2
    # AND dose = 1;
    # WHERE {where_clause}", tuple(params))
    

    cursor.close()
    conn.close()    
    return completion.choices[0].message.content

# --- API endpoint ---
@app.route("/demand", methods=["GET"])
def demand():
    data = request.get_json()  # Get JSON body
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400
    vaccine_id = data.get("vaccine_id")
    center_id = data.get("center_id")

    # Convert to int if provided
    if vaccine_id is not None:
        vaccine_id = int(vaccine_id)
    if center_id is not None:
        center_id = int(center_id)

    result = get_weekly_sums(vaccine_id, center_id)

    return jsonify({"weekly_sums": result})

if __name__ == "__main__":
    app.run(debug=True)
