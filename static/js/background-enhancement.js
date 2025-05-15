// Background Enhancement JavaScript - No modifications to original HTML

document.addEventListener('DOMContentLoaded', function() {
    // Dynamically load background enhancement CSS
    const backgroundEnhancementCss = document.createElement('link');
    backgroundEnhancementCss.rel = 'stylesheet';
    backgroundEnhancementCss.href = '/static/css/background-enhancement.css';
    document.head.appendChild(backgroundEnhancementCss);

    // Add background pattern element
    const bgPattern = document.createElement('div');
    bgPattern.className = 'bg-pattern';
    document.body.appendChild(bgPattern);

    // Add lighting effect element
    const spotlight = document.createElement('div');
    spotlight.className = 'spotlight';
    document.body.appendChild(spotlight);

    // Add special class for login page to apply specific CSS rules
    if (document.querySelector('form[action*="login"]') || 
        window.location.pathname.includes('login') || 
        document.querySelector('form input[name="email"]')) {
        document.querySelectorAll('form').forEach(form => {
            form.classList.add('login-enhanced');
        });
        
        // Add special class to login form fields
        document.querySelectorAll('label').forEach(label => {
            label.classList.add('enhanced-label');
        });
    }

    // Add particle effect
    createParticles();

    // Listen for scroll events to add parallax effect to background
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        if (spotlight) {
            spotlight.style.transform = `translateY(${scrollPosition * 0.05}px)`;
        }
        if (bgPattern) {
            bgPattern.style.transform = `translateY(${scrollPosition * 0.02}px)`;
        }
    });

    // Listen for mouse movement to add interactive effects to background
    document.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        if (spotlight) {
            spotlight.style.backgroundPosition = `${mouseX * 100}% ${mouseY * 100}%`;
        }
    });
});

// Create particle effect
function createParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle';
    document.body.appendChild(particleContainer);

    // Determine number of particles (based on screen size)
    const particleCount = Math.min(20, Math.floor(window.innerWidth / 100));
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        createParticle(particleContainer);
    }
}

// Create a single particle
function createParticle(container) {
    const particle = document.createElement('div');
    
    // Random particle size
    const size = Math.random() * 6 + 2;
    
    // Random position
    const posX = Math.random() * 100;
    const posY = Math.random() * 100;
    
    // Random opacity
    const opacity = Math.random() * 0.4 + 0.1;
    
    // Random animation delay
    const delay = Math.random() * 15;
    
    // Random color (selected from theme colors)
    const colors = [
        'rgba(99, 102, 241, ' + opacity + ')',  // Primary
        'rgba(165, 180, 252, ' + opacity + ')', // Primary light
        'rgba(139, 92, 246, ' + opacity + ')',  // Purple
        'rgba(124, 58, 237, ' + opacity + ')'   // Violet
    ];
    const color = colors[Math.floor(Math.random() * colors.length)];
    
    // Set particle style
    particle.style.cssText = `
        position: absolute;
        top: ${posY}%;
        left: ${posX}%;
        width: ${size}px;
        height: ${size}px;
        background-color: ${color};
        border-radius: 50%;
        opacity: ${opacity};
        pointer-events: none;
        animation: float ${Math.random() * 10 + 10}s ease-in-out ${delay}s infinite;
    `;
    
    // Add to container
    container.appendChild(particle);
}

// Add breathing effect to important elements
function addBreathingEffect() {
    // Get important elements
    const importantElements = document.querySelectorAll('.hero-content, .feature-card');
    
    importantElements.forEach(element => {
        element.style.animation = 'breathing 5s ease-in-out infinite';
    });
} 