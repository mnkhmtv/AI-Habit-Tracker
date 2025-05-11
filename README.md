# AI-Powered Habit Tracker (HabitTrack)

To use this project proceed with following steps:

   ```
   git clone https://github.com/yourusername/AI-Habit-Tracker.git
   cd AI-Habit-Tracker
   ```

   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

   ```
   pip install -r requirements.txt
   ```

   ```
   streamlit run app.py
   ```


```
AI-Habit-Tracker/
├── backend/
│   ├── database.py      # Операции с базой данных
│   ├── ml_engine.py     # ML
│   └── utils.py         # Служебные функции
├── frontend/
│   ├── auth.py          # Представления входа/регистрации
│   ├── dashboard.py     # Дашборд отслеживания привычек
│   ├── profile.py       # Страница профиля пользователя
│   ├── recommendations.py # Представления рекомендаций привычек
│   └── tracker.py       # Дополнительные представления трекера
├── datasets/
│   ├── survey_data.csv   # Данные для обучения профиля пользователя
│   └── habits_catalog.csv # Каталог привычек
├── data/                 # Директория для хранения базы данных
│   └── habit_tracker.db  # SQLite база данных
├── app.py                # Точка входа в приложение
└── requirements.txt      # Зависимости
```
