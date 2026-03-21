// LemonKaijuOS First-Boot Wizard JavaScript

// Global wizard state
const wizardState = {
    currentStep: 1,
    totalSteps: 8,
    data: {}
};

// Utility functions
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="loading">${message}</p>`;
    }
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="success">✓ ${message}</p>`;
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="error">✗ ${message}</p>`;
    }
}

// Form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateUsername(username) {
    // Alphanumeric and underscore only, 3-16 characters
    const re = /^[a-z0-9_]{3,16}$/;
    return re.test(username);
}

function validatePassword(password) {
    // At least 8 characters
    return password.length >= 8;
}

// API helpers
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return { success: false, error: error.message };
    }
}

// Navigation
function goToStep(stepNumber) {
    if (stepNumber >= 1 && stepNumber <= wizardState.totalSteps) {
        window.location.href = `/step/${stepNumber}`;
    }
}

function nextStep() {
    goToStep(wizardState.currentStep + 1);
}

function previousStep() {
    goToStep(wizardState.currentStep - 1);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Right Arrow = Next
    if ((event.ctrlKey || event.metaKey) && event.key === 'ArrowRight') {
        const nextBtn = document.querySelector('.btn-primary');
        if (nextBtn) nextBtn.click();
    }
    
    // Ctrl/Cmd + Left Arrow = Back
    if ((event.ctrlKey || event.metaKey) && event.key === 'ArrowLeft') {
        const backBtn = document.querySelector('.btn-secondary');
        if (backBtn) backBtn.click();
    }
});

// Auto-save form data to localStorage
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            const key = `wizard_${formId}_${input.id}`;
            localStorage.setItem(key, input.value);
        });
        
        // Restore saved value
        const key = `wizard_${formId}_${input.id}`;
        const saved = localStorage.getItem(key);
        if (saved) {
            input.value = saved;
        }
    });
}

// Clear saved form data
function clearSavedData() {
    Object.keys(localStorage).forEach(key => {
        if (key.startsWith('wizard_')) {
            localStorage.removeItem(key);
        }
    });
}

// Smooth scroll for long pages
function smoothScroll(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Tooltip management
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', showTooltip);
        trigger.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.position = 'absolute';
    tooltip.style.top = (event.pageY + 10) + 'px';
    tooltip.style.left = (event.pageX + 10) + 'px';
    document.body.appendChild(tooltip);
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                setTimeout(() => this.classList.remove('loading'), 2000);
            }
        });
    });
});

// Export for use in templates
window.wizardUtils = {
    apiCall,
    showLoading,
    showSuccess,
    showError,
    validateEmail,
    validateUsername,
    validatePassword,
    goToStep,
    nextStep,
    previousStep,
    smoothScroll
};
