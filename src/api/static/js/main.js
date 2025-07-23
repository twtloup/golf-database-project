// Main JavaScript for Golf Database Website

// Global utility functions and shared functionality

class GolfWebsite {
    constructor() {
        this.apiBase = '/api';
        this.currentPage = window.location.pathname;
        
        this.initializeGlobalFeatures();
        this.checkAPIHealth();
    }
    
    initializeGlobalFeatures() {
        // Set active navigation link
        this.setActiveNavigation();
        
        // Add mobile navigation toggle if needed
        this.setupMobileNavigation();
        
        // Add global event listeners
        this.setupGlobalEvents();
        
        // Initialize tooltips or other UI enhancements
        this.initializeUIEnhancements();
    }
    
    setActiveNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }
    
    setupMobileNavigation() {
        // Add hamburger menu for mobile if needed
        const navbar = document.querySelector('.navbar');
        if (navbar && window.innerWidth <= 768) {
            this.createMobileMenu();
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.createMobileMenu();
            } else {
                this.removeMobileMenu();
            }
        });
    }
    
    createMobileMenu() {
        const navContainer = document.querySelector('.nav-container');
        const navMenu = document.querySelector('.nav-menu');
        
        if (!navContainer || !navMenu) return;
        
        // Check if mobile toggle already exists
        if (navContainer.querySelector('.mobile-toggle')) return;
        
        // Create mobile toggle button
        const mobileToggle = document.createElement('button');
        mobileToggle.className = 'mobile-toggle';
        mobileToggle.innerHTML = '☰';
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('mobile-open');
        });
        
        navContainer.appendChild(mobileToggle);
        
        // Style the mobile menu
        navMenu.classList.add('mobile-menu');
    }
    
    removeMobileMenu() {
        const mobileToggle = document.querySelector('.mobile-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (mobileToggle) {
            mobileToggle.remove();
        }
        
        if (navMenu) {
            navMenu.classList.remove('mobile-menu', 'mobile-open');
        }
    }
    
    setupGlobalEvents() {
        // Handle escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
        
        // Handle clicks outside modals
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                e.target.remove();
            }
        });
        
        // Add loading states to buttons
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' && !e.target.disabled) {
                this.addButtonLoadingState(e.target);
            }
        });
    }
    
    initializeUIEnhancements() {
        // Add smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add fade-in animation for page elements
        this.addFadeInAnimations();
    }
    
    addFadeInAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observe elements that should fade in
        document.querySelectorAll('.feature-card, .player-card, .tournament-card, .course-card').forEach(el => {
            el.classList.add('fade-in-ready');
            observer.observe(el);
        });
    }
    
    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            if (response.ok && data.status === 'healthy') {
                console.log('✅ API is healthy:', data.data_summary);
                this.displayHealthStatus(true, data.data_summary);
            } else {
                console.warn('⚠️ API health check failed:', data);
                this.displayHealthStatus(false);
            }
        } catch (error) {
            console.error('❌ API health check error:', error);
            this.displayHealthStatus(false);
        }
    }
    
    displayHealthStatus(isHealthy, dataSummary = null) {
        // Only show status if we're on the homepage
        if (this.currentPage !== '/') return;
        
        const heroStats = document.querySelector('.hero-stats');
        if (!heroStats || !dataSummary) return;
        
        // Update the stats with real data
        const statCards = heroStats.querySelectorAll('.stat-card');
        if (statCards.length >= 4) {
            statCards[0].querySelector('h3').textContent = dataSummary.players || '748';
            statCards[1].querySelector('h3').textContent = dataSummary.tournaments || '333';
            statCards[2].querySelector('h3').textContent = `${Math.floor((dataSummary.tournament_results || 36864) / 1000)}K+`;
            statCards[3].querySelector('h3').textContent = dataSummary.courses || '92';
        }
    }
    
    closeAllModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => modal.remove());
    }
    
    addButtonLoadingState(button) {
        if (button.classList.contains('loading')) return;
        
        const originalText = button.textContent;
        button.classList.add('loading');
        button.disabled = true;
        button.textContent = 'Loading...';
        
        // Remove loading state after 3 seconds max
        setTimeout(() => {
            button.classList.remove('loading');
            button.disabled = false;
            button.textContent = originalText;
        }, 3000);
    }
    
    // Utility function to format numbers
    static formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
    
    // Utility function to format currency
    static formatCurrency(amount) {
        if (amount >= 1000000) {
            return `$${(amount / 1000000).toFixed(1)}M`;
        } else if (amount >= 1000) {
            return `$${(amount / 1000).toFixed(1)}K`;
        }
        return `$${amount}`;
    }
    
    // Utility function to format dates
    static formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    }
    
    // Show toast notifications
    static showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Style the toast
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 24px',
            borderRadius: '5px',
            color: 'white',
            fontWeight: '600',
            zIndex: '9999',
            animation: 'slideInRight 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800',
            error: '#F44336'
        };
        toast.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Global styles for animations and mobile menu
const globalStyles = `
<style>
.fade-in-ready {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}

.fade-in {
    opacity: 1;
    transform: translateY(0);
}

.mobile-toggle {
    display: none;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
}

.mobile-menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #2c5530;
    flex-direction: column;
    padding: 1rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.mobile-menu.mobile-open {
    display: flex;
}

.mobile-menu .nav-link {
    padding: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.loading {
    opacity: 0.7;
    cursor: not-allowed !important;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

@media (max-width: 768px) {
    .mobile-toggle {
        display: block;
    }
    
    .nav-menu {
        display: none;
    }
    
    .nav-container {
        position: relative;
    }
}
</style>
`;

// Initialize the website
document.addEventListener('DOMContentLoaded', () => {
    // Add global styles
    document.head.insertAdjacentHTML('beforeend', globalStyles);
    
    // Initialize the main website class
    window.golfWebsite = new GolfWebsite();
    
    // Make utility functions globally available
    window.GolfUtils = {
        formatNumber: GolfWebsite.formatNumber,
        formatCurrency: GolfWebsite.formatCurrency,
        formatDate: GolfWebsite.formatDate,
        showToast: GolfWebsite.showToast
    };
    
    console.log('🏌️ Golf Website initialized successfully!');
});