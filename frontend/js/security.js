/**
 * Frontend Security Utilities
 * Provides input validation, sanitization, and security functions
 */

class SecurityUtils {
    /**
     * Sanitize user input to prevent XSS attacks
     * @param {string} input - The input to sanitize
     * @returns {string} - Sanitized input
     */
    static sanitizeInput(input) {
        if (typeof input !== 'string') {
            return '';
        }
        
        // Remove potentially dangerous characters and scripts
        return input
            .replace(/[<>\"'&]/g, '')
            .replace(/javascript:/gi, '')
            .replace(/vbscript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .replace(/<script[^>]*>.*?<\/script>/gi, '')
            .trim();
    }
    
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} - True if valid email
     */
    static validateEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    }
    
    /**
     * Validate phone number format
     * @param {string} phone - Phone number to validate
     * @returns {boolean} - True if valid phone number
     */
    static validatePhone(phone) {
        const phoneRegex = /^[\d\s\-\+\(\)]{7,15}$/;
        return phoneRegex.test(phone);
    }
    
    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {object} - Validation result with errors array
     */
    static validatePassword(password) {
        const errors = [];
        
        if (!password || password.length < 8) {
            errors.push('Password must be at least 8 characters long');
        }
        
        if (!/[A-Z]/.test(password)) {
            errors.push('Password must contain at least one uppercase letter');
        }
        
        if (!/[a-z]/.test(password)) {
            errors.push('Password must contain at least one lowercase letter');
        }
        
        if (!/\d/.test(password)) {
            errors.push('Password must contain at least one digit');
        }
        
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            errors.push('Password must contain at least one special character');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    /**
     * Validate license number format
     * @param {string} licenseNumber - License number to validate
     * @returns {boolean} - True if valid license number
     */
    static validateLicenseNumber(licenseNumber) {
        const licenseRegex = /^[A-Z0-9\-\.\/\s]+$/;
        return licenseRegex.test(licenseNumber);
    }
    
    /**
     * Validate file type
     * @param {File} file - File to validate
     * @param {Array} allowedTypes - Array of allowed MIME types
     * @returns {boolean} - True if valid file type
     */
    static validateFileType(file, allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']) {
        return allowedTypes.includes(file.type);
    }
    
    /**
     * Validate file size
     * @param {File} file - File to validate
     * @param {number} maxSize - Maximum size in bytes (default: 16MB)
     * @returns {boolean} - True if file size is acceptable
     */
    static validateFileSize(file, maxSize = 16 * 1024 * 1024) {
        return file.size <= maxSize;
    }
    
    /**
     * Sanitize filename for safe storage
     * @param {string} filename - Filename to sanitize
     * @returns {string} - Sanitized filename
     */
    static sanitizeFilename(filename) {
        return filename
            .replace(/[<>:"/\\|?*]/g, '')
            .substring(0, 255);
    }
    
    /**
     * Generate CSRF token
     * @returns {string} - CSRF token
     */
    static generateCSRFToken() {
        return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    }
    
    /**
     * Validate form data
     * @param {object} formData - Form data to validate
     * @param {object} rules - Validation rules
     * @returns {object} - Validation result
     */
    static validateForm(formData, rules) {
        const errors = {};
        
        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];
            
            if (rule.required && (!value || value.trim() === '')) {
                errors[field] = `${field} is required`;
                continue;
            }
            
            if (value && rule.type === 'email' && !this.validateEmail(value)) {
                errors[field] = 'Invalid email format';
            }
            
            if (value && rule.type === 'phone' && !this.validatePhone(value)) {
                errors[field] = 'Invalid phone number format';
            }
            
            if (value && rule.type === 'password') {
                const passwordValidation = this.validatePassword(value);
                if (!passwordValidation.valid) {
                    errors[field] = passwordValidation.errors.join(', ');
                }
            }
            
            if (value && rule.minLength && value.length < rule.minLength) {
                errors[field] = `${field} must be at least ${rule.minLength} characters long`;
            }
            
            if (value && rule.maxLength && value.length > rule.maxLength) {
                errors[field] = `${field} must be no more than ${rule.maxLength} characters long`;
            }
        }
        
        return {
            valid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
    
    /**
     * Secure API request with authentication
     * @param {string} url - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} - Fetch promise
     */
    static secureRequest(url, options = {}) {
        const token = localStorage.getItem('auth_token');
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        return fetch(url, finalOptions);
    }
    
    /**
     * Log security events
     * @param {string} event - Event type
     * @param {object} details - Event details
     */
    static logSecurityEvent(event, details = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            event: event,
            details: details,
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        console.log('[SECURITY]', logEntry);
        
        // In production, send to logging service
        // this.sendToLoggingService(logEntry);
    }
    
    /**
     * Check if user is authenticated
     * @returns {boolean} - True if authenticated
     */
    static isAuthenticated() {
        const token = localStorage.getItem('auth_token');
        const userType = localStorage.getItem('user_type');
        const userId = localStorage.getItem('user_id');
        
        return !!(token && userType && userId);
    }
    
    /**
     * Clear authentication data
     */
    static logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_type');
        localStorage.removeItem('user_id');
        this.logSecurityEvent('LOGOUT');
    }
    
    /**
     * Prevent XSS in innerHTML usage
     * @param {string} html - HTML string to sanitize
     * @returns {string} - Sanitized HTML
     */
    static sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecurityUtils;
} 