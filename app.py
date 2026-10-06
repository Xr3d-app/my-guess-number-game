import streamlit as st
import random
import time

# --- 1. НАСТРОЙКА СТРАНИЦЫ И ЛОКАЛЬНОЙ ПАМЯТИ ВКЛАДКИ ---
st.set_page_config(page_title="Угадай число", page_icon="🎮")

if "screen" not in st.session_state:
    st.session_state.screen = "menu"

if "secret_number" not in st.session_state:
    st.session_state.secret_number = random.randint(1, 100)

if "bot_history" not in st.session_state:
    st.session_state.bot_history = []
if "bot_game_over" not in st.session_state:
    st.session_state.bot_game_over = False
if "bot_attempts" not in st.session_state:
    st.session_state.bot_attempts = 0

# Локальная память для сетевого режима
if "online_role" not in st.session_state:
    st.session_state.online_role = None
if "current_room" not in st.session_state:
    st.session_state.current_room = None


# --- 🌐 ОБЩАЯ СЕТЕВАЯ ПАМЯТЬ СЕРВЕРА ---
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ СБРОСА ---
def reset_all_games():
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.bot_history = []
    st.session_state.bot_game_over = False
    st.session_state.bot_attempts = 0
    st.session_state.online_role = None
    st.session_state.current_room = None
    st.session_state.screen = "menu"
    st.rerun()

def restart_bot_only():
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.bot_history = []
    st.session_state.bot_game_over = False
    st.session_state.bot_attempts = 0
    st.rerun()


# --- УНИВЕРСАЛЬНЫЙ СКРИПТ АВТОФОКУСА ---
def keep_focus():
    st.components.v1.html(
        """
        <script>
        setTimeout(function() {
            var input = window.parent.document.querySelector('input[type="text"]');
            if (input) { input.focus(); }
        }, 50);
        </script>
        """,
        height=0
    )


# --- 2. ЭКРАН 1: ГЛАВНОЕ МЕНЮ ---
if st.session_state.screen == "menu":
    st.title("🎯 Игра: Угадай Число")
    st.write("Выбери режим. Одиночный или настоящий ОНЛАЙН по названию комнат!")
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 Игра против Бота")
        st.write("Бот загадает случайное число от 1 до 100. Угадай за минимальное число ходов!")
        if st.button("Войти к Боту", use_container_width=True):
            st.session_state.screen = "bot_game"
            restart_bot_only()

    with col2:
        st.subheader("🌐 СЕТЕВОЙ ОНЛАЙН")
        st.write("Создай комнату по секретному имени или подключись к комнате друга!")
        if st.button("Войти в Онлайн-Лобби", use_container_width=True):
            st.session_state.screen = "online_choice" 
            st.rerun()


# --- 3. ЭКРАН 2: ЧАТ-КОМНАТА С БОТОМ ---
elif st.session_state.screen == "bot_game":
    st.title("🤖 Чат-комната с Ботом")
    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("⬅️ Выйти в меню", key="exit_bot", use_container_width=True): reset_all_games()
    with col_reset:
        if st.button("🔄 Начать заново", key="reset_bot_btn", use_container_width=True): restart_bot_only()
    st.write("---")
    
    with st.container():
        if not st.session_state.bot_history:
            st.info("🤖 **Бот:** Я загадал число от 1 до 100! Твой вариант?")

        for message in st.session_state.bot_history: st.write(message)
        st.write("---")

        if not st.session_state.bot_game_over:
            st.write(f"📊 Сделано попыток: **{st.session_state.bot_attempts}**")
            with st.form(key="bot_chat_form", clear_on_submit=True):
                user_input = st.text_input("Введи число от 1 до 100:", value="")
                submit_button = st.form_submit_button("Отправить боту", use_container_width=True)
            keep_focus()

            if submit_button and user_input:
                if user_input.isdigit() and 1 <= int(user_input) <= 100:
                    user_guess = int(user_input)
                    st.session_state.bot_attempts += 1
                    if user_guess < st.session_state.secret_number:
                        st.session_state.bot_history.append(f"💬 **Ты:** {user_guess} (Попытка №{st.session_state.bot_attempts}) ➡️  🤖 **Бот:** 🔼 Мало! Моё число больше.")
                        st.rerun()
                    elif user_guess > st.session_state.secret_number:
                        st.session_state.bot_history.append(f"💬 **Ты:** {user_guess} (Попытка №{st.session_state.bot_attempts}) ➡️  🤖 **Бот:** 🔽 Много! Моё число меньше.")
                        st.rerun()
                    else:
                        st.session_state.bot_history.append(f"🏆 **Ты:** {user_guess} ➡️  🎉 **Бот:** УРА! Ты угадал число за **{st.session_state.bot_attempts}** поп.!")
                        st.session_state.bot_game_over = True
                        st.balloons()
                        st.rerun()
                else: st.error("⚠️ Введи число от 1 до 100!")
        else: st.success(f"🎉 Игра окончена за {st.session_state.bot_attempts} ходов.")


# --- 4. ЭКРАН ВЫБОРА РОЛИ ---
elif st.session_state.screen == "online_choice":
    st.title("🌐 Выбор онлайн-режима")
    if st.button("⬅️ Назад в меню", use_container_width=True):
        st.session_state.screen = "menu"
        st.rerun()
        
    st.write("---")
    col_create, col_join = st.columns(2)
    with col_create:
        st.subheader("🔒 Создать лобби")
        if st.button("Создать Лобби", use_container_width=True):
            st.session_state.online_role = "Создатель"
            st.session_state.screen = "online_game"
            st.rerun()
    with col_join:
        st.subheader("🕵️ Присоединиться")
        if st.button("Войти к Другу", use_container_width=True):
            st.session_state.online_role = "Угадывающий"
            st.session_state.screen = "online_game"
            st.rerun()
# --- 5. ЭКРАН 3: 🌐 НАСТОЯЩИЙ СЕТЕВОЙ ОНЛАЙН ---
elif st.session_state.screen == "online_game":
    st.title(f"🌐 Сетевая комната ({st.session_state.online_role})")
    
    if st.button("⬅️ Покинуть лобби и выйти в меню", use_container_width=True):
        reset_all_games()
        
    st.write("---")
    
    # Если комната еще не выбрана локально во вкладке
    if st.session_state.current_room is None:
        if st.session_state.online_role == "Создатель":
            st.subheader("Шаг 1: Придумай имя лобби и секретное число")
            
            with st.form(key="creation_form", clear_on_submit=True):
                room_input = st.text_input("Придумай название комнаты (английскими буквами):", value="").strip().lower()
                secret_input = st.text_input("Загадай секретное число (1-100):", type="password")
                submit = st.form_submit_button("Создать комнату", use_container_width=True)
                
            if submit and room_input and secret_input:
                if room_input in global_rooms:
                    st.error("⚠️ Комната с таким именем уже существует! Придумай другое название.")
                elif not secret_input.isdigit() or not (1 <= int(secret_input) <= 100):
                    st.error("⚠️ Введи число от 1 до 100!")
                else:
                    global_rooms[room_input] = {
                        "secret": int(secret_input),
                        "history": [f"📢 **Система:** Комната `{room_input}` успешно создана! Ready Player 2."],
                        "game_over": False,
                        "attempts": 0
                    }
                    st.session_state.current_room = room_input
                    st.rerun()
        
        else: # Роль: Угадывающий
            st.subheader("Шаг 1: Подключение к другу")
            with st.form(key="join_form", clear_on_submit=True):
                room_input = st.text_input("Введи название комнаты, которую создал друг:", value="").strip().lower()
                submit = st.form_submit_button("Подключиться", use_container_width=True)
                
            if submit and room_input:
                if room_input not in global_rooms:
                    st.error("⚠️ Такой комнаты не существует! Проверь название у друга.")
                else:
                    st.session_state.current_room = room_input
                    st.rerun()

    # ЕСЛИ ВЫ КОМНАТУ ВВЕЛИ И ИГРАЕМ ПРЯМО СЕЙЧАС
    else:
        room_name = st.session_state.current_room
        
        if room_name not in global_rooms:
            st.error("⚠️ Лобби было закрыто создателем или удалено.")
            time.sleep(2)
            reset_all_games()
            
        room = global_rooms[room_name]
        
        st.subheader(f"🔒 Лобби: {room_name}")
        
        # Показываем общий чат и лог ходов
        with st.container():
            for message in room["history"]:
                st.write(message)
        st.write("---")
        
        # ОБЩИЙ СЕТЕВОЙ ТЕКСТОВЫЙ ЧАТ
        st.write("💬 **Сетевой чат:**")
        with st.form(key="lobby_chat_form", clear_on_submit=True):
            chat_text = st.text_input("Напиши сообщение в чат лобби:", value="", key="lobby_chat_input")
            submit_msg = st.form_submit_button("Отправить в чат", use_container_width=True)
            
        if submit_msg and chat_text:
            room["history"].append(f"✉️ **[{st.session_state.online_role}]:** {chat_text}")
            st.rerun()
            
        st.write("---")
        
        # ТА САМАЯ ИГРОВАЯ ЗОНА С РАЗДЕЛЕНИЕМ ПРАВ
        if not room["game_over"]:
            st.write(f"📊 Всего попыток сделано другом: **{room['attempts']}**")
            
            if st.session_state.online_role == "Угадывающий":
                with st.form(key="lobby_guess_form", clear_on_submit=True):
                    guess_input = st.text_input("Твой числовой ответ:", value="", key="lobby_guess_input")
                    submit_guess = st.form_submit_button("Проверить число", use_container_width=True)
                keep_focus()
                
                if submit_guess and guess_input:
                    if guess_input.isdigit():
                        guess = int(guess_input)
                        room["attempts"] += 1
                        
                        if guess < room["secret"]:
                            room["history"].append(f"🎯 **Друг ввёл:** {guess} (Попытка №{room['attempts']}) ➡️ 🖥️ **Сеть:** 🔼 Мало!")
                            st.rerun()
                        elif guess > room["secret"]:
                            room["history"].append(f"🎯 **Друг ввёл:** {guess} (Попытка №{room['attempts']}) ➡️ 🖥️ **Сеть:** 🔽 Много!")
                            st.rerun()
                        else:
                            room["history"].append(f"🏆 **Победа! Друг разгадал число:** {guess} за {room['attempts']} поп.!")
                            room["game_over"] = True
                            st.balloons()
                            st.rerun()
                    else:
                        st.error("⚠️ Вводи цифры!")
            else:
                st.info("👁️ Ты создатель. Поле ввода закрыто. Наблюдай за попытками друга в реальном времени и общайся в чате!")
        else:
            st.success(f"🏆 Раунд завершен! Загаданное число было: **{room['secret']}**")
            
        # Кнопка сброса лобби
        if st.button("🔄 Закрыть/Очистить лобби и выйти", use_container_width=True):
            if room_name in global_rooms:
                del global_rooms[room_name]
            reset_all_games()
            
        # Автообновление экрана раз в 2 секунды, чтобы чат обновлялся сам
        time.sleep(2)
        st.rerun()
