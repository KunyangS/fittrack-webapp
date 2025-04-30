// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement; // Target the <html> element
    const moonIcon = darkModeToggle.querySelector('.fa-moon');
    const sunIcon = darkModeToggle.querySelector('.fa-sun');

    // Function to apply theme based on preference
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            moonIcon.style.display = 'none'; // Hide moon
            sunIcon.style.display = 'inline-block'; // Show sun
        } else {
            htmlElement.classList.remove('dark');
            moonIcon.style.display = 'inline-block'; // Show moon
            sunIcon.style.display = 'none'; // Hide sun
        }
    };

    // Check localStorage first
    let preferredTheme = localStorage.getItem('theme');

    // If no preference in localStorage, check system preference
    if (!preferredTheme) {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            preferredTheme = 'dark';
        } else {
            preferredTheme = 'light'; // Default to light
        }
    }

    // Apply the determined theme on initial load
    applyTheme(preferredTheme);

    // Add event listener to the toggle button
    darkModeToggle.addEventListener('click', () => {
        // Toggle the theme
        if (htmlElement.classList.contains('dark')) {
            preferredTheme = 'light';
            localStorage.setItem('theme', 'light'); // Save preference
        } else {
            preferredTheme = 'dark';
            localStorage.setItem('theme', 'dark'); // Save preference
        }
        // Apply the new theme
        applyTheme(preferredTheme);
    });

    // Optional: Listen for system theme changes (if user changes OS theme while site is open)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        // Only change if no explicit preference is set in localStorage
        if (!localStorage.getItem('theme')) {
            const newColorScheme = event.matches ? "dark" : "light";
            applyTheme(newColorScheme);
        }
    });

    console.log("Fitness Tracker JS Initialized. Current theme:", preferredTheme);
});
// --- Smooth Scroll for Sidebar Menu ---
document.querySelectorAll('#sidebar a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // --- Scroll Animations on Sections ---
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
      }
    });
  });
  document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
  });
  
  // --- Loading Spinner ---
  window.addEventListener('load', () => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
      spinner.style.display = 'none';
    }
  });
  
  // --- Back to Top Button ---
  window.addEventListener('scroll', () => {
    const backToTop = document.getElementById('backToTop');
    if (window.scrollY > 300) {
      backToTop.classList.remove('hidden');
    } else {
      backToTop.classList.add('hidden');
    }
  });
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  