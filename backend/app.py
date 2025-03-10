from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# set CORS for all domains
CORS(app)

@app.route('/')
def home():
    return jsonify(message="Hello, AI Habit Tracker!")

if __name__ == '__main__':
    app.run(debug=True)