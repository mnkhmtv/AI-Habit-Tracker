import streamlit as st
import sys
import os
import bcrypt
from backend.database import create_user, get_user_by_username, verify_password
import re

# Add parent directory to path to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def render_auth_view():
    """Render the authentication view with login and registration forms."""
    st.title("🔐 Авторизация")
    
    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["Вход", "Регистрация"])
    
    with login_tab:
        render_login()
    
    with register_tab:
        render_register()

def render_login():
    """Render the login form."""
    with st.form("login_form"):
        st.subheader("Вход в систему")
        
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        
        submitted = st.form_submit_button("Войти")
        
        if submitted:
            if not username or not password:
                st.error("Пожалуйста, заполните все поля")
                return
            
            # Authenticate user
            user = get_user_by_username(username)
            
            if not user:
                st.error("Пользователь не найден")
                return
            
            if not verify_password(password, user.get('password_hash', '')):
                st.error("Неверный пароль")
                return
            
            # Set session state for authenticated user
            st.session_state.user_id = user['id']
            st.session_state.username = username
            
            st.success("Вход выполнен успешно!")
            st.rerun()

def render_register():
    """Render the registration form."""
    with st.form("registration_form"):
        st.subheader("Создать аккаунт")
        
        username = st.text_input("Имя пользователя")
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        
        submitted = st.form_submit_button("Зарегистрироваться")
        
        if submitted:
            # Validate inputs
            if not username or not email or not password or not confirm_password:
                st.error("Пожалуйста, заполните все поля")
                return
            
            # Validate username (alphanumeric, 3-20 chars)
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                st.error("Имя пользователя должно содержать от 3 до 20 символов и может включать буквы, цифры и знаки подчеркивания")
                return
            
            # Validate email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                st.error("Пожалуйста, введите корректный email адрес")
                return
            
            # Validate password (at least 8 chars, with at least one digit and one letter)
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
                st.error("Пароль должен содержать минимум 8 символов, включая хотя бы одну букву и одну цифру")
                return
            
            # Check if passwords match
            if password != confirm_password:
                st.error("Пароли не совпадают")
                return
            
            # Check if username exists
            existing_user = get_user_by_username(username)
            if existing_user:
                st.error("Это имя пользователя уже занято")
                return
            
            # Create user
            user_id = create_user(username, email, password)
            
            if user_id:
                # Set session state for authenticated user
                st.session_state.user_id = user_id
                st.session_state.username = username
                
                st.success("Регистрация успешна! Добро пожаловать!")
                st.rerun()
            else:
                st.error("Произошла ошибка при создании аккаунта. Пожалуйста, попробуйте позже.")

def render_logout():
    """Render the logout button."""
    if st.button("🚪 Выйти", use_container_width=True):
        for key in ['user_id', 'username', 'current_page']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun() 