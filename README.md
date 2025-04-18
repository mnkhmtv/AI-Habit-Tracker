# AI-Powered Habit Tracker

An AI-powered habit tracking application built with Streamlit that recommends personalized habits and helps users maintain consistency.

## Features

- **User Registration**: Collect user preferences and goals
- **AI Habit Recommendations**: Get personalized habit suggestions based on your profile
- **Habit Tracking**: Track your daily habits and build streaks
- **Analytics**: View your progress with interactive charts
- **Time Optimization**: AI suggests optimal times for habits based on your usage patterns

## Human-AI Interaction Design Principles

This application implements key principles of Human-AI Interaction Design:

### Interpretability
- The ML recommendation system explains why habits are recommended
- Clear visualization of data and decision patterns
- Transparent AI suggestions with reasoning

### Usability & Accessibility
- Intuitive UI with clear navigation
- High contrast mode support
- Screen reader compatibility
- Responsive design for different devices

### Ethical Considerations
- Privacy-focused (data stored locally)
- User control over recommendations
- Opt-in data collection for improvements
- No dark patterns to manipulate user behavior

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **ML**: scikit-learn, pandas, numpy
- **Data Visualization**: Plotly
- **Database**: SQLite

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/username/AI-Habit-Tracker.git
   cd AI-Habit-Tracker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run main.py
   ```

## Usage Guide

1. **Register/Login**: Create an account or log in
2. **Profile Setup**: Enter your preferences and goals
3. **Habit Selection**: Choose from AI-recommended habits or create your own
4. **Daily Tracking**: Check off completed habits on the dashboard
5. **Analytics**: View your progress and streaks
6. **Optimize**: Apply AI-suggested time optimizations

## Project Structure

```
AI-Habit-Tracker/
├── backend/
│   ├── database.py      # Database operations
│   ├── ml_engine.py     # ML recommendation engine
│   └── utils.py         # Utility functions
├── frontend/
│   ├── auth.py          # Login/registration views
│   ├── dashboard.py     # Habit tracking dashboard
│   └── recommendations.py # Habit recommendation views
├── datasets/
│   ├── survey_data.csv  # User profile training data
│   └── habits_catalog.csv # Habits catalog
├── main.py              # Main application entry point
└── requirements.txt     # Dependencies
```
