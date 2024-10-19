from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

error_log = []

@app.route('/')
def home():
    return "Hello Flask!"

# SDK posts to this route (using array for now; will switch to postgres)
@app.route('/api/errors', methods=['POST'])
def log_error():
    error_data = request.json
    error_log.append(error_data)

    print('current errors count:', len(error_log));
    return jsonify({"message": "Error logged successfully", "data": error_data }), 201

#react frontend makes get request to this route for error messages
@app.route('/api/errors', methods=['GET'])
def get_errors():
    return jsonify(error_log), 200

if __name__ == '__main__':
    app.run(debug=True)