// Language Switcher Component
class LanguageSwitcher {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'hi'; // Default to Hindi
        this.translations = {
            hi: {
                // Navigation
                'home': 'होम',
                'login': 'लॉगिन',
                'signup': 'साइनअप',
                'profile': 'प्रोफाइल',
                'dashboard': 'डैशबोर्ड',
                'logout': 'लॉगआउट',
                'edit': 'संपादित करें',
                'save': 'सहेजें',
                'back': 'वापस',
                'continue': 'जारी रखें',
                
                // Forms
                'business_name': 'व्यवसाय का नाम',
                'email': 'ईमेल',
                'phone': 'फोन',
                'password': 'पासवर्ड',
                'address': 'पता',
                'city': 'शहर',
                'state': 'राज्य',
                'pincode': 'पिनकोड',
                'country': 'देश',
                
                // Cart & Checkout
                'shopping_cart': 'खरीदारी कार्ट',
                'order_summary': 'आदेश सारांश',
                'subtotal': 'उप-कुल',
                'total': 'कुल',
                'checkout': 'चेकआउट',
                'place_order': 'आदेश दें',
                'empty_cart': 'आपकी कार्ट खाली है',
                'continue_shopping': 'खरीदारी जारी रखें',
                
                // Messages
                'order_success': 'आदेश सफलतापूर्वक दिया गया',
                'login_failed': 'लॉगिन विफल',
                'try_again': 'कृपया पुनः प्रयास करें',
                'loading': 'लोड हो रहा है...',
                'processing': 'प्रोसेसिंग...',
                
                // Settings
                'account_settings': 'खाता सेटिंग्स',
                'profile_settings': 'प्रोफाइल सेटिंग्स',
                'security_settings': 'सुरक्षा सेटिंग्स',
                'business_settings': 'व्यवसाय सेटिंग्स',
                'license_verification': 'लाइसेंस सत्यापन',
                
                // Welcome
                'welcome': 'स्वागत है',
                'welcome_message': 'OverXchange में आपका स्वागत है',
                'welcome_description': 'भारतीय स्ट्रीट फूड वेंडर्स को विश्वसनीय और सस्ते आपूर्तिकर्ताओं से कच्चा माल प्राप्त करने में सशक्त बनाना।<br>वेंडर्स को आपूर्तिकर्ताओं से डिजिटल रूप से जोड़ना',
                'get_started': 'शुरू करें',
                
                // Language
                'language': 'भाषा',
                'hindi': 'हिंदी',
                'english': 'अंग्रेज़ी',
                'select_language': 'भाषा चुनें'
            },
            en: {
                // Navigation
                'home': 'Home',
                'login': 'Login',
                'signup': 'Signup',
                'profile': 'Profile',
                'dashboard': 'Dashboard',
                'logout': 'Logout',
                'edit': 'Edit',
                'save': 'Save',
                'back': 'Back',
                'continue': 'Continue',
                
                // Forms
                'business_name': 'Business Name',
                'email': 'Email',
                'phone': 'Phone',
                'password': 'Password',
                'address': 'Address',
                'city': 'City',
                'state': 'State',
                'pincode': 'Pincode',
                'country': 'Country',
                
                // Cart & Checkout
                'shopping_cart': 'Shopping Cart',
                'order_summary': 'Order Summary',
                'subtotal': 'Subtotal',
                'total': 'Total',
                'checkout': 'Checkout',
                'place_order': 'Place Order',
                'empty_cart': 'Your cart is empty',
                'continue_shopping': 'Continue Shopping',
                
                // Messages
                'order_success': 'Order placed successfully',
                'login_failed': 'Login failed',
                'try_again': 'Please try again',
                'loading': 'Loading...',
                'processing': 'Processing...',
                
                // Settings
                'account_settings': 'Account Settings',
                'profile_settings': 'Profile Settings',
                'security_settings': 'Security Settings',
                'business_settings': 'Business Settings',
                'license_verification': 'License Verification',
                
                // Welcome
                'welcome': 'Welcome',
                'welcome_message': 'Welcome to OverXchange',
                'welcome_description': 'Empowering Indian street food vendors to source raw materials from trusted and affordable suppliers.<br>Connecting Vendors to Suppliers Digitally',
                'get_started': 'Get Started',
                
                // Language
                'language': 'Language',
                'hindi': 'Hindi',
                'english': 'English',
                'select_language': 'Select Language'
            }
        };
        
        this.init();
    }
    
    init() {
        this.updatePageLanguage();
        this.createLanguageSwitcher();
    }
    
    // Get translation for a key
    getText(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
    
    // Switch language
    switchLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('language', lang);
        this.updatePageLanguage();
        this.updateLanguageSwitcher();
    }
    
    // Update page language
    updatePageLanguage() {
        document.documentElement.lang = this.currentLanguage;
        this.translatePageContent();
    }
    
    // Create language switcher UI
    createLanguageSwitcher() {
        // Check if switcher already exists
        if (document.getElementById('language-switcher')) {
            return;
        }
        
        const switcher = document.createElement('div');
        switcher.id = 'language-switcher';
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <div class="language-switcher-container">
                <button class="language-btn ${this.currentLanguage === 'hi' ? 'active' : ''}" onclick="languageSwitcher.switchLanguage('hi')">
                    <span class="flag">🇮🇳</span>
                    <span class="lang-text">हिंदी</span>
                </button>
                <button class="language-btn ${this.currentLanguage === 'en' ? 'active' : ''}" onclick="languageSwitcher.switchLanguage('en')">
                    <span class="flag">🇺🇸</span>
                    <span class="lang-text">English</span>
                </button>
            </div>
        `;
        
        // Add styles
        this.addLanguageSwitcherStyles();
        
        // Add to navbar if exists
        const navbar = document.querySelector('.navbar-links');
        if (navbar) {
            navbar.appendChild(switcher);
        } else {
            // Add to body if no navbar
            document.body.appendChild(switcher);
        }
    }
    
    // Add language switcher styles
    addLanguageSwitcherStyles() {
        if (document.getElementById('language-switcher-styles')) {
            return;
        }
        
        const style = document.createElement('style');
        style.id = 'language-switcher-styles';
        style.textContent = `
            .language-switcher {
                display: flex;
                align-items: center;
                margin-left: 10px;
            }
            
            .language-switcher-container {
                display: flex;
                gap: 5px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 2px;
            }
            
            .language-btn {
                background: transparent;
                border: none;
                color: white;
                padding: 8px 12px;
                border-radius: 18px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 0.9em;
                font-weight: 500;
            }
            
            .language-btn:hover {
                background: rgba(255,255,255,0.2);
            }
            
            .language-btn.active {
                background: rgba(255,255,255,0.3);
                font-weight: 600;
            }
            
            .language-btn .flag {
                font-size: 1.1em;
            }
            
            .language-btn .lang-text {
                display: none;
            }
            
            @media (min-width: 768px) {
                .language-btn .lang-text {
                    display: inline;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Update language switcher UI
    updateLanguageSwitcher() {
        const buttons = document.querySelectorAll('.language-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.onclick.toString().includes(this.currentLanguage)) {
                btn.classList.add('active');
            }
        });
    }
    
    // Translate page content
    translatePageContent() {
        // Translate common elements with data attributes
        this.translateElementsWithDataAttr();
        
        // Translate page-specific content
        this.translatePageSpecific();
    }
    
    // Translate elements with data-translate attribute
    translateElementsWithDataAttr() {
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.getText(key);
            if (translation && translation !== key) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            }
        });
    }
    
    // Translate specific element
    translateElement(elementId, translationKey) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = this.getText(translationKey);
        }
    }
    
    // Translate page-specific content
    translatePageSpecific() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        switch (currentPage) {
            case 'index.html':
                this.translateHomePage();
                break;
            case 'login.html':
                this.translateLoginPage();
                break;
            case 'signup.html':
                this.translateSignupPage();
                break;
            case 'vendor-dashboard.html':
                this.translateVendorDashboard();
                break;
            case 'cart.html':
                this.translateCartPage();
                break;
            case 'checkout.html':
                this.translateCheckoutPage();
                break;
            case 'profile.html':
                this.translateProfilePage();
                break;
        }
    }
    
    // Translate home page
    translateHomePage() {
        const welcomeTitle = document.querySelector('.hero h1');
        if (welcomeTitle) {
            welcomeTitle.textContent = this.getText('welcome_message');
        }
        
        const getStartedBtn = document.querySelector('.cta-btn');
        if (getStartedBtn) {
            getStartedBtn.textContent = this.getText('get_started');
        }
    }
    
    // Translate login page
    translateLoginPage() {
        const loginTitle = document.querySelector('.login-container h2');
        if (loginTitle) {
            loginTitle.textContent = this.getText('login');
        }
        
        const usernameInput = document.getElementById('login-username');
        if (usernameInput) {
            usernameInput.placeholder = this.currentLanguage === 'hi' ? 'फोन या ईमेल' : 'Phone or Email';
        }
        
        const passwordInput = document.getElementById('login-password');
        if (passwordInput) {
            passwordInput.placeholder = this.getText('password');
        }
        
        const loginBtn = document.querySelector('.login-container button[type="submit"]');
        if (loginBtn) {
            loginBtn.textContent = this.getText('login');
        }
    }
    
    // Translate signup page
    translateSignupPage() {
        const signupTitle = document.querySelector('.signup-container h2');
        if (signupTitle) {
            signupTitle.textContent = this.getText('signup');
        }
        
        const vendorBtn = document.getElementById('vendorBtn');
        if (vendorBtn) {
            vendorBtn.textContent = this.currentLanguage === 'hi' ? 'वेंडर' : 'Vendor';
        }
        
        const supplierBtn = document.getElementById('supplierBtn');
        if (supplierBtn) {
            supplierBtn.textContent = this.currentLanguage === 'hi' ? 'आपूर्तिकर्ता' : 'Supplier';
        }
    }
    
    // Translate vendor dashboard
    translateVendorDashboard() {
        const dashboardTitle = document.querySelector('.sidebar-header h3');
        if (dashboardTitle) {
            dashboardTitle.textContent = this.currentLanguage === 'hi' ? 'वेंडर डैशबोर्ड' : 'Vendor Dashboard';
        }
        
        const welcomeText = document.querySelector('.sidebar-header p');
        if (welcomeText) {
            welcomeText.textContent = this.currentLanguage === 'hi' ? 'वापसी पर स्वागत है' : 'Welcome back';
        }
    }
    
    // Translate cart page
    translateCartPage() {
        const cartTitle = document.querySelector('.page-title');
        if (cartTitle) {
            cartTitle.textContent = this.getText('shopping_cart');
        }
        
        const emptyCartTitle = document.querySelector('.empty-cart h2');
        if (emptyCartTitle) {
            emptyCartTitle.textContent = this.getText('empty_cart');
        }
    }
    
    // Translate checkout page
    translateCheckoutPage() {
        const checkoutTitle = document.querySelector('.page-title');
        if (checkoutTitle) {
            checkoutTitle.textContent = this.getText('checkout');
        }
        
        const orderSummaryTitle = document.querySelector('.summary-title');
        if (orderSummaryTitle) {
            orderSummaryTitle.textContent = this.getText('order_summary');
        }
    }
    
    // Translate profile page
    translateProfilePage() {
        const profileTitle = document.querySelector('.profile-title');
        if (profileTitle) {
            profileTitle.textContent = this.currentLanguage === 'hi' ? 'आपकी प्रोफाइल' : 'Your Profile';
        }
        
        const editBtn = document.getElementById('edit-btn');
        if (editBtn) {
            editBtn.textContent = this.getText('edit');
        }
        
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.textContent = this.getText('save');
        }
    }
}

// Initialize language switcher
let languageSwitcher;
document.addEventListener('DOMContentLoaded', function() {
    languageSwitcher = new LanguageSwitcher();
}); 