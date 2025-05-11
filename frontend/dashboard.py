import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import altair as alt
from backend.database import (
    get_user_habits, 
    get_habit_logs,
    add_habit_log,
    delete_habit,
    update_habit_streak,
    get_streak_data,
    update_habit,
    add_user_habit
)

# Add parent directory to path to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Database
from backend.ml_engine import HabitRecommender
from backend.utils import display_streak_icon, validate_time_format, format_time_string


def render_dashboard():
    """Render the main dashboard for tracking habits."""
    st.title("📊 Панель управления привычками")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему для доступа к панели управления.")
        return
    
    # Welcome message with username
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете отслеживать свои привычки.")
    
    # Get user habits
    user_id = st.session_state.user_id
    habits = get_user_habits(user_id)
    
    # Quick Add Habit Section at the top
    st.subheader("🌟 Быстрое добавление привычки")
    
    # Use columns to create a compact form
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        new_habit_name = st.text_input("Название привычки", key="quick_add_name")
    
    with col2:
        new_habit_category = st.selectbox(
            "Категория",
            options=["Здоровье", "Продуктивность", "Саморазвитие", "Ментальное здоровье", "Физическое здоровье", "Другое"],
            key="quick_add_category"
        )
    
    with col3:
        if st.button("Добавить", key="quick_add_btn"):
            if new_habit_name:
                # Add new habit with minimal details
                add_user_habit(
                    user_id=user_id,
                    name=new_habit_name,
                    description=f"Привычка: {new_habit_name}",
                    category=new_habit_category,
                    time_required="5 минут",
                    difficulty="Средне",
                    selected_time="08:00"
                )
                st.success(f"Привычка '{new_habit_name}' добавлена!")
                st.rerun()
            else:
                st.error("Введите название привычки")
    
    # Quick Recommendations Section
    st.subheader("🔍 Рекомендуемые привычки")
    
    # Create a list of sample recommended habits
    recommended_habits = [
        {
            "name": "Утренняя зарядка",
            "category": "Физическое здоровье",
            "description": "5-минутная зарядка для повышения энергии"
        },
        {
            "name": "Медитация",
            "category": "Ментальное здоровье",
            "description": "10 минут медитации для снижения стресса"
        },
        {
            "name": "Питьевой режим",
            "category": "Физическое здоровье",
            "description": "Выпивать стакан воды каждые 2 часа"
        },
        {
            "name": "Чтение",
            "category": "Саморазвитие",
            "description": "Читать 10 страниц книги перед сном"
        }
    ]
    
    # Check which habits the user already has
    current_habit_names = [h['name'].lower() for h in habits] if habits else []
    
    # Filter recommendations to only show new ones
    filtered_recommendations = [h for h in recommended_habits 
                             if h["name"].lower() not in current_habit_names]
    
    if filtered_recommendations:
        # Display recommendations in a horizontal layout
        cols = st.columns(min(4, len(filtered_recommendations)))
        
        for i, habit in enumerate(filtered_recommendations[:4]):  # Show up to 4 recommendations
            with cols[i]:
                st.markdown(f"**{habit['name']}**")
                st.caption(f"{habit['category']}")
                
                if st.button("Добавить ➕", key=f"rec_{i}"):
                    add_user_habit(
                        user_id=user_id,
                        name=habit['name'],
                        description=habit['description'],
                        category=habit['category'],
                        time_required="5 минут",
                        difficulty="Средне",
                        selected_time="08:00"
                    )
                    st.success(f"Привычка '{habit['name']}' добавлена!")
                    st.rerun()
    else:
        st.info("У вас уже есть все рекомендуемые привычки!")
    
    st.markdown("---")
    
    # If no habits, show a message
    if not habits:
        st.info("У вас пока нет отслеживаемых привычек. Добавьте привычки с помощью формы выше.")
        return
    
    # Tabs for different sections
    habit_track_tab, progress_tab, statistics_tab, manage_tab = st.tabs(["Трекер", "Прогресс", "Статистика", "Управление"])
    
    with habit_track_tab:
        render_habit_tracker(habits, user_id)
    
    with progress_tab:
        render_progress_view(habits, user_id)
    
    with statistics_tab:
        render_statistics_view(habits, user_id)
        
    with manage_tab:
        render_manage_habits(habits, user_id)

def render_habit_tracker(habits, user_id):
    """Render the habit tracking interface."""
    st.subheader("📝 Трекер ежедневных привычек")
    st.write("Отметьте привычки, которые вы выполнили сегодня:")
    
    # Get today's date
    today = datetime.now().date()
    
    # Display each habit with checkbox
    for habit in habits:
        habit_id = habit['id']
        habit_name = habit['name']
        
        # Check if habit was already logged today
        logs = get_habit_logs(user_id, habit_id, today)
        is_logged = len(logs) > 0
        
        # Create a unique key for each checkbox
        key = f"habit_{habit_id}_{today}"
        
        col1, col2 = st.columns([4, 1])
        with col1:
            checked = st.checkbox(
                habit_name,
                value=is_logged,
                key=key
            )
        
        # If checkbox state changed
        if checked != is_logged:
            if checked:
                # Log the habit
                add_habit_log(user_id, habit_id, today, completed=True)
                st.success(f"✅ {habit_name} отмечена как выполненная!")
            else:
                # Remove log for that habit and day
                # Note: Not implemented in this example
                st.info(f"❌ {habit_name} отмечена как невыполненная.")

def render_progress_view(habits, user_id):
    """Render the progress tracking view."""
    st.subheader("📈 Прогресс")
    
    # Calculate date range (last 7 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Get streak data
    streak_data = {}
    for habit in habits:
        habit_id = habit['id']
        streak_info = get_streak_data(user_id, habit_id)
        streak_data[habit['name']] = streak_info
    
    # Create a streak overview
    st.write("### Текущие серии выполнения")
    
    if streak_data:
        streak_df = pd.DataFrame({
            'Привычка': list(streak_data.keys()),
            'Текущая серия': [data['current_streak'] for data in streak_data.values()],
            'Максимальная серия': [data['max_streak'] for data in streak_data.values()]
        })
        
        st.dataframe(streak_df, hide_index=True)
    else:
        st.info("Пока нет данных о сериях. Начните отслеживать привычки!")
    
    # Show calendar heatmap or similar visualization
    st.write("### Календарь выполнения")
    st.info("Календарь будет показывать ваш прогресс за последние 7 дней.")
    
    # Placeholder for calendar visualization
    # In a real app, you would create a heatmap or calendar view here

def render_statistics_view(habits, user_id):
    """Render statistics and analytics view."""
    st.subheader("📊 Статистика выполнения")
    
    if not habits:
        st.info("Добавьте привычки и начните их отслеживать для просмотра статистики.")
        return
    
    # Calculate overall completion rate
    completion_data = {}
    
    # Get last 30 days of data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)
    
    for habit in habits:
        habit_id = habit['id']
        logs = get_habit_logs(user_id, habit_id, start_date=start_date, end_date=end_date)
        
        # Count logged days
        logged_days = len(logs)
        total_days = (end_date - start_date).days + 1
        
        # Calculate completion rate
        completion_rate = (logged_days / total_days) * 100
        completion_data[habit['name']] = completion_rate
    
    if completion_data:
        # Create dataframe for visualization
        df = pd.DataFrame({
            'Привычка': list(completion_data.keys()),
            'Процент выполнения': list(completion_data.values())
        })
        
        # Create bar chart for completion rates
        fig = px.bar(
            df,
            x='Привычка',
            y='Процент выполнения',
            title='Процент выполнения привычек за последние 30 дней',
            labels={'Привычка': 'Привычка', 'Процент выполнения': 'Процент выполнения (%)'},
            color='Процент выполнения',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Пока нет данных для отображения статистики.")

def render_manage_habits(habits, user_id):
    """Render interface for managing habits."""
    st.subheader("⚙️ Управление привычками")
    
    # Add Detailed Habit form
    with st.expander("➕ Добавить новую привычку с подробностями"):
        with st.form("detailed_habit_form"):
            # Form inputs
            habit_name = st.text_input("Название привычки", max_chars=50)
            habit_description = st.text_area("Описание (цель и польза)", max_chars=200)
            habit_category = st.selectbox(
                "Категория",
                options=["Здоровье", "Продуктивность", "Саморазвитие", "Физическое здоровье", "Ментальное здоровье", "Другое"]
            )
            habit_time_required = st.selectbox(
                "Требуемое время",
                options=["5 минут", "10-15 минут", "15-30 минут", "30-60 минут"]
            )
            habit_difficulty = st.selectbox(
                "Сложность привычки",
                options=["Легко", "Средне", "Сложно"]
            )
            habit_selected_time = st.time_input("Предпочтительное время выполнения", value=datetime.strptime("08:00", "%H:%M").time())
            
            # Submit button
            submitted = st.form_submit_button("Добавить привычку")
            
            if submitted:
                if not habit_name:
                    st.error("Пожалуйста, введите название привычки.")
                else:
                    # Add the habit to the database
                    add_user_habit(
                        user_id=user_id,
                        name=habit_name,
                        description=habit_description,
                        category=habit_category,
                        time_required=habit_time_required,
                        difficulty=habit_difficulty,
                        selected_time=habit_selected_time.strftime("%H:%M")
                    )
                    st.success(f"Привычка '{habit_name}' успешно добавлена!")
                    st.rerun()
    
    # Display all habits with edit/delete options
    for habit in habits:
        with st.expander(f"{habit['name']} ({habit.get('category', 'Общее')})"):
            # Create a form for editing the habit
            with st.form(key=f"edit_form_{habit['id']}"):
                # Habit name
                new_name = st.text_input(
                    "Название привычки",
                    value=habit['name'],
                    key=f"edit_name_{habit['id']}"
                )
                
                # Category (if available)
                category = habit.get('category', 'Общее')
                st.text_input(
                    "Категория",
                    value=category,
                    disabled=True,
                    key=f"edit_category_{habit['id']}"
                )
                
                # Description
                description = habit.get('description', '')
                new_description = st.text_area(
                    "Описание",
                    value=description,
                    key=f"edit_desc_{habit['id']}"
                )
                
                # Time required
                time_required = habit.get('time_required', '5 минут')
                new_time_required = st.selectbox(
                    "Требуемое время",
                    ["5 минут", "10-15 минут", "15-30 минут", "30-60 минут"],
                    index=["5 минут", "10-15 минут", "15-30 минут", "30-60 минут"].index(time_required)
                    if time_required in ["5 минут", "10-15 минут", "15-30 минут", "30-60 минут"]
                    else 0,
                    key=f"edit_time_req_{habit['id']}"
                )
                
                # Difficulty
                difficulty = habit.get('difficulty', 'Средне')
                new_difficulty = st.selectbox(
                    "Сложность",
                    ["Легко", "Средне", "Сложно"],
                    index=["Легко", "Средне", "Сложно"].index(difficulty)
                    if difficulty in ["Легко", "Средне", "Сложно"]
                    else 0,
                    key=f"edit_diff_{habit['id']}"
                )
                
                # Selected time
                selected_time = habit.get('selected_time', '08:00')
                new_selected_time = st.text_input(
                    "Запланированное время (ЧЧ:ММ)",
                    value=selected_time,
                    key=f"edit_time_{habit['id']}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Save button
                    save_changes = st.form_submit_button("Сохранить изменения")
                
                if save_changes:
                    # Validate time format
                    if not validate_time_format(new_selected_time):
                        st.error("Неверный формат времени. Используйте формат ЧЧ:ММ.")
                    else:
                        # Update habit in database
                        update_habit(
                            habit['id'],
                            new_name,
                            new_description,
                            new_time_required,
                            new_difficulty,
                            new_selected_time
                        )
                        st.success("Привычка успешно обновлена!")
                        st.rerun()
            
            # Delete button (outside the form)
            if st.button("Удалить привычку", key=f"delete_{habit['id']}"):
                # Confirm deletion
                st.warning("Вы уверены, что хотите удалить эту привычку? Это действие нельзя отменить.")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Да, удалить", key=f"confirm_delete_{habit['id']}"):
                        # Delete habit from database
                        delete_habit(habit['id'])
                        st.success("Привычка успешно удалена!")
                        st.rerun()
                
                with col2:
                    if st.button("Отмена", key=f"cancel_delete_{habit['id']}"):
                        st.rerun() 