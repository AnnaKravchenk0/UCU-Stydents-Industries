function renderHeader() {
    const existingHeader = document.querySelector('header');
    if (existingHeader) {
        existingHeader.remove();
    }

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
            </ul>
            <div class="auth-lang" id="nav-right" style="display: flex; gap: 15px; align-items: center;">
    `;

    if (token) {
        navContent += `
                <a href="my_films.html" style="color: white; text-decoration: none;">My Collection</a>
                <a href="profile.html" style="color: white; text-decoration: none;">Friends</a>

                <div class="user-menu" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-weight: 600; color: white;">${username}</span>
                    <div class="user-avatar-circle" style="width: 36px; height: 36px; background: var(--accent-pink); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        ${username.charAt(0).toUpperCase()}
                    </div>
                </div>

                <a href="#" onclick="logout()" class="auth-link" style="color: var(--text-sec); text-decoration: none; font-size: 0.85rem;">Log out</a>
        `;
    } else {
        navContent += `
                <a href="login.html" style="color: white; text-decoration: none; font-weight: 500;">Log In</a>
                <a href="signup.html" style="background-color: var(--accent-pink); color: white; text-decoration: none; padding: 8px 20px; border-radius: 20px; font-weight: bold;">Sign Up</a>
        `;
    }

    navContent += `
            </div>
        </nav>
    `;

    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage === 'index.html' || currentPage === '') {
        navContent += `
            <nav class="sub-nav">
                <a href="index.html" class="active-sub" onclick="goToChoose()">Movies</a>
                <a href="development.html">Books</a>
                <a href="development.html">Cartoons</a>
                <a href="development.html">Audiobooks</a>
                <a href="development.html">Podcasts</a>
                <a href="development.html">Playlists</a>
                <a href="development.html">Show</a>
                <a href="development.html">TV shows</a>
            </nav>
        `;
    }

    header.innerHTML = navContent;

    document.body.prepend(header);
}

function goToChoose() {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'choose.html';
    } else {
        window.location.href = 'login.html';
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', renderHeader);