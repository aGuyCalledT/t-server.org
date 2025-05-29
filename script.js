document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    // Function to close the mobile navigation menu
    const closeMobileMenu = () => {
        navLinks.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
    };

    // Toggle mobile navigation menu
    navToggle.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent document click from closing immediately
        const isActive = navLinks.classList.contains('active');
        if (isActive) {
            closeMobileMenu();
        } else {
            navLinks.classList.add('active');
            navToggle.setAttribute('aria-expanded', 'true');
        }
    });

    // Close mobile menu if clicked outside
    document.addEventListener('click', (event) => {
        // Check if the click is outside the nav-toggle and nav-links
        if (!navLinks.contains(event.target) && !navToggle.contains(event.target) && navLinks.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    // Reset menu state on window resize (desktop <-> mobile)
    window.addEventListener('resize', () => {
        if (window.innerWidth > 700) { /* Adjust breakpoint if needed */
            // On desktop size: hide mobile menu, reset display
            navLinks.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        } else {
            // On mobile size: ensure menu is hidden by default
            navLinks.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    });
});

