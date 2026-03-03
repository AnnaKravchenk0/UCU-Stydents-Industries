function renderHeader() {
    const existingHeader = document.querySelector('header');
    if (existingHeader) existingHeader.remove();

    const header = document.createElement('header');
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'Користувач';

    let navContent = `
        <nav class="top-nav">
            <a href="index.html" class="logo">MovieMatch</a>
            <ul class="nav-links">
                <li><a href="index.html#popular">Popular</a></li>
                <li><a href="index.html#about">About</a></li>
                <li><a href="index.html#contacts">Contacts</a></li>
                <li><a href="search_results.html">Search Movies</a></li>
    `;

    if (token) {
        navContent += `
                <li><a href="choose.html">Choose Movies</a></li>
                <li><a href="my_films.html">My Collection</a></li>
                <li><a href="search_friends.html">Search Friends</a></li>
                <li><a href="profile.html" class="friends-link">Friends</a></li>
            </ul> <div class="auth-lang" id="nav-right">
                <div class="user-menu">
                    <span class="username-display">${username}</span>
                    <div class="user-avatar-circle">${username.charAt(0).toUpperCase()}</div>
                </div>
                <a href="#" onclick="logout()" class="logout-link">Log Out</a>
        `;
    } else {
        navContent += `
            </ul>
            <div class="auth-lang" id="nav-right">
                <a href="login.html" class="login-link">Log In</a>
                <a href="signup.html" class="signup-btn">Sign Up</a>
        `;
    }

    navContent += `</div></nav>`;
    header.innerHTML = navContent;
    document.body.prepend(header);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Функція для адаптивного розміру шрифту
function setResponsiveFontSize() {
    const width = window.innerWidth;
    let baseSize = 16;

    if (width <= 360) {
        baseSize = 11;
    } else if (width <= 480) {
        baseSize = 12;
    } else if (width <= 768) {
        baseSize = 14;
    } else if (width <= 1024) {
        baseSize = 15;
    } else {
        baseSize = 16;
    }

    document.documentElement.style.fontSize = baseSize + 'px';
}

// Викликаємо при завантаженні та зміні розміру
window.addEventListener('load', setResponsiveFontSize);
window.addEventListener('resize', setResponsiveFontSize);

document.addEventListener('DOMContentLoaded', renderHeader);
