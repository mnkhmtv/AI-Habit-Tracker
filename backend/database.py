import sqlite3
import os
import pandas as pd
from datetime import datetime
import hashlib
import uuid
import bcrypt

def initialize_database():
    """Initialize the database connection and create tables if they don't exist."""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT,
        password_hash TEXT,
        full_name TEXT,
        bio TEXT,
        notification_settings TEXT,
        created_at INTEGER
    )
    ''')
    
    # Create habits table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        category TEXT,
        description TEXT,
        time_required TEXT,
        difficulty TEXT,
        selected_time TEXT,
        created_at INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create habit_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        user_id TEXT,
        date TEXT,
        completed INTEGER DEFAULT 1,
        actual_time TEXT,
        created_at INTEGER,
        FOREIGN KEY (habit_id) REFERENCES habits (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, email, password):
    """Create a new user in the database with hashed password."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    
    # Hash password and store it in the gender field as a workaround
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Current timestamp for registration date
    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute('''
        INSERT INTO users (user_id, name, age, gender, registration_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, registration_date))
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        # Username already exists
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    """Get user data by username."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Try to find user using the 'name' column instead of 'username'
    cursor.execute('SELECT * FROM users WHERE name = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        # Map to match the expected structure in the rest of the code
        columns = ['id', 'username', 'email', 'password_hash', 'full_name', 'bio', 'notification_settings', 'created_at']
        db_columns = ['user_id', 'name', 'age', 'gender', 'existing_habits', 'improvement_areas', 
                     'time_commitment', 'preferred_time', 'barriers', 'registration_date']
        
        # Create a mapping of values
        user_dict = dict(zip(db_columns, user))
        
        # Map to the expected structure
        result = {
            'id': user_dict['user_id'],
            'username': user_dict['name'],
            'email': '',  # Not in original schema
            'password_hash': user_dict.get('gender', ''),  # Storing password in gender field for demo
            'created_at': int(datetime.now().timestamp())  # Use current time as placeholder
        }
        
        return result
    return None

def get_user_by_id(user_id):
    """Get user data by ID."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        # Map columns from the database schema to the expected structure
        db_columns = ['user_id', 'name', 'age', 'gender', 'existing_habits', 'improvement_areas', 
                     'time_commitment', 'preferred_time', 'barriers', 'registration_date']
        
        # Create a mapping of values
        user_dict = dict(zip(db_columns, user))
        
        # Map to the expected structure
        result = {
            'id': user_dict['user_id'],
            'username': user_dict['name'],
            'email': user_dict.get('age', ''),  # Using age field for email
            'password_hash': user_dict.get('gender', ''),  # Using gender field for password hash
            'full_name': user_dict.get('name', ''),  # Reusing name as full_name
            'bio': '',  # Not in original schema
            'notification_settings': user_dict.get('improvement_areas', '{}'),  # Using improvement_areas for settings
            'created_at': int(datetime.now().timestamp())  # Use current time as placeholder
        }
        
        return result
    return None

def verify_password(password, stored_hash):
    """Verify a password against a stored hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except:
        # If there's any error in verification (e.g. invalid hash format), return False
        return False

def update_user_profile(user_id, **kwargs):
    """Update user profile data."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Map fields from the expected schema to the actual database schema
    field_mapping = {
        'full_name': 'name',
        'email': 'age',
        'bio': 'existing_habits',
        'notification_settings': 'improvement_areas'
    }
    
    fields = []
    values = []
    
    for key, value in kwargs.items():
        if key in field_mapping:
            fields.append(f"{field_mapping[key]} = ?")
            values.append(value)
    
    if not fields:
        conn.close()
        return False
    
    values.append(user_id)
    
    try:
        cursor.execute(f'''
        UPDATE users 
        SET {', '.join(fields)}
        WHERE user_id = ?
        ''', values)
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except:
        conn.close()
        return False

def add_user_habit(user_id, name, description, category, time_required, difficulty, selected_time):
    """Add a new habit for a user."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Use current datetime for the created_date
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
    INSERT INTO habits (user_id, habit_name, category, description, time_required, difficulty, selected_time, created_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, category, description, time_required, difficulty, selected_time, created_date))
    
    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return habit_id

def get_user_habits(user_id):
    """Get all habits for a specific user."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM habits WHERE user_id = ? ORDER BY created_date DESC', (user_id,))
    habits = cursor.fetchall()
    
    conn.close()
    
    if habits:
        # Map database schema columns to expected columns
        db_columns = ['habit_id', 'user_id', 'habit_name', 'category', 'description', 
                     'time_required', 'difficulty', 'selected_time', 'created_date']
        
        # Map to expected column structure
        result = []
        for habit in habits:
            habit_dict = dict(zip(db_columns, habit))
            result.append({
                'id': habit_dict['habit_id'],
                'user_id': habit_dict['user_id'],
                'name': habit_dict['habit_name'],
                'category': habit_dict['category'],
                'description': habit_dict['description'],
                'time_required': habit_dict['time_required'],
                'difficulty': habit_dict['difficulty'],
                'selected_time': habit_dict['selected_time'],
                'created_at': habit_dict['created_date']
            })
        return result
    return []

def delete_habit(habit_id):
    """Delete a habit and all its logs."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Delete the habit logs first
    cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
    
    # Then delete the habit
    cursor.execute('DELETE FROM habits WHERE habit_id = ?', (habit_id,))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_habit(habit_id, name, description, time_required, difficulty, selected_time):
    """Update a habit's details."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE habits 
    SET habit_name = ?, description = ?, time_required = ?, difficulty = ?, selected_time = ?
    WHERE habit_id = ?
    ''', (name, description, time_required, difficulty, selected_time, habit_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def add_habit_log(user_id, habit_id, date, completed=True, actual_time=None):
    """Add or update a habit log entry."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Format date to YYYY-MM-DD if it's a datetime object
    if isinstance(date, datetime):
        date = date.strftime('%Y-%m-%d')
    
    # Check if there's already a log for this habit and date
    cursor.execute('''
    SELECT tracking_id FROM habit_tracking 
    WHERE habit_id = ? AND user_id = ? AND date = ?
    ''', (habit_id, user_id, date))
    
    existing_log = cursor.fetchone()
    
    if existing_log:
        # Update existing log
        cursor.execute('''
        UPDATE habit_tracking 
        SET completed = ?, actual_time = ?
        WHERE tracking_id = ?
        ''', (1 if completed else 0, actual_time, existing_log[0]))
    else:
        # Create new log
        cursor.execute('''
        INSERT INTO habit_tracking (habit_id, user_id, date, completed, actual_time)
        VALUES (?, ?, ?, ?, ?)
        ''', (habit_id, user_id, date, 1 if completed else 0, actual_time))
    
    conn.commit()
    conn.close()
    
    # Update streak data after logging
    update_habit_streak(habit_id, user_id)
    
    return True

def get_habit_logs(user_id, habit_id, date=None, start_date=None, end_date=None):
    """Get habit logs for a specific habit and date range."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    query = 'SELECT * FROM habit_tracking WHERE user_id = ? AND habit_id = ?'
    params = [user_id, habit_id]
    
    if date:
        # Format date to YYYY-MM-DD if it's a datetime object
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        query += ' AND date = ?'
        params.append(date)
    
    if start_date and end_date:
        # Format dates to YYYY-MM-DD if they're datetime objects
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
        query += ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    
    cursor.execute(query, params)
    logs = cursor.fetchall()
    
    conn.close()
    
    if logs:
        # Map from schema to expected structure
        db_columns = ['tracking_id', 'habit_id', 'user_id', 'date', 'completed', 'actual_time']
        result = []
        for log in logs:
            log_dict = dict(zip(db_columns, log))
            result.append({
                'id': log_dict['tracking_id'],
                'habit_id': log_dict['habit_id'],
                'user_id': log_dict['user_id'],
                'date': log_dict['date'],
                'completed': bool(log_dict['completed']),
                'actual_time': log_dict['actual_time'],
                'created_at': None  # Not in the schema, but needed for compatibility
            })
        return result
    return []

def update_habit_streak(habit_id, user_id):
    """Update streak data for a habit."""
    # This function would calculate and update the current streak
    # Since the streak is calculated on-the-fly in get_streak_data, this is a placeholder
    return True

def get_streak_data(user_id, habit_id):
    """Get current and maximum streak for a habit."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    # Get all completed logs for this habit, ordered by date
    cursor.execute('''
    SELECT date FROM habit_tracking 
    WHERE habit_id = ? AND user_id = ? AND completed = 1
    ORDER BY date ASC
    ''', (habit_id, user_id))
    
    logs = cursor.fetchall()
    conn.close()
    
    if not logs:
        return {'current_streak': 0, 'max_streak': 0}
    
    # Convert date strings to datetime objects
    log_dates = [datetime.strptime(log[0], '%Y-%m-%d').date() for log in logs]
    
    # Calculate current streak
    current_streak = 0
    today = datetime.now().date()
    
    # Get the most recent log date
    most_recent_date = max(log_dates)
    
    # Check if the most recent log is from today or yesterday (to maintain streak)
    if (today - most_recent_date).days <= 1:
        current_streak = 1
        
        # Count consecutive days backwards from most recent
        for i in range(len(log_dates) - 1, 0, -1):
            if (log_dates[i] - log_dates[i-1]).days == 1:
                current_streak += 1
            else:
                break
    
    # Calculate max streak
    max_streak = 0
    current_run = 1
    
    for i in range(1, len(log_dates)):
        if (log_dates[i] - log_dates[i-1]).days == 1:
            current_run += 1
        else:
            max_streak = max(max_streak, current_run)
            current_run = 1
    
    max_streak = max(max_streak, current_run)
    
    return {'current_streak': current_streak, 'max_streak': max_streak}

def get_habit_entries(habit_id):
    """Get all entries for a specific habit."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM habit_logs WHERE habit_id = ? ORDER BY date DESC', (habit_id,))
    entries = cursor.fetchall()
    
    conn.close()
    
    if entries:
        columns = ['id', 'habit_id', 'user_id', 'date', 'completed', 'actual_time', 'created_at']
        return [dict(zip(columns, entry)) for entry in entries]
    return []

def get_user_data(user_id):
    """Get all user data including profile and preferences."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Remove sensitive information like password hash
    if 'password_hash' in user:
        del user['password_hash']
    
    return user

def get_user_stats(user_id):
    """Get user statistics for habits and progress."""
    conn = sqlite3.connect('data/habit_tracker.db')
    cursor = conn.cursor()
    
    stats = {}
    
    # Get all habits for this user
    cursor.execute('SELECT id FROM habits WHERE user_id = ?', (user_id,))
    habits = cursor.fetchall()
    
    # Total habits
    stats['total_habits'] = len(habits)
    
    # If no habits, return basic stats
    if stats['total_habits'] == 0:
        conn.close()
        return stats
    
    # Get habit logs for all user habits
    habit_ids = [habit[0] for habit in habits]
    placeholders = ','.join(['?' for _ in habit_ids])
    
    cursor.execute(f'''
    SELECT COUNT(*) FROM habit_logs 
    WHERE user_id = ? AND habit_id IN ({placeholders})
    ''', (user_id, *habit_ids))
    
    total_logs = cursor.fetchone()[0]
    
    # Calculate completion rate (simplified)
    stats['completion_rate'] = 0
    if stats['total_habits'] > 0:
        # This is a simplified calculation - in a real app, you'd consider the expected
        # frequency of each habit over a specific time period
        stats['completion_rate'] = min(100, (total_logs / (stats['total_habits'] * 30)) * 100)
    
    # Current streak (simplified)
    stats['current_streak'] = 0
    
    # Get habit performance details
    habit_performance = []
    
    # Get detailed info for each habit
    cursor.execute(f'''
    SELECT h.id, h.name, COUNT(hl.id) as log_count 
    FROM habits h 
    LEFT JOIN habit_logs hl ON h.id = hl.habit_id 
    WHERE h.user_id = ?
    GROUP BY h.id
    ''', (user_id,))
    
    habit_details = cursor.fetchall()
    
    for habit_id, habit_name, log_count in habit_details:
        # For each habit, calculate tracking days, completion rate, etc.
        # This is simplified - in a real app you'd do more detailed calculations
        tracking_days = 30  # Placeholder for real calculation
        completion_pct = min(100, (log_count / tracking_days) * 100) if tracking_days > 0 else 0
        max_streak = 0  # Placeholder for real streak calculation
        
        habit_performance.append([
            habit_name,
            tracking_days,
            log_count,
            completion_pct,
            max_streak
        ])
    
    stats['habit_performance'] = habit_performance
    
    conn.close()
    return stats

class Database:
    def __init__(self, db_name='habit_tracker.db'):
        # Create database directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        self.db_path = os.path.join('data', db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            age TEXT,
            gender TEXT,
            existing_habits TEXT,
            improvement_areas TEXT,
            time_commitment TEXT,
            preferred_time TEXT,
            barriers TEXT,
            registration_date TEXT
        )
        ''')
        
        # Create habits table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            habit_name TEXT,
            category TEXT,
            description TEXT,
            time_required TEXT,
            difficulty TEXT,
            selected_time TEXT,
            created_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # Create habit_tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_tracking (
            tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            user_id TEXT,
            date TEXT,
            completed INTEGER,
            actual_time TEXT,
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, name, age, gender, existing_habits, improvement_areas, 
                 time_commitment, preferred_time, barriers):
        cursor = self.conn.cursor()
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO users (user_id, name, age, gender, existing_habits, improvement_areas, 
                          time_commitment, preferred_time, barriers, registration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, age, gender, existing_habits, improvement_areas, 
              time_commitment, preferred_time, barriers, registration_date))
        
        self.conn.commit()
        return user_id
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, user))
        return None
    
    def add_habit(self, user_id, habit_name, category, description, time_required, 
                 difficulty, selected_time):
        cursor = self.conn.cursor()
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO habits (user_id, habit_name, category, description, time_required, 
                          difficulty, selected_time, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, habit_name, category, description, time_required, 
              difficulty, selected_time, created_date))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_habits(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM habits WHERE user_id = ?', (user_id,))
        habits = cursor.fetchall()
        
        if habits:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, habit)) for habit in habits]
        return []
    
    def get_habit(self, habit_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM habits WHERE habit_id = ?', (habit_id,))
        habit = cursor.fetchone()
        
        if habit:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, habit))
        return None
    
    def update_habit(self, habit_id, habit_name=None, category=None, description=None, 
                    time_required=None, difficulty=None, selected_time=None):
        cursor = self.conn.cursor()
        current_habit = self.get_habit(habit_id)
        
        if not current_habit:
            return False
        
        habit_name = habit_name if habit_name is not None else current_habit['habit_name']
        category = category if category is not None else current_habit['category']
        description = description if description is not None else current_habit['description']
        time_required = time_required if time_required is not None else current_habit['time_required']
        difficulty = difficulty if difficulty is not None else current_habit['difficulty']
        selected_time = selected_time if selected_time is not None else current_habit['selected_time']
        
        cursor.execute('''
        UPDATE habits 
        SET habit_name = ?, category = ?, description = ?, time_required = ?, 
            difficulty = ?, selected_time = ?
        WHERE habit_id = ?
        ''', (habit_name, category, description, time_required, 
              difficulty, selected_time, habit_id))
        
        self.conn.commit()
        return True
    
    def delete_habit(self, habit_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM habits WHERE habit_id = ?', (habit_id,))
        cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def track_habit(self, habit_id, user_id, completed, actual_time=None):
        cursor = self.conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if there's already an entry for today
        cursor.execute('''
        SELECT tracking_id FROM habit_tracking 
        WHERE habit_id = ? AND user_id = ? AND date = ?
        ''', (habit_id, user_id, today))
        
        existing_entry = cursor.fetchone()
        
        if existing_entry:
            # Update existing entry
            cursor.execute('''
            UPDATE habit_tracking 
            SET completed = ?, actual_time = ?
            WHERE tracking_id = ?
            ''', (completed, actual_time, existing_entry[0]))
        else:
            # Create new entry
            cursor.execute('''
            INSERT INTO habit_tracking (habit_id, user_id, date, completed, actual_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (habit_id, user_id, today, completed, actual_time))
        
        self.conn.commit()
        return True
    
    def get_streak(self, habit_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT date, completed FROM habit_tracking 
        WHERE habit_id = ? AND user_id = ?
        ORDER BY date DESC
        ''', (habit_id, user_id))
        
        tracking_data = cursor.fetchall()
        
        if not tracking_data:
            return 0
        
        streak = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        for date, completed in tracking_data:
            if completed and (date == today or streak > 0):
                streak += 1
            else:
                break
        
        return streak
    
    def get_tracking_data(self, habit_id, user_id, days=30):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT date, completed, actual_time FROM habit_tracking 
        WHERE habit_id = ? AND user_id = ?
        ORDER BY date DESC
        LIMIT ?
        ''', (habit_id, user_id, days))
        
        tracking_data = cursor.fetchall()
        
        if tracking_data:
            columns = ['date', 'completed', 'actual_time']
            return [dict(zip(columns, data)) for data in tracking_data]
        return []
    
    def close(self):
        self.conn.close() 