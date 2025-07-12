// Remove Firebase SDK imports
// import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
// import { getAuth, signInAnonymously, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
// import { getFirestore, collection, addDoc, deleteDoc, updateDoc, doc, onSnapshot, query, where, getDocs } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// === Configuration for your local Backend Server ===
const API_BASE_URL = 'http://www.t-server.org:3000/api/movies';
// Replace 'DEINE_SERVER_IP_ODER_DOMAIN' with your actual server IP or domain name.
// E.g., 'http://192.168.1.100:3000/api/movies' or 'http://my-server.com:3000/api/movies'

// Global variables (no longer Firebase related)
let userId = 'local_user'; // A dummy userId since Firebase Auth is removed
let isAuthReady = true; // Always true, as no external auth is needed for this simple setup

// Map to track failed attempts for movies missing a year
const failedYearAttempts = new Map();

// DOM Elements (declared as `let`, assigned in DOMContentLoaded)
let navToggle;
let navLinks;
let starField;
let todoInput;
let addButton;
let todoList;
let errorMessage;
let userIdDisplay;

document.addEventListener('DOMContentLoaded', async () => {
    // Assign DOM elements once the document is ready
    todoInput = document.getElementById('todoInput');
    addButton = document.getElementById('addButton');
    todoList = document.getElementById('todoList');
    errorMessage = document.getElementById('errorMessage');
    starField = document.getElementById('star-field');
    navToggle = document.getElementById('navToggle');
    navLinks = document.getElementById('navLinks');
    userIdDisplay = document.getElementById('user-id-display');

    // --- Backend Initialization & Data Loading ---
    try {
        console.log("Loading movies from local backend...");
        userIdDisplay.textContent = `User ID: ${userId}`; // Display dummy user ID
        // Start listening to the backend (simulate Firestore's onSnapshot with a fetch)
        await fetchAndRenderMovies(); // Initial load
    } catch (error) {
        console.error("Error initializing application:", error);
        errorMessage.textContent = `Failed to load the application: ${error.message}. Please check your server setup.`;
        errorMessage.classList.remove('hidden');
    }

    // --- Event Listeners for Movie List App ---
    addButton.addEventListener('click', addTodo);
    todoInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            addTodo();
        }
    });

    // --- Mobile Navigation Logic ---
    const closeMobileMenu = () => {
        navLinks.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
    };

    navToggle.addEventListener('click', (event) => {
        event.stopPropagation();
        const isActive = navLinks.classList.contains('active');
        if (isActive) {
            closeMobileMenu();
        } else {
            navLinks.classList.add('active');
            navToggle.setAttribute('aria-expanded', 'true');
        }
    });

    document.addEventListener('click', (event) => {
        if (!navLinks.contains(event.target) && !navToggle.contains(event.target) && navLinks.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 700) {
            navLinks.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        } else {
            navLinks.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    });

    // --- Dynamic Star Field Logic ---
    const numStars = 200;

    function createStar(isInitialPlacement = false) {
        const star = document.createElement('div');
        star.classList.add('star');
        const size = Math.random() * 3 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        const duration = Math.random() * 15 + 10;
        star.style.setProperty('--animation-duration', `${duration}s`);
        const startY = Math.random() * window.innerHeight;
        star.style.top = `${startY}px`;
        const offScreenBuffer = 50;
        const randomOffScreenOffset = 100;
        const startX = window.innerWidth + offScreenBuffer + Math.random() * randomOffScreenOffset;
        star.style.left = `${startX}px`;
        let delay;
        if (isInitialPlacement) {
            delay = -Math.random() * duration;
        } else {
            delay = 0;
        }
        star.style.setProperty('--animation-delay', `${delay}s`);
        star.style.animation = `starTwinkle ${Math.random() * 5 + 2}s infinite alternate, moveStar var(--animation-duration) linear var(--animation-delay) infinite`;
        star.style.opacity = Math.random() * 0.8 + 0.2;
        starField.appendChild(star);
        setTimeout(() => {
            star.style.opacity = '1';
        }, 50);
        star.addEventListener('animationend', (e) => {
            if (e.animationName === 'moveStar') {
                star.remove();
                createStar(false);
            }
        });
    }

    function updateStarKeyframes() {
        let styleSheet = document.getElementById('star-keyframes-style');
        if (!styleSheet) {
            styleSheet = document.createElement('style');
            styleSheet.id = 'star-keyframes-style';
            styleSheet.type = 'text/css';
            document.head.appendChild(styleSheet);
        }
        styleSheet.innerText = `
            @keyframes moveStar {
                from { transform: translateX(0); }
                to { transform: translateX(${-window.innerWidth - 100}px); }
            }
        `;
    }

    updateStarKeyframes();
    for (let i = 0; i < numStars; i++) {
        createStar(true);
    }
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateStarKeyframes();
            starField.innerHTML = '';
            for (let i = 0; i < numStars; i++) {
                createStar(true);
            }
        }, 250);
    });

    // Initial fetch of movies
    await fetchAndRenderMovies();
});

// --- Movie List App Functions ---

/**
 * Fetches movies from the backend and renders them.
 */
async function fetchAndRenderMovies() {
    hideError();
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const movies = await response.json();

        // Sort movies by hearts (descending) - This is now handled by the backend, but good to keep for consistency
        movies.sort((a, b) => (b.hearts || 0) - (a.hearts || 0));

        todoList.innerHTML = ''; // Clear current list

        if (movies.length === 0) {
            todoList.innerHTML = '<li class="list-item-strip text-center text-gray-400">No movies yet! Add some above.</li>';
        } else {
            movies.forEach(movie => {
                const listItem = createTodoItem(movie.title, movie.year, movie.hearts, movie.id);
                todoList.appendChild(listItem);
            });
        }
        console.log("Movies loaded from backend:", movies);
    } catch (error) {
        console.error("Error loading movies from backend:", error);
        showError(`Failed to load movies: ${error.message}. Please check your server connection.`);
    }
}

/**
 * Displays an error message.
 * @param {string} message - The error message to display.
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

/**
 * Hides the error message.
 */
function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

/**
 * Checks if an item with the given text and year already exists in the list (case-insensitive for text).
 * Fetches current movies and checks locally.
 * @param {string} text - The cleaned text of the item (without year, before parentheses).
 * @param {(number|string)} year - The year of the item (can be '???').
 * @returns {Promise<boolean>} True if the item already exists, otherwise False.
 */
async function itemExists(text, year) {
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const existingMovies = await response.json();
        const normalizedInputTitle = text.trim().toLowerCase();
        const normalizedInputYear = year.toString();

        return existingMovies.some(movie =>
            movie.normalizedTitle === normalizedInputTitle && movie.year === normalizedInputYear
        );
    } catch (e) {
        console.error("Error checking item existence from backend:", e);
        showError("Failed to check for duplicates. Please try again.");
        return false;
    }
}

/**
 * Creates a new list item with title, year, heart, and delete buttons.
 * @param {string} title - The text of the list item (movie title).
 * Will be displayed as "Title (Year)".
 * @param {(number|string)} year - The year of the list item (e.g., 2023 or '???').
 * @param {number} hearts - The current number of hearts.
 * @param {string} docId - The movie's unique ID from the backend.
 * @returns {HTMLLIElement} The created list item.
 */
function createTodoItem(title, year, hearts, docId) {
    const listItem = document.createElement('li');
    listItem.classList.add('list-item-strip');
    listItem.dataset.hearts = hearts;
    listItem.dataset.docId = docId;

    const itemText = document.createElement('span');
    itemText.textContent = `${title.trim()} (${year})`;
    itemText.classList.add('text-lg', 'flex-grow');

    const actionsContainer = document.createElement('div');
    actionsContainer.classList.add('flex', 'items-center');

    const heartCountSpan = document.createElement('span');
    heartCountSpan.classList.add('heart-count');
    heartCountSpan.textContent = hearts.toString();

    const heartButton = document.createElement('button');
    heartButton.classList.add('heart-button');
    const heartImg = document.createElement('img');
    heartImg.src = "https://placehold.co/16x16/50fa7b/121212?text=%E2%9D%A4";
    heartImg.alt = "Heart icon";
    heartImg.classList.add('heart-button-img');
    heartButton.appendChild(heartImg);
    heartButton.setAttribute('aria-label', 'Give heart');

    heartButton.addEventListener('click', async () => {
        const currentHearts = parseInt(listItem.dataset.hearts) + 1;
        try {
            const response = await fetch(`${API_BASE_URL}/${docId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ hearts: currentHearts })
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await fetchAndRenderMovies(); // Re-fetch and render to update UI and sorting
        } catch (e) {
            console.error("Error updating hearts:", e);
            showError("Failed to update hearts.");
        }
    });

    const deleteButton = document.createElement('button');
    deleteButton.classList.add('delete-button');
    const deleteImg = document.createElement('img');
    deleteImg.src = "https://placehold.co/16x16/be123c/ffffff?text=%E2%A0%97";
    deleteImg.alt = "Delete icon";
    deleteImg.classList.add('delete-button-img');
    deleteButton.appendChild(deleteImg);
    deleteButton.setAttribute('aria-label', 'Delete item');

    deleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/${docId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await fetchAndRenderMovies(); // Re-fetch and render to update UI
        } catch (e) {
            console.error("Error deleting movie:", e);
            showError("Failed to delete movie.");
        }
    });

    actionsContainer.appendChild(heartCountSpan);
    actionsContainer.appendChild(heartButton);
    actionsContainer.appendChild(deleteButton);

    listItem.appendChild(itemText);
    listItem.appendChild(actionsContainer);

    return listItem;
}

/**
 * Adds a new movie item to the list.
 * Extracts the year, formats the display text, and handles duplicate/missing year logic.
 */
async function addTodo() {
    hideError();

    let todoTextFull = todoInput.value.trim();

    if (todoTextFull === '') {
        showError("Please enter some text.");
        return;
    }

    let year = null;
    let mainTextForDisplay = todoTextFull;

    const yearPattern = /\(?((?:18|19|20)\d{2}|2100)\)?/g;
    const allMatches = [...todoTextFull.matchAll(yearPattern)];

    if (allMatches.length > 0) {
        for (const match of allMatches) {
            const candidateYear = parseInt(match[1]);
            if (candidateYear >= 1800 && candidateYear <= 2100) {
                year = candidateYear;
                mainTextForDisplay = todoTextFull.replace(match[0], '').trim();
                mainTextForDisplay = mainTextForDisplay.replace(/\(\s*\)/g, '').trim();
                break;
            }
        }
    }

    const normalizedMovieTitle = mainTextForDisplay.toLowerCase();

    if (!year) {
        if (failedYearAttempts.has(normalizedMovieTitle)) {
            year = '???';
            failedYearAttempts.delete(normalizedMovieTitle);
        } else {
            showError("What year is the movie from?");
            failedYearAttempts.set(normalizedMovieTitle, true);
            return;
        }
    } else {
        failedYearAttempts.delete(normalizedMovieTitle);
    }

    if (await itemExists(mainTextForDisplay, year)) {
        showError("This movie is already in the list.");
        return;
    }

    try {
        const movieData = {
            title: mainTextForDisplay,
            normalizedTitle: normalizedMovieTitle,
            year: year.toString(),
            hearts: 0,
            createdAt: new Date().toISOString()
        };

        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(movieData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
        }

        todoInput.value = '';
        todoInput.focus();
        await fetchAndRenderMovies(); // Re-fetch and render to update UI
    } catch (e) {
        console.error("Error adding movie:", e);
        showError("Failed to add movie.");
    }
}
