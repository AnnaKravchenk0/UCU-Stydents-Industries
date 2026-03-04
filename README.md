# MovieMatch – Technical Documentation

## 1. Project Overview

MovieMatch is a social movie-tracking API built with **FastAPI** and **SQLAlchemy 2.0 (Async)**. It handles secure user authentication, social networking (friendships), and TMDB integration.

---

## 2. Technical Architecture

* **Framework:** FastAPI (Asynchronous).
* **Database Layer:** SQLAlchemy Async ORM (supports PostgreSQL, MySQL, SQLite, etc.).
* **Validation:** Pydantic models for request/response filtering.
* **Service Layer:** Business logic is decoupled from route handlers.

---

## 3. Data Schema

The data layer consists of four primary entities managed via the ORM:

* **Users:** Stores unique usernames and **Argon2id** password hashes.
* **Movies:** Local cache of TMDB metadata (ID, Title, Poster).
* **Likes:** Association table linking Users to Movies (Many-to-Many).
* **Friendships:** Manages social links with `sender_id`, `receiver_id`, and `is_accepted` status.

---

## 4. Security & Authentication

The system uses **JWT (JSON Web Tokens)** for secure session handling and **Argon2id** for password security.

### Password Security

* **No Plain Text:** Passwords are never stored raw.
* **Secure:** Even if the database is compromised, raw passwords cannot be recovered.
* **Resistance:** Strong protection against brute-force and rainbow table attacks.

### JWT Authentication Flow

1. **Login:** A user submits valid login credentials.
2. **Verify:** The backend verifies the password hash.
3. **Issue:** If successful, a JWT access token is generated (30-minute expiry).
4. **Authorize:** The token must be included in the header for protected requests:

```http
Authorization: Bearer <YOUR_TOKEN>

```

---

## 5. API Endpoints

### Users & Social (`/users`)

* `POST /registration`: Create a new account.
* `POST /login`: OAuth2 compatible login (Form data).
* `GET /me`: Retrieve private profile (**Auth Required**).
* `POST /friends/request/{id}`: Send friend request.
* `POST /friends/accept/{id}`: Confirm friendship.

### Movies (`/movies`)

* `GET /`: Search TMDB (with `name` and `year` filters).
* `POST /like-movie`: Save movie metadata locally and link to user.
* `GET /common/{friend_id}`: Find shared liked movies using DB joins.

---
3. **Run Server:**

```bash
uvicorn main:app --reload

```
The server will run at `http://127.0.0.1:8000`.
---