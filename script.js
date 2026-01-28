// ============================================
// NAVIGATION & INTERACTION SCRIPTS
// ============================================

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Toggle active nav link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

// ============================================
// LOGIN FORM HANDLER
// ============================================

function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    // Validate inputs
    if (!email || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    // Validate email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address');
        return;
    }
    
    // Show dashboard
    document.getElementById('loginForm').style.display = 'none';
    document.querySelector('.login-divider').style.display = 'none';
    document.querySelectorAll('.btn-secondary')[0].style.display = 'none';
    document.querySelector('.login-footer').style.display = 'none';
    
    const dashboardCard = document.getElementById('dashboardCard');
    dashboardCard.style.display = 'block';
    
    // Extract name from email
    const userName = email.split('@')[0];
    const firstLetter = userName.charAt(0).toUpperCase();
    const restOfName = userName.slice(1);
    const displayName = firstLetter + restOfName;
    
    document.getElementById('welcomeUser').textContent = 'Welcome, ' + displayName + '!';
    
    // Store login info if remember is checked
    if (remember) {
        localStorage.setItem('userEmail', email);
        localStorage.setItem('rememberMe', 'true');
    }
}

// ============================================
// REGISTRATION FORM HANDLER
// ============================================

function handleRegister(event) {
    event.preventDefault();
    
    const institution = document.getElementById('institution').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const agree = document.getElementById('agree').checked;
    
    // Validate inputs
    if (!institution || !email || !password || !confirmPassword) {
        alert('Please fill in all fields');
        return;
    }
    
    // Validate email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address');
        return;
    }
    
    // Validate password length
    if (password.length < 8) {
        alert('Password must be at least 8 characters long');
        return;
    }
    
    // Validate password match
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }
    
    // Validate terms agreement
    if (!agree) {
        alert('You must agree to the Terms of Service and Privacy Policy');
        return;
    }
    
    // Show success message
    alert('Account created successfully! Your account is pending admin verification.\nYou will receive an email confirmation once verified.');
    
    // Reset form and go back to login
    document.getElementById('registerForm').reset();
    toggleRegister();
}

// ============================================
// TOGGLE BETWEEN LOGIN AND REGISTER
// ============================================

function toggleRegister() {
    const loginCard = document.querySelector('.login-card');
    const registerCard = document.getElementById('registerCard');
    const loginDivider = document.querySelector('.login-divider');
    const buttons = document.querySelectorAll('.btn-secondary');
    const loginFooter = document.querySelector('.login-footer');
    
    loginCard.style.display = loginCard.style.display === 'none' ? 'block' : 'none';
    registerCard.style.display = registerCard.style.display === 'none' ? 'block' : 'none';
    
    // Hide divider and buttons when showing register, show when showing login
    if (registerCard.style.display === 'block') {
        loginDivider.style.display = 'none';
        buttons[0].style.display = 'none';
        loginFooter.style.display = 'none';
    } else {
        loginDivider.style.display = 'block';
        buttons[0].style.display = 'block';
        loginFooter.style.display = 'block';
    }
}

// ============================================
// LOGOUT HANDLER
// ============================================

function handleLogout() {
    // Hide dashboard
    document.getElementById('dashboardCard').style.display = 'none';
    
    // Show login form
    document.getElementById('loginForm').style.display = 'flex';
    document.querySelector('.login-divider').style.display = 'block';
    document.querySelectorAll('.btn-secondary')[0].style.display = 'block';
    document.querySelector('.login-footer').style.display = 'block';
    
    // Reset form
    document.getElementById('loginForm').reset();
    
    // Clear localStorage
    localStorage.removeItem('userEmail');
    localStorage.removeItem('rememberMe');
}

// ============================================
// PAGE LOAD - CHECK FOR SAVED LOGIN
// ============================================

window.addEventListener('load', function() {
    // Check if this is the login page
    if (document.getElementById('loginForm')) {
        const savedEmail = localStorage.getItem('userEmail');
        const rememberMe = localStorage.getItem('rememberMe');
        
        if (savedEmail && rememberMe === 'true') {
            document.getElementById('email').value = savedEmail;
            document.getElementById('remember').checked = true;
        }
    }
});

// ============================================
// FORM VALIDATION - REAL TIME
// ============================================

// Email validation with visual feedback
const emailInputs = document.querySelectorAll('input[type="email"]');
emailInputs.forEach(input => {
    input.addEventListener('blur', function() {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (this.value && !emailPattern.test(this.value)) {
            this.style.borderColor = '#d32f2f';
        } else {
            this.style.borderColor = '#e0e0e0';
        }
    });
});

// Password strength indicator (optional)
const passwordInputs = document.querySelectorAll('input[type="password"]');
passwordInputs.forEach(input => {
    input.addEventListener('input', function() {
        if (this.value.length < 6) {
            this.style.borderColor = '#d32f2f';
        } else if (this.value.length < 10) {
            this.style.borderColor = '#ff9800';
        } else {
            this.style.borderColor = '#4caf50';
        }
    });
});

// ============================================
// ACCESSIBILITY & KEYBOARD NAVIGATION
// ============================================

// Allow form submission with Enter key
document.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
        const form = event.target.closest('form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
});

// ============================================
// MOBILE MENU TOGGLE (if needed)
// ============================================

function toggleMobileMenu() {
    const navbar = document.querySelector('.navbar');
    if (navbar.style.display === 'flex') {
        navbar.style.display = 'none';
    } else {
        navbar.style.display = 'flex';
    }
}

// ============================================
// SCROLL TO TOP BUTTON (optional)
// ============================================

// Show scroll-to-top button when scrolled down
let scrollToTopBtn = document.createElement('button');
scrollToTopBtn.innerHTML = '↑ Top';
scrollToTopBtn.id = 'scrollToTop';
scrollToTopBtn.style.display = 'none';
scrollToTopBtn.style.position = 'fixed';
scrollToTopBtn.style.bottom = '30px';
scrollToTopBtn.style.right = '30px';
scrollToTopBtn.style.zIndex = '999';
scrollToTopBtn.style.padding = '12px 20px';
scrollToTopBtn.style.backgroundColor = '#1f3c88';
scrollToTopBtn.style.color = 'white';
scrollToTopBtn.style.border = 'none';
scrollToTopBtn.style.borderRadius = '6px';
scrollToTopBtn.style.cursor = 'pointer';
scrollToTopBtn.style.fontSize = '14px';
scrollToTopBtn.style.fontWeight = '600';
scrollToTopBtn.style.transition = 'all 0.3s ease';

document.body.appendChild(scrollToTopBtn);

window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

scrollToTopBtn.addEventListener('click', function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

scrollToTopBtn.addEventListener('mouseover', function() {
    this.style.backgroundColor = '#2c7da0';
    this.style.transform = 'translateY(-3px)';
    this.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
});

scrollToTopBtn.addEventListener('mouseout', function() {
    this.style.backgroundColor = '#1f3c88';
    this.style.transform = 'translateY(0)';
    this.style.boxShadow = 'none';
});

// ============================================
// ANIMATION ON SCROLL (simple)
// ============================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards and module cards
document.querySelectorAll('.feature-card, .module-card, .metric-card, .attack-card, .problem-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// ============================================
// PERFORMANCE TRACKING (optional analytics)
// ============================================

// Log page load time
window.addEventListener('load', function() {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log('Page Load Time: ' + pageLoadTime + 'ms');
});

// ============================================
// ERROR HANDLING
// ============================================

window.addEventListener('error', function(event) {
    console.error('Error:', event.error);
    // You can send error logs to a server here
});

// ============================================
// DOCUMENT READY - INITIALIZE
// ============================================

console.log('SecureHealth AI - Federated Learning Platform Loaded');
console.log('Version 1.0 | College Project');
