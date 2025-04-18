import streamlit as st
from frontend.auth import render_login, render_register, render_logout
from frontend.dashboard import render_dashboard
from frontend.profile import render_profile_page
from frontend.recommendations import render_recommendations
from frontend.tracker import render_tracker
from backend.database import initialize_database

# Set page configuration
st.set_page_config(
    page_title="HabitTrack - Умный трекер привычек",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
initialize_database()

# Session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# Custom CSS
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    .stButton button {border-radius: 4px;}
    .habit-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: white;
    }
    .habit-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🌱 HabitTrack")
    st.caption("Умный трекер привычек с ИИ")
    
    # Only show login/register if user is not logged in
    if 'user_id' not in st.session_state:
        auth_tab1, auth_tab2 = st.tabs(["Вход", "Регистрация"])
        with auth_tab1:
            render_login()
        with auth_tab2:
            render_register()
    else:
        # Show user info and navigation
        st.success(f"Добро пожаловать, {st.session_state.username}!")
        
        # Navigation Menu
        st.subheader("Навигация")
        nav_cols = st.columns(1)
        
        with nav_cols[0]:
            if st.button("📊 Дашборд", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
                
            if st.button("📝 Трекер", use_container_width=True):
                st.session_state.current_page = "tracker"
                st.rerun()
                
            if st.button("🔍 Рекомендации", use_container_width=True):
                st.session_state.current_page = "recommendations"
                st.rerun()
                
            if st.button("👤 Профиль", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
                
            st.divider()
            render_logout()

# Main content
if 'user_id' in st.session_state:
    # User is logged in, show appropriate page
    if st.session_state.current_page == "dashboard":
        render_dashboard()
    elif st.session_state.current_page == "tracker":
        render_tracker()
    elif st.session_state.current_page == "recommendations":
        render_recommendations()
    elif st.session_state.current_page == "profile":
        render_profile_page()
else:
    # If not logged in, show landing page
    st.title("🌱 Добро пожаловать в HabitTrack!")
    st.write("""
    ### Умный трекер привычек с поддержкой ИИ
    
    HabitTrack помогает вам формировать полезные привычки и отслеживать свой прогресс.
    Используя искусственный интеллект, мы предлагаем персонализированные рекомендации
    для улучшения вашей жизни.
    
    **Для начала войдите в систему или зарегистрируйтесь.**
    """)
    
    # Features section
    st.subheader("Возможности:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📊 Отслеживание привычек
        Ежедневно отмечайте выполненные привычки и наблюдайте за своим прогрессом.
        """)
    
    with col2:
        st.markdown("""
        #### 🧠 ИИ-рекомендации
        Получайте персонализированные предложения по привычкам на основе ваших целей.
        """)
    
    with col3:
        st.markdown("""
        #### 🏆 Достижения
        Зарабатывайте награды и поддерживайте мотивацию на пути к самосовершенствованию.
        """) 