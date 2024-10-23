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
DB_USER = os.getenv('PGUSER')
DB_PASS = os.getenv('PGPASSWORD')
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
            e.id, e.name, e.message, e.created_at, e.line_number, e.col_number, e.project_id, e.stack_trace, e.handled
        FROM error_logs e
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
                "handled": row[8]
            }

            data_log.append(error_entry)

    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500

    return jsonify(data_log), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)