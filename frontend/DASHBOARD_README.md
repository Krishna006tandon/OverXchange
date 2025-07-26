# Supply Dashboard

A modern, responsive supply management dashboard with light/dark mode toggle and comprehensive stock management features.

## Features

### 🌟 Core Features
- **Side Menu Bar**: Easy navigation between different sections
- **Stocks Management**: Complete stock tracking and management
- **Light/Dark Mode**: Toggle between light and dark themes with sun/moon icon
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

### 📊 Dashboard Sections
1. **Dashboard**: Overview with key statistics and recent stock updates
2. **Stocks**: Detailed stock management with search and filtering
3. **Orders**: Order management (placeholder for future implementation)
4. **Suppliers**: Supplier management (placeholder for future implementation)
5. **Analytics**: Data analytics and reporting (placeholder for future implementation)
6. **Settings**: System settings (placeholder for future implementation)

### 🎨 Theme Features
- **Light Mode**: Clean, bright interface for daytime use
- **Dark Mode**: Easy on the eyes for nighttime use
- **Persistent Theme**: Your theme preference is saved and remembered
- **Smooth Transitions**: Beautiful animations when switching themes

### 📱 Responsive Design
- **Desktop**: Full sidebar with text labels
- **Tablet**: Collapsible sidebar
- **Mobile**: Icon-only sidebar for maximum space efficiency

## How to Use

### Opening the Dashboard
1. Open `supply-dashboard.html` in your web browser
2. The dashboard will load with the default light theme

### Switching Themes
1. Look for the sun/moon icon in the top-right corner of the sidebar
2. Click the icon to toggle between light and dark mode
3. Your preference will be automatically saved

### Navigating the Dashboard
1. Use the sidebar menu to navigate between different sections
2. Click on "Stocks" to access the stock management page
3. Use the search functionality to find specific items
4. Click edit/delete buttons to manage individual stock items

### Stock Management
- **View All Stocks**: See complete inventory with status indicators
- **Search Stocks**: Use the search bar to find specific products
- **Add New Stock**: Click "Add New Stock" button (placeholder functionality)
- **Edit Stock**: Click the edit icon next to any stock item
- **Delete Stock**: Click the delete icon and confirm deletion

## File Structure

```
frontend/
├── supply-dashboard.html    # Main dashboard file
├── dashboard-styles.css     # Additional styling
├── dashboard.js            # JavaScript functionality
└── DASHBOARD_README.md     # This file
```

## Technical Details

### Technologies Used
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables for theming
- **JavaScript**: Interactive functionality and theme management
- **Font Awesome**: Icons for better user experience

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

### Theme System
The dashboard uses CSS custom properties (variables) for theming:
- Light theme: Clean whites and blues
- Dark theme: Dark grays and blues
- Smooth transitions between themes
- Local storage for theme persistence

## Future Enhancements

### Planned Features
- [ ] Real-time stock updates
- [ ] Advanced analytics and charts
- [ ] User authentication system
- [ ] Export functionality (PDF, Excel)
- [ ] Email notifications for low stock
- [ ] Barcode scanning integration
- [ ] Multi-language support

### API Integration
- [ ] Backend API for data persistence
- [ ] Real-time notifications
- [ ] User management
- [ ] Advanced reporting

## Customization

### Adding New Menu Items
1. Add a new `<li>` element to the `.nav-menu` in the HTML
2. Create a corresponding page content div
3. Update the JavaScript navigation logic

### Modifying Colors
1. Edit the CSS variables in the `:root` and `[data-theme="dark"]` selectors
2. Colors are defined using CSS custom properties for easy theming

### Adding New Features
1. Extend the `SupplyDashboard` class in `dashboard.js`
2. Add new event listeners and functionality
3. Update the HTML structure as needed

## Support

For any issues or questions about the dashboard:
1. Check the browser console for JavaScript errors
2. Ensure all files are in the same directory
3. Verify that your browser supports modern CSS and JavaScript features

## License

This dashboard is created for educational and demonstration purposes. Feel free to modify and use it in your projects. 