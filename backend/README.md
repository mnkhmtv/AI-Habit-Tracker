# AI Habit Tracker Backend

A Flask-based backend for tracking user habits, analyzing execution times, and recommending optimal schedules using AI. Built with Firebase Firestore for storage and scikit-learn for machine learning.

## Features
- Users manually select a preferred habit time.
- System tracks actual execution times.
- AI analyzes data and suggests time adjustments if habits are consistently performed at different times.

## Prerequisites
- Python 3.8+
- Firebase project with Firestore enabled
- Firebase Admin SDK JSON file

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mnkhmtv/AI-Habit-Tracker/
   cd AI-Habit-Tracker
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install firebase-admin flask scikit-learn numpy pandas
   ```

4. **Configure Firebase**:
   - Go to [Firebase Console](https://console.firebase.google.com/).
   - Create a project (e.g., `ai-habit-tracker-873c2`).
   - Enable Firestore in test mode.
   - Download the Admin SDK JSON from Project Settings > Service Accounts.
   - Place it in the project root (e.g., `firebase-adminsdk.json`).
   - Update `main.py` with the correct path:
     ```python
     cred = credentials.Certificate("./firebase-adminsdk.json")
     ```

## Running the Backend

1. **Start the Server**:
   ```bash
   python main.py
   ```
   - Runs on `http://127.0.0.1:8080`.

2. **API Endpoints**:
   - **Create a Habit**:
     ```
     POST /api/habits
     Body: {"user_id": "user123", "selected_time": "09:00"}
     ```
   - **Track a Habit**:
     ```
     POST /api/habits/<habit_id>/track
     Body: {"actual_time": "09:05"}
     ```
   - **Get Habit Details**:
     ```
     GET /api/habits/<habit_id>
     ```

3. **Example Usage**:
   ```bash
   curl -X POST http://127.0.0.1:8080/api/habits \
   -H "Content-Type: application/json" \
   -d '{"user_id": "user123", "selected_time": "09:00"}'
   ```

## Generating Sample Data
To populate the database with test data:
1. Run `generate_data.py` (see code in documentation).
2. Export to CSV with the provided script.

## Training the Model
- The ML model (KMeans) trains on-the-fly in `ml_model.py`.
- To pre-train with a CSV, use `train_model.py`:
  ```bash
  python train_model.py
  ```

## File Structure
```
AI-Habit-Tracker/
├── main.py          # Flask API backend
├── ml_model.py      # ML analysis logic
├── train_model.py   # Model training script
├── firebase-adminsdk.json  # Firebase credentials
```

## Troubleshooting
- **404 Database Error**: Ensure Firestore is enabled in Firebase.
- **Permission Denied**: Update Firestore rules to `allow read, write: if true;` for testing.
- **Port Conflict**: Change port in `main.py` (e.g., `app.run(port=8081)`).

## Future Improvements
- Build a frontend for user interaction.
- Enhance ML with time series analysis.

## License
MIT License
```