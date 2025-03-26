import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from ml_model import HabitAnalyzer
import datetime

# Initialize Firebase
cred = credentials.Certificate("/Users/dminnakhmetova/AI-Habit-Tracker/backend/firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Flask
app = Flask(__name__)
analyzer = HabitAnalyzer()

@app.route('/api/habits', methods=['POST'])
def create_habit():
    try:
        data = request.json
        habit_ref = db.collection('habits').document()
        
        habit_data = {
            'habit_id': habit_ref.id,
            'user_id': data['user_id'],
            'selected_time': data['selected_time'],  # Format: "HH:MM"
            'actual_time': [],
            'streak': 0,
            'success_rate': 0.0,
            'avg_deviation': 0.0,
            'recommended_time': data['selected_time']
        }
        habit_ref.set(habit_data)
        return jsonify({'success': True, 'habit_id': habit_ref.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/habits/<habit_id>/track', methods=['POST'])
def track_habit(habit_id):
    try:
        data = request.json
        actual_time = data['actual_time']  # Format: "HH:MM"
        
        habit_ref = db.collection('habits').document(habit_id)
        habit = habit_ref.get().to_dict()
        
        # Update actual times
        habit['actual_time'].append(actual_time)
        
        # Analyze with ML model
        analysis = analyzer.analyze_habit(habit)
        
        # Update habit data
        update_data = {
            'actual_time': habit['actual_time'],
            'streak': analysis['streak'],
            'success_rate': analysis['success_rate'],
            'avg_deviation': analysis['avg_deviation'],
            'recommended_time': analysis['recommended_time']
        }
        habit_ref.update(update_data)
        
        return jsonify({'success': True, 'analysis': update_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/habits/<habit_id>', methods=['GET'])
def get_habit(habit_id):
    try:
        habit = db.collection('habits').document(habit_id).get().to_dict()
        if habit:
            return jsonify(habit), 200
        return jsonify({'error': 'Habit not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/', methods=['GET'])
def home():
    return "Habit Tracker API is running!", 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
    