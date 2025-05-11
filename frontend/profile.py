import streamlit as st
import pandas as pd
import json
from datetime import datetime
from backend.database import get_user_by_id, update_user_profile, get_user_habits, get_habit_logs

def render_profile_page():
    """Render the user profile page."""
    st.title("👤 Профиль пользователя")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему для доступа к профилю.")
        return
    
    user_id = st.session_state.user_id
    user_data = get_user_by_id(user_id)
    
    if not user_data:
        st.error("Ошибка при загрузке данных пользователя.")
        return
    
    # Create tabs for profile sections
    profile_tab, stats_tab, settings_tab = st.tabs([
        "Информация о профиле", 
        "Статистика", 
        "Настройки"
    ])
    
    with profile_tab:
        render_profile_info(user_data, user_id)
    
    with stats_tab:
        render_user_statistics(user_id)
    
    with settings_tab:
        render_user_settings(user_data, user_id)

def render_profile_info(user_data, user_id):
    """Render basic profile information."""
    st.subheader("🧑‍💻 Информация о профиле")
    
    # Display current profile details
    st.write("#### Текущая информация")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Имя пользователя:** {user_data['username']}")
        st.markdown(f"**Имя:** {user_data.get('full_name', 'Не указано')}")
    
    with col2:
        st.markdown(f"**Email:** {user_data.get('email', 'Не указано')}")
        joined_date = datetime.fromtimestamp(user_data['created_at']).strftime('%d.%m.%Y')
        st.markdown(f"**Дата регистрации:** {joined_date}")
    
    # Edit profile form
    st.write("#### Редактировать профиль")
    
    with st.form("edit_profile_form"):
        full_name = st.text_input("Полное имя", value=user_data.get('full_name', ''))
        email = st.text_input("Email", value=user_data.get('email', ''))
        bio = st.text_area("О себе", value=user_data.get('bio', ''), max_chars=200)
        
        submitted = st.form_submit_button("Сохранить изменения")
        
        if submitted:
            # Update profile in database
            success = update_user_profile(
                user_id=user_id,
                full_name=full_name,
                email=email,
                bio=bio
            )
            
            if success:
                st.success("Профиль успешно обновлен!")
                st.rerun()
            else:
                st.error("Не удалось обновить профиль. Пожалуйста, попробуйте еще раз.")

def render_user_statistics(user_id):
    """Render user statistics about habits and progress."""
    st.subheader("📊 Ваша статистика")
    
    # Get user habits and logs
    habits = get_user_habits(user_id)
    
    if not habits:
        st.info("Статистика еще не доступна. Начните отслеживать привычки чтобы увидеть данные.")
        return
    
    # Calculate statistics
    total_habits = len(habits)
    
    # Calculate completion rate, streak, etc.
    habit_logs = []
    for habit in habits:
        logs = get_habit_logs(user_id, habit['id'])
        habit_logs.extend(logs)
    
    # Simple stats
    completion_count = len(habit_logs)
    current_streak = 0  # This would need more complex calculation
    completion_rate = 0
    
    if total_habits > 0:
        # Very simplified calculation for demo purposes
        completion_rate = min(100, (completion_count / (total_habits * 30)) * 100)
    
    # Create metrics for key statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Всего привычек",
            value=total_habits,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Текущая серия",
            value=f"{current_streak} дней",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Процент выполнения",
            value=f"{completion_rate:.1f}%",
            delta=None,
            help="Процент выполнения привычек"
        )
    
    # Show detailed statistics
    st.write("#### Подробная статистика")
    
    # Create DataFrame for habit performance
    if habits:
        habit_data = []
        for habit in habits:
            logs = get_habit_logs(user_id, habit['id'])
            habit_data.append([
                habit['name'], 
                len(logs), 
                len(logs), 
                100.0 if len(logs) > 0 else 0.0,
                0  # Max streak (would need more complex calculation)
            ])
        
        if habit_data:
            perf_df = pd.DataFrame(habit_data)
            perf_df.columns = [
                "Привычка", "Дней отслеживания", "Выполнено", "Процент выполнения", "Макс. серия"
            ]
            
            st.dataframe(
                perf_df,
                column_config={
                    "Процент выполнения": st.column_config.ProgressColumn(
                        "Процент выполнения",
                        format="%{value:.1f}%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
            )
    else:
        st.info("Нет данных о выполнении привычек. Продолжайте отслеживание чтобы увидеть результаты.")

def render_user_settings(user_data, user_id):
    """Render user settings options."""
    st.subheader("⚙️ Настройки")
    
    st.write("#### Уведомления")
    
    # Initialize default settings
    default_settings = {
        'daily_reminder': True,
        'reminder_time': '20:00',
        'weekly_summary': True,
        'achievement_notifications': True
    }
    
    # Parse notification settings from JSON string or use default
    notification_settings = default_settings.copy()
    
    try:
        if user_data.get('notification_settings'):
            if isinstance(user_data['notification_settings'], str):
                # Try to parse JSON string
                parsed_settings = json.loads(user_data['notification_settings'])
                if isinstance(parsed_settings, dict):
                    notification_settings.update(parsed_settings)
            elif isinstance(user_data['notification_settings'], dict):
                # If it's already a dictionary, use it
                notification_settings.update(user_data['notification_settings'])
            # If it's a list or any other type, we'll use the default settings
    except:
        # If any error occurs, we'll use the default settings
        pass
    
    with st.form("notification_settings"):
        daily_reminder = st.toggle(
            "Ежедневные напоминания о привычках",
            value=notification_settings['daily_reminder']
        )
        
        # Parse reminder time or use default
        default_time = datetime.strptime('20:00', '%H:%M').time()
        try:
            reminder_time = datetime.strptime(notification_settings['reminder_time'], '%H:%M').time()
        except:
            reminder_time = default_time
            
        reminder_time = st.time_input(
            "Время ежедневного напоминания",
            value=reminder_time
        )
        
        weekly_summary = st.toggle(
            "Еженедельная сводка прогресса",
            value=notification_settings['weekly_summary']
        )
        
        achievement_notifications = st.toggle(
            "Уведомления о достижениях",
            value=notification_settings['achievement_notifications']
        )
        
        submitted = st.form_submit_button("Сохранить настройки")
        
        if submitted:
            # Update notification settings in database
            new_settings = {
                'daily_reminder': daily_reminder,
                'reminder_time': reminder_time.strftime('%H:%M'),
                'weekly_summary': weekly_summary,
                'achievement_notifications': achievement_notifications
            }
            
            # Convert to JSON string for storage
            success = update_user_profile(
                user_id=user_id,
                notification_settings=json.dumps(new_settings)
            )
            
            if success:
                st.success("Настройки успешно обновлены!")
            else:
                st.error("Не удалось обновить настройки. Пожалуйста, попробуйте еще раз.") 