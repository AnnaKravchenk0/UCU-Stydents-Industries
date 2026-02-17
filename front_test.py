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
        f"{BASE_URL}/users/token",
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
