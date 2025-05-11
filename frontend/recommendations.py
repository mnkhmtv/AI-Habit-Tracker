import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import get_user_by_id, get_user_habits, add_user_habit, get_user_data
from backend.utils import format_time_string, validate_time_format, get_improvement_areas_options, get_time_commitment_options, get_preferred_time_options

def render_recommendations():
    """Render the recommendations page with habit suggestions."""
    st.title("🔍 Рекомендации по привычкам")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему для доступа к рекомендациям.")
        return
    
    # Get user information
    user_id = st.session_state.user_id
    user_data = get_user_data(user_id)
    
    # Welcome message
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете найти рекомендации по привычкам, которые помогут вам достичь ваших целей.")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Рекомендации", "Настроить рекомендации"])
    
    with tab1:
        # Display recommended habits
        st.subheader("Рекомендуемые привычки")
        
        # Get current user habits
        current_habits = get_user_habits(user_id)
        current_habit_names = [h['name'] for h in current_habits] if current_habits else []
        
        # Create a list of sample recommended habits
        # In a real app, these would come from a recommendation engine
        recommended_habits = [
            {
                "name": "Утренняя зарядка",
                "category": "Физическое здоровье",
                "description": "Начните день с 5-минутной зарядки для повышения энергии и улучшения настроения.",
                "difficulty": "Легко",
                "time_required": "5 минут",
                "benefits": "Повышение энергии, улучшение настроения, поддержание гибкости"
            },
            {
                "name": "Медитация осознанности",
                "category": "Ментальное здоровье",
                "description": "Уделите 10 минут в день тихой медитации для снижения стресса и улучшения концентрации.",
                "difficulty": "Средне",
                "time_required": "10-15 минут",
                "benefits": "Снижение стресса, улучшение концентрации, эмоциональная стабильность"
            },
            {
                "name": "Питьевой режим",
                "category": "Физическое здоровье",
                "description": "Выпивайте стакан воды каждые 2 часа для поддержания гидратации.",
                "difficulty": "Легко",
                "time_required": "5 минут",
                "benefits": "Гидратация, улучшение метаболизма, здоровая кожа"
            },
            {
                "name": "Чтение перед сном",
                "category": "Саморазвитие",
                "description": "Читайте книгу перед сном вместо использования электронных устройств.",
                "difficulty": "Средне",
                "time_required": "15-30 минут",
                "benefits": "Улучшение сна, расширение кругозора, снижение стресса"
            },
            {
                "name": "Планирование дня",
                "category": "Продуктивность",
                "description": "Начните день с составления списка приоритетных задач.",
                "difficulty": "Легко",
                "time_required": "5 минут",
                "benefits": "Повышение продуктивности, снижение стресса, лучшая организация"
            },
            {
                "name": "Благодарность",
                "category": "Ментальное здоровье",
                "description": "Запишите три вещи, за которые вы благодарны каждый день.",
                "difficulty": "Легко",
                "time_required": "5 минут",
                "benefits": "Позитивное мышление, улучшение настроения, снижение тревожности"
            }
        ]
        
        # Filter out habits that user already has
        filtered_recommendations = [h for h in recommended_habits if h["name"] not in current_habit_names]
        
        if not filtered_recommendations:
            st.info("У нас нет новых рекомендаций для вас на данный момент. Попробуйте настроить ваши предпочтения.")
        else:
            for i, habit in enumerate(filtered_recommendations):
                with st.expander(f"{habit['name']} - {habit['category']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Описание:** {habit['description']}")
                        st.markdown(f"**Сложность:** {habit['difficulty']}")
                        st.markdown(f"**Требуемое время:** {habit['time_required']}")
                        st.markdown(f"**Польза:** {habit['benefits']}")
                    
                    with col2:
                        # Add habit button
                        if st.button("Добавить привычку", key=f"add_habit_{i}"):
                            # Default time selection
                            if habit['category'] == "Физическое здоровье":
                                default_time = "08:00"
                            elif habit['category'] == "Продуктивность":
                                default_time = "09:00"
                            elif habit['category'] == "Ментальное здоровье":
                                default_time = "19:00"
                            else:
                                default_time = "20:00"
                            
                            # Add habit to user's list
                            add_user_habit(
                                user_id=user_id,
                                name=habit['name'],
                                description=habit['description'],
                                category=habit['category'],
                                time_required=habit['time_required'],
                                difficulty=habit['difficulty'],
                                selected_time=default_time
                            )
                            
                            st.success(f"Привычка '{habit['name']}' добавлена! Перейдите в Трекер, чтобы начать отслеживание.")
                            st.rerun()
    
    with tab2:
        # Preference settings form to customize recommendations
        st.subheader("Настройте ваши предпочтения")
        st.write("Укажите свои предпочтения, чтобы получить более персонализированные рекомендации.")
        
        with st.form("preference_form"):
            # Areas to improve
            improvement_areas = st.multiselect(
                "Какие области вы хотите улучшить?",
                options=get_improvement_areas_options(),
                default=["Физическое здоровье"]
            )
            
            # Time commitment
            time_commitment = st.select_slider(
                "Сколько времени вы готовы посвящать новым привычкам ежедневно?",
                options=get_time_commitment_options()
            )
            
            # Preferred time
            preferred_time = st.multiselect(
                "В какое время дня вам удобнее выполнять привычки?",
                options=get_preferred_time_options(),
                default=["Утро"]
            )
            
            # Difficulty level
            difficulty_level = st.slider(
                "Предпочитаемый уровень сложности (1 - легко, 5 - сложно)",
                1, 5, 3
            )
            
            # Submit button
            submitted = st.form_submit_button("Обновить предпочтения")
            
            if submitted:
                # In a real app, save these preferences to user's profile
                st.success("Ваши предпочтения сохранены! Обновляем рекомендации...")
                st.rerun()
    
    # Display educational content
    st.subheader("Как формировать полезные привычки")
    
    st.write("""
    ### Научный подход к формированию привычек:
    
    1. **Начинайте с малого** - Исследования показывают, что начинать с небольших, легко выполнимых действий значительно повышает шансы на успех.
    
    2. **Используйте триггеры** - Привяжите новую привычку к существующей рутине. Например: "После чистки зубов я буду медитировать 2 минуты".
    
    3. **Создайте цепочку успеха** - Отмечайте каждый день выполнения привычки в календаре или приложении, чтобы визуализировать прогресс.
    
    4. **Ожидайте неудач** - Исследования показывают, что большинство людей пропускают день или два в процессе формирования привычки. Важно не бросать после первой неудачи.
    
    5. **Система вознаграждений** - Вознаграждайте себя за достижение определенных рубежей, чтобы укрепить мотивацию.
    """)
    
    # Statistical insights
    st.write("### Интересные факты о привычках:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Среднее время формирования привычки", "66 дней", "21-254 дней")
        st.write("Исследование Филиппы Лэлли показало, что в среднем требуется 66 дней для формирования привычки, с разбросом от 21 до 254 дней.")
    
    with col2:
        st.metric("Вероятность успеха с трекером привычек", "80%", "+42%")
        st.write("Люди, отслеживающие свои привычки, имеют на 42% больше шансов сохранить их в долгосрочной перспективе.")

def render_custom_habit_form(user_id, existing_habit_names):
    """Render form to add custom habits."""
    st.subheader("📝 Создайте свою привычку")
    st.write("Создайте полезную привычку, которую хотите развить:")
    
    with st.form("custom_habit_form"):
        # Form inputs
        habit_name = st.text_input("Название привычки", max_chars=50)
        habit_description = st.text_area("Описание (цель и польза)", max_chars=200)
        habit_category = st.selectbox(
            "Категория",
            options=["Здоровье", "Продуктивность", "Саморазвитие", "Физическое здоровье", "Ментальное здоровье"]
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
            elif habit_name.lower() in existing_habit_names:
                st.error(f"Привычка '{habit_name}' уже существует.")
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

def render_ai_recommendations(user_id, existing_habit_names):
    """Render AI-based habit recommendations."""
    st.subheader("🤖 Рекомендации от ИИ")
    st.write("Выберите категорию для получения рекомендаций по привычкам:")
    
    # Category selector
    categories = [
        "Выберите категорию...",
        "Здоровье и фитнес",
        "Продуктивность",
        "Личностный рост",
        "Здоровое питание",
        "Психическое здоровье",
        "Творчество"
    ]
    
    selected_category = st.selectbox("Категория привычек", options=categories)
    
    if selected_category == "Выберите категорию...":
        st.info("Выберите категорию для просмотра рекомендаций.")
        return
    
    # Sample recommendations based on selected category
    recommendations = []
    if selected_category == "Здоровье и фитнес":
        recommendations = [
            {"id": 1, "name": "Утренняя зарядка", "description": "10 минут зарядки после пробуждения", "frequency": "Ежедневно", "difficulty": "Средне"},
            {"id": 2, "name": "Прогулка", "description": "30-минутная прогулка на свежем воздухе", "frequency": "Ежедневно", "difficulty": "Легко"}
        ]
    elif selected_category == "Продуктивность":
        recommendations = [
            {"id": 3, "name": "Планирование дня", "description": "5 минут планирования задач утром", "frequency": "Ежедневно", "difficulty": "Легко"},
            {"id": 4, "name": "Метод Помодоро", "description": "Использование техники Помодоро для работы", "frequency": "В рабочие дни", "difficulty": "Средне"}
        ]
    
    # Filter out habits that user already has
    new_recommendations = [r for r in recommendations 
                          if r['name'].lower() not in existing_habit_names]
    
    if not new_recommendations:
        st.info("Вы уже отслеживаете все рекомендуемые привычки из этой категории.")
        return
    
    # Display recommendations
    st.write(f"### Рекомендации для: {selected_category}")
    
    # Create columns for displaying habits
    cols = st.columns(2)
    
    for i, habit in enumerate(new_recommendations):
        with cols[i % 2]:
            with st.container():
                st.subheader(habit['name'])
                st.write(habit['description'])
                
                # Display metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Частота: {habit['frequency']}")
                with col2:
                    st.caption(f"Сложность: {habit['difficulty']}")
                
                # Add button
                if st.button("Добавить в мои привычки", key=f"add_{habit['id']}"):
                    # Set default time based on habit
                    default_time = "08:00"  # morning default
                    if "вечер" in habit['description'].lower():
                        default_time = "19:00"
                    elif "обед" in habit['description'].lower():
                        default_time = "13:00"
                        
                    add_user_habit(
                        user_id=user_id,
                        name=habit['name'],
                        description=habit['description'],
                        category=selected_category,
                        time_required="15 минут",
                        difficulty=habit['difficulty'],
                        selected_time=default_time
                    )
                    st.success(f"Привычка '{habit['name']}' добавлена!")
                    st.rerun()

def render_recommendations_view():
    """Render the recommendations view with habit suggestions and personalized recommendations."""
    st.title("🔍 Рекомендации привычек")
    
    if 'user_id' not in st.session_state:
        st.error("Пожалуйста, войдите в систему для доступа к рекомендациям")
        st.session_state.current_page = "login"
        st.rerun()
    
    # Get user info
    user = get_user_by_id(st.session_state.user_id)
    
    if not user:
        st.error("Пользователь не найден")
        return
    
    st.write(f"Привет, {user['username']}! Давайте подберем для вас полезные привычки.")
    
    # Show success message if habit was added
    if 'habit_added' in st.session_state and st.session_state.habit_added:
        st.success("Привычка успешно добавлена! Отслеживайте её на своей панели управления.")
        st.session_state.habit_added = False
    
    # Create a list of common habits in different categories
    habits_data = {
        "Здоровье": [
            {"name": "Выпивать стакан воды", "description": "Выпивать стакан воды сразу после пробуждения", "difficulty": "Легко"},
            {"name": "Зарядка", "description": "10 минут утренней зарядки", "difficulty": "Средне"},
            {"name": "Медитация", "description": "5 минут медитации утром или вечером", "difficulty": "Легко"},
            {"name": "Прогулка", "description": "20-30 минут ходьбы на свежем воздухе", "difficulty": "Средне"},
            {"name": "Здоровый перекус", "description": "Заменить один нездоровый перекус на фрукт или орехи", "difficulty": "Средне"}
        ],
        "Продуктивность": [
            {"name": "Глубокая работа", "description": "30 минут работы без отвлечений", "difficulty": "Сложно"},
            {"name": "Планирование дня", "description": "5 минут планирования задач на день", "difficulty": "Легко"},
            {"name": "Чтение", "description": "Читать 10 страниц книги", "difficulty": "Средне"},
            {"name": "Проверка email", "description": "Проверять почту только в определенное время", "difficulty": "Средне"},
            {"name": "Таймер Помодоро", "description": "Использовать технику Помодоро для работы", "difficulty": "Средне"}
        ],
        "Личностный рост": [
            {"name": "Благодарность", "description": "Записать 3 вещи, за которые вы благодарны", "difficulty": "Легко"},
            {"name": "Новый навык", "description": "Уделить 15 минут изучению нового навыка", "difficulty": "Средне"},
            {"name": "Рефлексия", "description": "Уделить 5 минут размышлениям о прошедшем дне", "difficulty": "Легко"},
            {"name": "Цели", "description": "Напоминать себе о своих целях", "difficulty": "Легко"},
            {"name": "Общение", "description": "Поговорить с другом или близким человеком", "difficulty": "Средне"}
        ]
    }
    
    st.subheader("📋 Выберите категорию")
    
    # Create tabs for different habit categories
    tabs = st.tabs(list(habits_data.keys()))
    
    # For each category tab
    for i, (category, habits) in enumerate(habits_data.items()):
        with tabs[i]:
            st.write(f"Предлагаемые привычки в категории '{category}':")
            
            # Display each habit in the category
            for j, habit in enumerate(habits):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(habit["name"])
                        st.write(habit["description"])
                        st.write(f"**Сложность:** {habit['difficulty']}")
                    
                    with col2:
                        # Add habit button
                        if st.button("Добавить", key=f"add_{category}_{j}"):
                            # Determine appropriate time based on habit name and description
                            default_time = "08:00"  # Default morning time
                            if "вечер" in habit["description"].lower() or "сон" in habit["description"].lower():
                                default_time = "20:00"
                            elif "обед" in habit["description"].lower():
                                default_time = "13:00"
                            
                            # Determine appropriate time required
                            time_required = "5 минут"
                            if "10 минут" in habit["description"]:
                                time_required = "10-15 минут"
                            elif "15 минут" in habit["description"] or "20 минут" in habit["description"]:
                                time_required = "15-30 минут"
                            elif "30 минут" in habit["description"]:
                                time_required = "30-60 минут"
                            
                            # Add habit to database
                            add_user_habit(
                                user_id=st.session_state.user_id,
                                name=habit["name"],
                                description=habit["description"],
                                category=category,
                                time_required=time_required,
                                difficulty=habit["difficulty"],
                                selected_time=default_time
                            )
                            
                            # Set success message flag
                            st.session_state.habit_added = True
                            st.rerun()
    
    # Custom habit section
    st.markdown("---")
    st.subheader("🌟 Создать свою привычку")
    
    with st.form("custom_habit_form"):
        habit_name = st.text_input("Название привычки")
        habit_description = st.text_area("Описание привычки")
        habit_category = st.selectbox(
            "Категория",
            options=["Здоровье", "Продуктивность", "Личностный рост", "Другое"]
        )
        habit_time_required = st.selectbox(
            "Требуемое время",
            options=["5 минут", "10-15 минут", "15-30 минут", "30-60 минут"]
        )
        habit_difficulty = st.selectbox(
            "Сложность",
            options=["Легко", "Средне", "Сложно"]
        )
        habit_selected_time = st.time_input("Предпочтительное время", value=datetime.strptime("08:00", "%H:%M").time())
        
        submitted = st.form_submit_button("Добавить привычку")
        
        if submitted:
            if not habit_name or not habit_description:
                st.error("Пожалуйста, заполните все поля")
            else:
                # Add custom habit to database
                add_user_habit(
                    user_id=st.session_state.user_id,
                    name=habit_name,
                    description=habit_description,
                    category=habit_category,
                    time_required=habit_time_required,
                    difficulty=habit_difficulty,
                    selected_time=habit_selected_time.strftime("%H:%M")
                )
                
                # Set success message flag
                st.session_state.habit_added = True
                st.rerun()
    
    # Tips section
    st.markdown("---")
    st.subheader("💡 Советы по формированию привычек")
    
    with st.expander("Как формировать устойчивые привычки"):
        st.markdown("""
        1. **Начинайте с малого** — Выбирайте привычки, которые требуют менее 2 минут в начале.
        2. **Привязывайте к существующим привычкам** — Добавляйте новые привычки после уже устоявшихся действий.
        3. **Делайте их очевидными** — Используйте напоминания или размещайте нужные предметы на видном месте.
        4. **Делайте их привлекательными** — Соедините их с чем-то приятным.
        5. **Отслеживайте прогресс** — Визуальный прогресс мотивирует продолжать.
        6. **Не пропускайте два дня подряд** — Один пропуск не страшен, два создают новый паттерн.
        7. **Будьте терпеливы** — На формирование устойчивой привычки может уйти от 21 до 66 дней.
        """)
    
    with st.expander("Как преодолеть распространенные препятствия"):
        st.markdown("""
        1. **Прокрастинация** — Используйте правило 2-х минут: начните делать хотя бы 2 минуты.
        2. **Отсутствие мотивации** — Создайте систему, не полагайтесь только на мотивацию.
        3. **Забывчивость** — Используйте напоминания и триггеры в окружающей среде.
        4. **Сложность** — Упростите привычку так, чтобы её невозможно было не выполнить.
        5. **Скука** — Варьируйте способы выполнения привычки, делайте её игрой.
        6. **Стресс** — Практикуйте осознанность, чтобы заметить, когда стресс мешает вашим привычкам.
        7. **Срывы** — Заранее планируйте, как вернуться к привычке после срыва.
        """)
    
    # Personalized suggestions based on user data (placeholder for ML model integration)
    st.markdown("---")
    st.subheader("🤖 Персонализированные рекомендации")
    
    # This would be connected to the ML model in a future update
    st.info("Эта функция будет доступна после сбора достаточного количества данных о ваших привычках. Продолжайте отслеживать свои привычки, чтобы получить персональные рекомендации!") 