import streamlit as st
import requests

# streamlit run front_test.py

BASE_URL = "http://127.0.0.1:8000"

# зберігаємо токен між запитами
if "token" not in st.session_state:
    st.session_state.token = None


# ---------------- REGISTRATION ----------------
st.header("Registration")

reg_username = st.text_input("Username", key="reg_username")
reg_password = st.text_input("Password", type="password", key="reg_password")

if st.button("Register"):
    r = requests.post(
        f"{BASE_URL}/users/registration",
        json={"username": reg_username, "password": reg_password},
        timeout=5,
    )

    if r.status_code == 201:
        st.success("User created!")
        st.json(r.json())
    else:
        st.error(r.text)


# ---------------- LOGIN ----------------
st.header("Login")

login_username = st.text_input("Username", key="login_username")
login_password = st.text_input("Password", type="password", key="login_password")

if st.button("Login"):
    r = requests.post(
        f"{BASE_URL}/users/login",
        data={"username": login_username, "password": login_password},
        timeout=5,
    )

    if r.status_code == 200:
        token = r.json()["access_token"]
        st.session_state.token = token
        st.success("Logged in!")
        st.write(token)
    else:
        st.error(r.text)


# ---------------- ME ----------------
st.header("Current user (/me)")

if st.button("Get me"):
    if not st.session_state.token:
        st.warning("Login first")
    else:
        r = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        st.write(r.status_code)
        st.json(r.json())


# ---------------- GET BY ID ----------------
st.header("Get user by ID")

user_id = st.text_input("User ID")

if st.button("Get user"):
    r = requests.get(f"{BASE_URL}/users/{user_id}")
    st.write(r.status_code)
    st.text(r.text)


# ---------------- DELETE ----------------
st.header("Delete myself")

delete_id = st.text_input("ID to delete")

if st.button("Delete"):
    if not st.session_state.token:
        st.warning("Login first")
    else:
        r = requests.delete(
            f"{BASE_URL}/users/{delete_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        st.write(r.status_code)
        if r.status_code == 204:
            st.success("Deleted!")


# ---------------- FRIENDS SECTION ----------------
st.divider()
st.header("🤝 Friends Management")

if not st.session_state.token:
    st.info("Увійдіть в систему, щоб керувати друзями.")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # 1. Надсилання запиту
    st.subheader("Send Friend Request")
    target_friend_id = st.number_input("Enter User ID to add", min_value=1, step=1, key="send_req_id")
    if st.button("Send Request", key="send_req_btn"):
        r = requests.post(f"{BASE_URL}/users/friends/request/{target_friend_id}", headers=headers)
        if r.status_code == 201:
            st.success("Request sent!")
        else:
            st.error(f"Error: {r.json().get('detail')}")

    # 2. Вхідні запити
    st.subheader("Incoming Requests")
    # Використовуємо контейнер, щоб дані оновлювалися
    incoming_container = st.container()

    # Робимо запит одразу, без кнопки "Check", щоб бачити актуальний стан
    r_inc = requests.get(f"{BASE_URL}/users/friends/requests/incoming", headers=headers)
    if r_inc.status_code == 200:
        incoming = r_inc.json()
        if not incoming:
            st.write("No pending requests.")
        else:
            for req_user in incoming:
                with st.expander(f"Request from {req_user['username']} (ID: {req_user['id']})", expanded=True):
                    col1, col2 = st.columns(2)
                    # Додаємо унікальні ключі для кнопок
                    if col1.button(f"✅ Accept {req_user['id']}", key=f"acc_{req_user['id']}"):
                        acc_r = requests.post(f"{BASE_URL}/users/friends/accept/{req_user['id']}", headers=headers)
                        if acc_r.status_code == 200:
                            st.toast(f"Accepted {req_user['username']}!")
                            st.rerun()

                    if col2.button(f"❌ Reject {req_user['id']}", key=f"rej_{req_user['id']}"):
                        rej_r = requests.delete(f"{BASE_URL}/users/friends/{req_user['id']}", headers=headers)
                        if rej_r.status_code == 204:
                            st.toast(f"Rejected {req_user['username']}")
                            st.rerun()

    # 3. Мій список друзів
    st.subheader("My Friends List")
    r_friends = requests.get(f"{BASE_URL}/users/friends/my", headers=headers)
    if r_friends.status_code == 200:
        friends = r_friends.json()
        if not friends:
            st.write("You have no friends yet.")
        else:
            for friend in friends:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {friend['username']} (ID: {friend['id']})")
                if col2.button(f"🗑️ Unfriend", key=f"unf_{friend['id']}"):
                    del_r = requests.delete(f"{BASE_URL}/users/friends/{friend['id']}", headers=headers)
                    if del_r.status_code == 204:
                        st.toast(f"Removed {friend['username']}")
                        st.rerun()



# ---------------- MOVIES ----------------
st.header("Get movies")

name = st.text_input("Назва фільму (name)")
year = st.number_input("Рік (year)", value=None, step=1)
page = st.number_input("Сторінка (page)", min_value=1, value=1)

if 'movie_index' not in st.session_state:
    st.session_state.movie_index = 0
if 'movies_list' not in st.session_state:
    st.session_state.movies_list = []

if st.button("Зробити запит"):
    # Формуємо параметри (фільтруємо None)
    params = {"name": name, "year": year, "page": page}
    params = {k: v for k, v in params.items() if v}

    try:
        # Запит до твого FastAPI (файл movies.py)
        response = requests.get("http://127.0.0.1:8000/movies/", params=params)

        if response.status_code == 200:
            data = response.json()

            # Зберігаємо результати з TMDBClient у стан
            st.session_state.movies_list = data.get("results", [])
            st.session_state.movie_index = 0 # Скидаємо на перший фільм
        else:
            st.error(f"Помилка сервера: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error(f"Не вдалося підключитися до бекенду: {e}")

if st.session_state.movies_list:
    movies = st.session_state.movies_list
    idx = st.session_state.movie_index

    # Виводимо дані поточного фільму
    st.subheader(f"Фільм {idx + 1} з {len(movies)}")
    st.json(movies[idx])

    # Кнопки навігації
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Попередній"):
            if idx > 0:
                st.session_state.movie_index -= 1
                st.rerun()

    with col2:
        if st.button("Наступний ➡️"):
            if idx < len(movies) - 1:
                st.session_state.movie_index += 1
                st.rerun()
            else:
                st.warning("Це останній фільм у списку.")
else:
    st.info("Натисніть кнопку вище, щоб завантажити дані.")

# ---------------- MOVIES ENDPOINTS TEST ----------------

st.divider()
st.header("🎬 Movies Endpoints Testing")

if not st.session_state.token:
    st.info("Login first to test movie endpoints.")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # -------- LIKE MOVIE --------
    st.subheader("❤️ Like Movie")

    movie_id = st.number_input("Movie ID", min_value=1, step=1, key="like_movie_id")
    movie_name = st.text_input("Movie name", key="like_movie_name")
    poster_path = st.text_input("Poster path", key="like_movie_poster")

    if st.button("Like Movie"):
        payload = {
            "id": movie_id,
            "movie_name": movie_name,
            "poster_path": poster_path,
        }

        r = requests.get(
            f"{BASE_URL}/movies/like-movie",
            json=payload,
            headers=headers,
            timeout=5,
        )

        st.write(r.status_code)
        st.json(r.json())

    # -------- GET LIKED MOVIES --------
    st.subheader("📂 Get Liked Movies")

    liked_user_id = st.number_input("User ID", min_value=1, step=1, key="liked_user_id")

    if st.button("Get liked movies"):
        r = requests.get(
            f"{BASE_URL}/movies/{liked_user_id}/liked",
            headers=headers,
            timeout=5,
        )

        st.write(r.status_code)
        st.json(r.json())

    # -------- COMMON MOVIES --------
    st.subheader("👯 Common Movies")

    friend_id = st.number_input("Friend ID", min_value=1, step=1, key="common_friend_id")

    if st.button("Get common movies"):
        r = requests.get(
            f"{BASE_URL}/movies/common/{friend_id}",
            headers=headers,
            timeout=5,
        )

        st.write(r.status_code)
        st.json(r.json())
