// FitTrack Main JavaScript File
// Handles site-wide functionality including dark mode, animations, and UI enhancements

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
    
    // ===== EDEN'S UI ENHANCEMENTS =====
    console.log("FitTrack UI Enhancements Initialized - " + new Date().toISOString());
    
    // Initialize UI components
    initializeSmoothScroll();
    initializeScrollAnimations();
    initializeTooltips();
    setupLoadingSpinner();
    initializeBackToTop();
    initializeToasts();
    addImageHoverEffects();

    // ===== SMOOTH SCROLL =====
    function initializeSmoothScroll() {
        // Add smooth scrolling to all anchor links
        document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // If we have a URL hash, update it
                    history.pushState(null, null, this.getAttribute('href'));
                }
            });
        });
    }

    // ===== SCROLL ANIMATIONS =====
    function initializeScrollAnimations() {
        // Add fade-in animations to sections and cards
        if ('IntersectionObserver' in window) {
            const fadeElements = document.querySelectorAll('.card, section, .dashboard-card');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in-up');
                        observer.unobserve(entry.target); // Stop observing once animated
                    }
                });
            }, {
                root: null,
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });
            
            fadeElements.forEach(element => {
                observer.observe(element);
            });
        }
    }

    // ===== TOOLTIPS =====
    function initializeTooltips() {
        // Initialize tooltips on elements with data-tooltip attribute
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            // We'll use the browser's built-in tooltip (title attribute)
            element.setAttribute('title', element.getAttribute('data-tooltip'));
            
            // Add a custom class for styling
            element.classList.add('has-tooltip');
        });
    }

    // ===== LOADING SPINNER =====
    function setupLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            window.addEventListener('load', () => {
                spinner.style.opacity = '0';
                setTimeout(() => {
                    spinner.style.display = 'none';
                }, 300);
            });
        }
    }

    // ===== BACK TO TOP BUTTON =====
    function initializeBackToTop() {
        const backToTopButton = document.getElementById('backToTop');
        
        if (backToTopButton) {
            // Show button when scrolled down
            window.addEventListener('scroll', () => {
                if (window.scrollY > 300) {
                    backToTopButton.classList.add('visible');
                } else {
                    backToTopButton.classList.remove('visible');
                }
            });
            
            // Initial check (in case page is refreshed while scrolled down)
            if (window.scrollY > 300) {
                backToTopButton.classList.add('visible');
            }
        }
    }

    // ===== TOAST NOTIFICATIONS =====
    function initializeToasts() {
        // Handle auto-dismissing flash messages
        const toasts = document.querySelectorAll('.flash-messages > div');
        
        if (toasts.length > 0) {
            setTimeout(() => {
                toasts.forEach(toast => {
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateY(-20px)';
                    setTimeout(() => {
                        toast.remove();
                    }, 300);
                });
            }, 5000);
            
            // Add close button functionality
            document.querySelectorAll('.flash-messages button').forEach(button => {
                button.addEventListener('click', function() {
                    const toast = this.closest('.flash-messages > div');
                    if (toast) {
                        toast.style.opacity = '0';
                        toast.style.transform = 'translateY(-20px)';
                        setTimeout(() => {
                            toast.remove();
                        }, 300);
                    }
                });
            });
        }
    }
    
    // ===== IMAGE HOVER EFFECTS =====
    function addImageHoverEffects() {
        // Add zoom effect class to images that don't have it yet
        const images = document.querySelectorAll('img:not(.no-zoom):not(.zoom-hover)');
        images.forEach(img => {
            // Don't add to profile images or logos
            if (!img.closest('.user-dropdown') && !img.parentElement.closest('header')) {
                img.classList.add('zoom-hover');
                // Wrap in div if not already wrapped
                if (img.parentElement.nodeName !== 'DIV') {
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('overflow-hidden', 'rounded');
                    img.parentNode.insertBefore(wrapper, img);
                    wrapper.appendChild(img);
                }
            }
        });
    }
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
const backToTopButton = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
});

// Global function for scroll to top (used by the button)
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
