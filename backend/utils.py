import uuid
import re
from datetime import datetime
import pandas as pd
import streamlit as st

def generate_user_id():
    """Generate a unique user ID."""
    return str(uuid.uuid4())

def validate_email(email):
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_time_format(time_str):
    """Validate time format (HH:MM)."""
    pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
    return bool(re.match(pattern, time_str))

def format_time_string(time_str):
    """Format time string to HH:MM format."""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        return time_obj.strftime('%H:%M')
    except ValueError:
        return None

def load_dataset(file_path):
    """Load and return a dataset from CSV."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {str(e)}")
        return None

def get_age_ranges():
    """Return standard age ranges for the application."""
    return ['18-25', '26-35', '36-45', '45+']

def get_gender_options():
    """Return standard gender options for the application."""
    return ['Мужской', 'Женский', 'Другое', 'Предпочитаю не указывать']

def get_time_commitment_options():
    """Return standard time commitment options."""
    return ['5 минут', '15 минут', '30 минут', '1 час']

def get_preferred_time_options():
    """Return standard preferred time options."""
    return ['Утро', 'День', 'Вечер', 'Не важно']

def get_existing_habits_options():
    """Return common existing habits options."""
    return [
        'Здоровое питание',
        'Регулярные тренировки',
        'Чтение',
        'Медитация',
        'Ранний подъем',
        'Правильное распределение времени',
        'Ведение дневника',
        'Экономия денег',
        'Отслеживание расходов',
        'Регулярный режим сна'
    ]

def get_improvement_areas_options():
    """Return standard improvement areas options."""
    return [
        'Физическое здоровье',
        'Ментальное здоровье',
        'Продуктивность',
        'Финансы',
        'Отношения'
    ]

def get_barriers_options():
    """Return standard barriers options."""
    return [
        'Нехватка времени',
        'Нет мотивации',
        'Непонятно с чего начать',
        'Страх неудачи',
        'Нет поддержки',
        'Слишком сложно'
    ]

def display_streak_icon(streak):
    """Display a streak icon and count."""
    if streak == 0:
        return "🔄 Начните свою серию!"
    elif streak < 3:
        return f"🔥 {streak} дн. подряд"
    elif streak < 7:
        return f"🔥🔥 {streak} дн. подряд"
    else:
        return f"🔥🔥🔥 {streak} дн. подряд"

def convert_time_to_minutes(time_str):
    """Convert a time string (like '30 minutes') to minutes as an integer."""
    if not time_str:
        return 0
    
    match = re.search(r'(\d+)', time_str)
    if match:
        return int(match.group(1))
    return 0 