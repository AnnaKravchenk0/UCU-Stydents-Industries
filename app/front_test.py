import streamlit as st
import requests

# Command to start frontend
# >>> streamlit run front.py

st.title('Hello world!')
st.header('Registration or Login')

username = st.text_input("Enter username:")
if username:
    st.success(f'{username}')

password = st.text_input("Password:")
if password:
    st.success(f'{password}')

if st.button('Login'):
    url = 'http://127.0.0.1:8000/user'

    data = {
    "username": username,
    "password": password
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        data = response.json()

        st.json(data)
    else:
        print(f'Failed to retrieve data {response.status_code}')

if st.button('get user'):
    url = f'http://127.0.0.1:8000/get_user/{username}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        st.json(data)
    else:
        print(f'Failed to retrieve data {response.status_code}')
