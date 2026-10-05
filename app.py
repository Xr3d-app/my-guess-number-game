import streamlit as st
import random

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
        }, 30);
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
            st.session_state.screen = "online_lobby"
            st.rerun()


# --- 3. ЭКРАН 2: ЧАТ-КОМНАТА С БОТОМ ---
elif st.session_state.screen == "bot_game":
    st.title("🤖 Чат-комната с Ботом")
    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("⬅️ Выйти в меню", key="exit_bot", use_container_width=True): 
            reset_all_games()
    with col_reset:
        if st.button("🔄 Начать заново", key="reset_bot_btn", use_container_width=True): 
            restart_bot_only()
    st.write("---")
    
    # Фиксированный контейнер защищает от мерцания интерфейса
    with st.container():
        if not st.session_state.bot_history:
            st.info("🤖 **Бот:** Я загадал число от 1 до 100! Твой вариант?")

        for message in st.session_state.bot_history: 
            st.write(message)
        
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
                else:
                    st.error("⚠️ Введи корректное число от 1 до 100!")
        else:
            st.success(f"🎉 Игра окончена! Ты победил бота за {st.session_state.bot_attempts} ходов. Нажми 'Начать заново' для нового раунда.")


# --- 4. ЭКРАН 3:🌐 НАСТОЯЩИЙ СЕТЕВОЙ ОНЛАЙН ---
elif st.session_state.screen == "online_lobby":
    st.title("🌐 Сетевые Онлайн-Комнаты")
    
    if st.button("⬅️ Выйти в главное меню", use_container_width=True):
        st.session_state.screen = "menu"
        st.rerun()
        
    st.write("---")
    
    room_name = st.text_input("Введи НАЗВАНИЕ комнаты (например: nfs, dota, lock):", value="").strip().lower()
    
    if room_name:
        st.write(f"Вы ввели комнату: **{room_name}**")
        
        with st.container():
            if room_name not in global_rooms:
                st.subheader("🔒 Создание комнаты (Ты Игрок 1)")
                st.info(f"Комната '{room_name}' свободна. Загадай число, чтобы друг мог подключиться.")
                
                with st.form(key="create_room_form", clear_on_submit=True):
                    secret_input = st.text_input("Загадай секретное число (1-100):", type="password")
                    submit_create = st.form_submit_button("Создать лобби и скрыть число", use_container_width=True)
                    
                if submit_create and secret_input:
                    if secret_input.isdigit() and 1 <= int(secret_input) <= 100:
                        global_rooms[room_name] = {
                            "secret": int(secret_input),
                            "history": [],
                            "game_over": False,
                            "attempts": 0
                        }
                        st.success(f"Лобби '{room_name}' создано! Скажи другу название. Не закрывай эту страницу!")
                        st.rerun()
                    else:
                        st.error("⚠️ Введи число от 1 до 100!")
                        
            else:
                st.subheader(f"🕵️ Игра в лобби: {room_name} (Ты Игрок 2)")
                room = global_rooms[room_name]
                
                if not room["history"]:
                    st.info("🔒 Число загадано Игроком 1! Вводи свои догадки👇")
                for message in room["history"]:
                    st.write(message)
                    
                st.write("---")
                
                if not room["game_over"]:
                    st.write(f"📊 Сделано попыток другом: **{room['attempts']}**")
                    
                    with st.form(key="online_guess_form", clear_on_submit=True):
                        friend_input = st.text_input("Твоя догадка:", value="")
                        submit_friend = st.form_submit_button("Проверить в онлайне", use_container_width=True)
                    keep_focus()
                    
                    if submit_friend and friend_input:
                        if friend_input.isdigit():
                            guess = int(friend_input)
                            room["attempts"] += 1
                            
                            if guess < room["secret"]:
                                room["history"].append(f"💬 **Игрок 2:** {guess} (Попытка №{room['attempts']}) ➡️  🖥️ **Сеть:** 🔼 Мало! Загаданное число больше.")
                                st.rerun()
                            elif guess > room["secret"]:
                                room["history"].append(f"💬 **Игрок 2:** {guess} (Попытка №{room['attempts']}) ➡️  🖥️ **Сеть:** 🔽 Много! Загаданное число меньше.")
                                st.rerun()
                            else:
                                room["history"].append(f"🏆 **Игрок 2:** {guess} ➡️  🎉 **Сеть:** ПОБЕДА! Число разгадано за {room['attempts']} поп.!")
                                room["game_over"] = True
                                st.balloons()
                                st.rerun()
                        else:
                            st.error("⚠️ Введи число цифрами!")
                else:
                    st.success(f"🏆 Раунд завершен! Число разгадано. Чтобы сыграть заново, нажмите кнопку ниже.")
                    
                if st.button("🔄 Сбросить это онлайн-лобби и удалить"):
                    del global_rooms[room_name]
                    st.rerun()
