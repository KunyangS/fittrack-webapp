// UI Enhancement JavaScript - Page enhancement script without modifying original HTML

document.addEventListener('DOMContentLoaded', function() {
    // Dynamically load enhancement CSS
    const enhancementCss = document.createElement('link');
    enhancementCss.rel = 'stylesheet';
    enhancementCss.href = '/static/css/enhancement.css';
    document.head.appendChild(enhancementCss);
    
    // Detect page type
    const isLoginPage = window.location.pathname.includes('login') || 
                         document.querySelector('form[action*="login"]') ||
                         (document.querySelector('form input[name="email"]') && 
                          document.querySelector('form input[name="password"]'));
    
    // Dynamically load background enhancement script
    const backgroundScript = document.createElement('script');
    backgroundScript.src = '/static/js/background-enhancement.js';
    document.body.appendChild(backgroundScript);

    // Page initialization animation
    document.body.classList.add('page-transition');

    // If login page, don't apply floating label enhancement to forms
    if (isLoginPage) {
        console.log('Login page detected, applying special enhancements...');
        document.querySelectorAll('form').forEach(form => {
            form.classList.add('login-enhanced');
        });
        return; // Don't continue with the rest of the form enhancement functions
    }

    // Add animation effect class to form containers
    const exerciseContainer = document.getElementById('exerciseContainer');
    if (exerciseContainer) {
        exerciseContainer.classList.add('animate-children');
        const exerciseBlocks = exerciseContainer.querySelectorAll('.exercise-block');
        exerciseBlocks.forEach(block => {
            block.classList.add('interactive-hover');
        });
    }

    const foodContainer = document.getElementById('foodContainer');
    if (foodContainer) {
        foodContainer.classList.add('animate-children');
        const foodBlocks = foodContainer.querySelectorAll('div');
        foodBlocks.forEach(block => {
            block.classList.add('interactive-hover');
        });
    }

    // Add effects to form titles
    const formTitles = document.querySelectorAll('h2, h3');
    formTitles.forEach(title => {
        title.classList.add('shimmer');
    });

    // Add effects to submit buttons
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.classList.add('btn-float');
    }

    // Add effects to add buttons
    const addBtns = document.querySelectorAll('#addExerciseBtn, #addFoodBtn');
    addBtns.forEach(btn => {
        btn.classList.add('btn-pulse');
    });

    // Animation for form areas when entering viewport
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const sections = document.querySelectorAll('.glass-effect, .bg-light-bg');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        observer.observe(section);
    });

    // Dynamically add floating label effect - skip login page
    const enhanceFormControls = () => {
        if (isLoginPage) return; // Don't add floating labels to login page
        
        const inputs = document.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            // Skip input fields that have already been processed
            if (input.parentElement.classList.contains('form-control')) return;
            
            // Get adjacent label or create a new one
            let label = input.nextElementSibling;
            if (!label || label.tagName !== 'LABEL') {
                label = document.createElement('label');
                let placeholder = input.getAttribute('placeholder');
                if (!placeholder && input.tagName === 'SELECT') {
                    const firstOption = input.querySelector('option');
                    placeholder = firstOption ? firstOption.textContent : '';
                }
                label.textContent = placeholder || input.name;
                
                // Wrap the input field in a div
                const wrapper = document.createElement('div');
                wrapper.classList.add('form-control');
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
                wrapper.appendChild(label);
            }
        });
    };

    // Delay execution to ensure all original scripts have loaded
    setTimeout(enhanceFormControls, 500);

    // Add animation when adding new form items
    const originalAddExercise = window.addExercise;
    if (typeof originalAddExercise === 'function') {
        window.addExercise = function() {
            originalAddExercise();
            // Apply styles to newly added elements
            const blocks = document.querySelectorAll('.exercise-block');
            const lastBlock = blocks[blocks.length - 1];
            if (lastBlock) {
                lastBlock.classList.add('interactive-hover');
                lastBlock.style.opacity = 0;
                setTimeout(() => {
                    lastBlock.classList.add('fade-in-up');
                    lastBlock.style.opacity = 1;
                }, 10);
                
                // Add floating labels to newly added input fields
                enhanceFormControls();
            }
        };
    }

    const originalAddFood = window.addFood;
    if (typeof originalAddFood === 'function') {
        window.addFood = function() {
            originalAddFood();
            // Apply styles to newly added elements
            const blocks = document.querySelectorAll('#foodContainer > div');
            const lastBlock = blocks[blocks.length - 1];
            if (lastBlock) {
                lastBlock.classList.add('interactive-hover');
                lastBlock.style.opacity = 0;
                setTimeout(() => {
                    lastBlock.classList.add('fade-in-up');
                    lastBlock.style.opacity = 1;
                }, 10);
                
                // Add floating labels to newly added input fields
                enhanceFormControls();
            }
        };
    }
    
    // Form validation beautification
    const form = document.getElementById('uploadForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('input[required]');
            let hasError = false;
            
            requiredInputs.forEach(input => {
                if (!input.value) {
                    input.classList.add('border-red-500');
                    input.classList.add('shake-animation');
                    
                    // Add shake animation
                    if (!document.querySelector('.shake-keyframes')) {
                        const style = document.createElement('style');
                        style.classList.add('shake-keyframes');
                        style.textContent = `
                            @keyframes shake {
                                0%, 100% { transform: translateX(0); }
                                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                                20%, 40%, 60%, 80% { transform: translateX(5px); }
                            }
                            .shake-animation {
                                animation: shake 0.6s ease-in-out;
                            }
                        `;
                        document.head.appendChild(style);
                    }
                    
                    // Remove animation class so it can be triggered again
                    setTimeout(() => {
                        input.classList.remove('shake-animation');
                    }, 600);
                    
                    hasError = true;
                } else {
                    input.classList.remove('border-red-500');
                }
            });
            
            if (hasError) {
                e.preventDefault();
            }
        });
    }
}); 