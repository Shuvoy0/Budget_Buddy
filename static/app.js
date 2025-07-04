// Budget Buddy - Enhanced JavaScript Functionality

// Global utilities
const BudgetBuddy = {
    // Format currency consistently
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format date consistently
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Show toast notifications
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Style the toast
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '9999',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#06b6d4'
        };
        toast.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);

        // Animate out and remove
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    },

    // Validate form fields
    validateField(field, rules) {
        const value = field.value.trim();
        const errors = [];

        if (rules.required && !value) {
            errors.push('This field is required');
        }

        if (rules.minLength && value.length < rules.minLength) {
            errors.push(`Minimum length is ${rules.minLength} characters`);
        }

        if (rules.maxLength && value.length > rules.maxLength) {
            errors.push(`Maximum length is ${rules.maxLength} characters`);
        }

        if (rules.min && parseFloat(value) < rules.min) {
            errors.push(`Minimum value is ${rules.min}`);
        }

        if (rules.max && parseFloat(value) > rules.max) {
            errors.push(`Maximum value is ${rules.max}`);
        }

        if (rules.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            errors.push('Please enter a valid email address');
        }

        return errors;
    },

    // Add loading state to buttons
    setButtonLoading(button, loading = true) {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    },

    // Animate numbers (count up effect)
    animateNumber(element, finalValue, duration = 1000) {
        const startValue = 0;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out animation
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (finalValue - startValue) * easeProgress;
            
            element.textContent = BudgetBuddy.formatCurrency(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }
};

// Enhanced form handling
document.addEventListener('DOMContentLoaded', function() {
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                BudgetBuddy.setButtonLoading(submitButton, true);
                
                // Reset loading state after 5 seconds if form hasn't submitted
                setTimeout(() => {
                    BudgetBuddy.setButtonLoading(submitButton, false);
                }, 5000);
            }
        });
    });

    // Auto-save form data to localStorage
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    autoSaveForms.forEach(form => {
        const formId = form.dataset.autosave;
        
        // Load saved data
        const savedData = localStorage.getItem(`budgetbuddy_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(name => {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field && field.type !== 'password') {
                        field.value = data[name];
                    }
                });
            } catch (e) {
                console.warn('Failed to load saved form data');
            }
        }

        // Save data on input
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [name, value] of formData.entries()) {
                if (name !== 'password') { // Don't save passwords
                    data[name] = value;
                }
            }
            localStorage.setItem(`budgetbuddy_${formId}`, JSON.stringify(data));
        });

        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            setTimeout(() => {
                localStorage.removeItem(`budgetbuddy_${formId}`);
            }, 1000);
        });
    });

    // Animate stats numbers on dashboard
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(element => {
        const text = element.textContent;
        const match = text.match(/\$?([\d,]+\.?\d*)/);
        if (match) {
            const value = parseFloat(match[1].replace(/,/g, ''));
            if (!isNaN(value)) {
                element.textContent = '$0.00';
                BudgetBuddy.animateNumber(element, value);
            }
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#searchFilter');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal[style*="flex"]');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });

    // Progressive Web App features
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js').then(function(registration) {
                console.log('SW registered: ', registration);
            }).catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
        });
    }

    // Dark mode toggle (future feature)
    const darkModeToggle = document.querySelector('#darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });

        // Load saved dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    }

    // Handle offline status
    window.addEventListener('online', function() {
        BudgetBuddy.showToast('You are back online!', 'success');
    });

    window.addEventListener('offline', function() {
        BudgetBuddy.showToast('You are offline. Some features may not work.', 'warning');
    });
});

// Export for use in templates
window.BudgetBuddy = BudgetBuddy;