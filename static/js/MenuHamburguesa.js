const hamburger = document.getElementById('hamburger');
    const menuItems = document.getElementById('menuItems');

    hamburger.addEventListener('click', () => {
        menuItems.classList.toggle('active');
    });