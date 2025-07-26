// Dashboard JavaScript Functionality

class SupplyDashboard {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupNavigation();
        this.setupEventListeners();
        this.loadDashboardData();
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const sunIcon = document.getElementById('sunIcon');
        const moonIcon = document.getElementById('moonIcon');
        const body = document.body;

        // Set initial theme
        body.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon(this.currentTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.updateThemeIcon(newTheme);
            this.currentTheme = newTheme;
        });
    }

    updateThemeIcon(theme) {
        const sunIcon = document.getElementById('sunIcon');
        const moonIcon = document.getElementById('moonIcon');
        
        if (theme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const pageContents = document.querySelectorAll('.page-content');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                link.classList.add('active');
                
                // Hide all page contents
                pageContents.forEach(content => {
                    content.style.display = 'none';
                });
                
                // Show the corresponding page
                const targetPage = link.getAttribute('data-page');
                const targetContent = document.getElementById(targetPage + '-page');
                if (targetContent) {
                    targetContent.style.display = 'block';
                    this.loadPageData(targetPage);
                }
            });
        });
    }

    setupEventListeners() {
        // Setup edit buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.edit-btn')) {
                this.handleEdit(e.target.closest('tr'));
            }
            
            if (e.target.closest('.delete-btn')) {
                this.handleDelete(e.target.closest('tr'));
            }
            
            if (e.target.closest('.add-stock-btn')) {
                this.showAddStockModal();
            }
        });

        // Setup search functionality
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
    }

    handleEdit(row) {
        const productName = row.cells[0].textContent;
        this.showNotification(`Edit functionality for ${productName} will be implemented here`, 'info');
    }

    handleDelete(row) {
        const productName = row.cells[0].textContent;
        if (confirm(`Are you sure you want to delete ${productName}?`)) {
            this.showNotification(`${productName} deleted successfully`, 'success');
            // Here you would typically make an API call to delete the item
            // row.remove(); // Remove from DOM
        }
    }

    showAddStockModal() {
        this.showNotification('Add new stock modal will be implemented here', 'info');
    }

    handleSearch(query) {
        const tableRows = document.querySelectorAll('.stocks-table tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    loadDashboardData() {
        // Simulate loading dashboard data
        this.updateStats();
    }

    loadPageData(page) {
        switch(page) {
            case 'stocks':
                this.loadStocksData();
                break;
            case 'analytics':
                this.loadAnalyticsData();
                break;
            default:
                break;
        }
    }

    updateStats() {
        // Simulate updating statistics
        const statValues = document.querySelectorAll('.stat-value');
        statValues.forEach(stat => {
            const currentValue = parseInt(stat.textContent.replace(/[^\d]/g, ''));
            const newValue = currentValue + Math.floor(Math.random() * 10);
            stat.textContent = stat.textContent.replace(/\d+/, newValue);
        });
    }

    loadStocksData() {
        // Simulate loading stocks data
        this.showNotification('Stocks data loaded', 'success');
    }

    loadAnalyticsData() {
        // Simulate loading analytics data
        this.showNotification('Analytics data loaded', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Utility functions
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SupplyDashboard();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupplyDashboard;
} 