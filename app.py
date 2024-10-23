from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# should this be in a separate config file?
DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGHUSER')
DB_PASS = os.getenv('PGHOST')
DB_PORT = os.getenv('PGPORT')

# Function to get a database connection
# .connect returns a connection object, which is used below in get_data()
def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return connection


# should we delete this/handle / differently?
@app.route('/')
def home():
    return "Hello Flask!"

@app.route('/api/errors', methods=['GET'])
def get_data():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query for fetching data from ErrorLogs, Requests, and Promises tables
        query = """
        SELECT
            e.id, e.name, e.message, e.created_at, e.line_number, e.col_number, e.project_id, e.stack_trace,
            r.id AS request_id, r.status_code, r.status_message, r.method, r.url,
            p.id AS promise_id, p.reason
        FROM error_logs e
        LEFT JOIN requests r ON e.request_id = r.id
        LEFT JOIN promises p ON e.promise_id = p.id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        # Format the results as a list of dictionaries
        data_log = []
        for row in rows:
            error_entry = {
                "error_id": row[0],
                "name": row[1],
                "message": row[2],
                "created_at": row[3],
                "line_number": row[4],
                "col_number": row[5],
                "project_id": row[6],
                "stack_trace": row[7],
                "request": {
                    "id": row[8],
                    "status_code": row[9],
                    "status_message": row[10],
                    "method": row[11],
                    "url": row[12]
                } if row[8] else None,
                "promise": {
                    "id": row[13],
                    "reason": row[14]
                } if row[13] else None
            }
            data_log.append(error_entry)

    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500

    return jsonify(data_log), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)