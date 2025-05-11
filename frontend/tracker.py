import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from backend.database import (
    get_user_habits,
    add_habit_log,
    get_habit_logs,
    get_streak_data
)
from backend.utils import display_streak_icon

def render_tracker():
    """Render the habit tracking interface."""
    st.title("📝 Ежедневный трекер привычек")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему для доступа к трекеру.")
        return
    
    # Get user habits
    user_id = st.session_state.user_id
    habits = get_user_habits(user_id)
    
    if not habits:
        st.info("У вас пока нет отслеживаемых привычек. Перейдите на вкладку 'Рекомендации' чтобы добавить привычки.")
        return
    
    # Welcome message with username
    st.write(f"Привет, {st.session_state.username}! Отметьте привычки, которые вы выполнили сегодня.")
    
    # Get today's date
    today = datetime.now().date()
    
    # Create habit tracking area
    st.subheader("Трекер на сегодня")
    st.write(f"Дата: {today.strftime('%d.%m.%Y')}")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display each habit with checkbox and streak information
        for habit in habits:
            habit_id = habit['id']
            habit_name = habit['name']
            
            # Get streak information
            streak_info = get_streak_data(user_id, habit_id)
            streak_text = display_streak_icon(streak_info['current_streak'])
            
            # Check if habit was already logged today
            logs = get_habit_logs(user_id, habit_id, today)
            is_logged = len(logs) > 0
            
            # Create container for each habit
            with st.container():
                habit_col1, habit_col2 = st.columns([4, 1])
                
                with habit_col1:
                    # Create a unique key for each checkbox
                    key = f"tracker_habit_{habit_id}_{today}"
                    checked = st.checkbox(
                        f"{habit_name} {streak_text}",
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
                        # Remove log for that habit and day (implementation would depend on database structure)
                        st.info(f"❌ {habit_name} отмечена как невыполненная.")
                    
                    # Force refresh for updated streak information
                    st.rerun()
    
    with col2:
        # Display weekly overview
        st.subheader("Недельный обзор")
        
        # Calculate date range (last 7 days)
        end_date = today
        start_date = end_date - timedelta(days=6)
        date_range = [(start_date + timedelta(days=i)).strftime("%d.%m") for i in range(7)]
        
        # Create a dataframe with completion status for each habit for each day
        completion_data = []
        
        for habit in habits:
            habit_id = habit['id']
            habit_name = habit['name']
            
            row_data = {'Привычка': habit_name}
            
            for i, date_str in enumerate(date_range):
                date = start_date + timedelta(days=i)
                logs = get_habit_logs(user_id, habit_id, date)
                row_data[date_str] = "✅" if logs else "⬜"
            
            completion_data.append(row_data)
        
        # Create dataframe and display as table
        if completion_data:
            df = pd.DataFrame(completion_data)
            st.dataframe(df, hide_index=True)
        else:
            st.info("Нет данных для отображения.")
    
    # Visualization section
    st.subheader("Визуализация прогресса")
    
    # Calculate completion rates for each habit
    completion_rates = {}
    
    for habit in habits:
        habit_id = habit['id']
        
        # Get logs for last 30 days
        thirty_days_ago = today - timedelta(days=29)
        logs = get_habit_logs(user_id, habit_id, start_date=thirty_days_ago, end_date=today)
        
        # Calculate completion rate
        completion_rate = (len(logs) / 30) * 100
        completion_rates[habit['name']] = completion_rate
    
    # Create bar chart for visualization
    if completion_rates:
        df = pd.DataFrame({
            'Привычка': list(completion_rates.keys()),
            'Процент выполнения': list(completion_rates.values())
        })
        
        fig = px.bar(
            df,
            x='Привычка', 
            y='Процент выполнения',
            title='Процент выполнения за последние 30 дней',
            color='Процент выполнения',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    # Motivational section
    st.subheader("Мотивационные советы")
    
    # Calculate average completion rate
    avg_completion = sum(completion_rates.values()) / len(completion_rates) if completion_rates else 0
    
    if avg_completion >= 80:
        st.success("🏆 Отличная работа! Вы отлично справляетесь с выполнением своих привычек. Продолжайте в том же духе!")
    elif avg_completion >= 50:
        st.info("👍 Хороший прогресс! Вы на пути к успеху. Попробуйте повысить регулярность выполнения привычек.")
    else:
        st.warning("💪 Не сдавайтесь! Формирование привычек требует времени. Начните с малого и постепенно увеличивайте нагрузку.")
        
    st.write("""
    ### Советы для формирования привычек:
    
    1. **Начинайте с малого** - делайте маленькие шаги, которые легко выполнить
    2. **Будьте последовательны** - старайтесь выполнять привычки в одно и то же время каждый день
    3. **Объединяйте с существующими привычками** - привяжите новую привычку к тому, что вы уже делаете
    4. **Используйте визуальные напоминания** - разместите заметки или подсказки на видном месте
    5. **Отмечайте свои успехи** - праздновайте маленькие победы
    """) 