# 🧾 Professional Invoice System

A complete, fully functional invoice system with HTML, CSS, JavaScript, and optional Flask backend.

## 📁 File Structure

```
frontend/
├── invoice.html          # Main invoice page
├── invoice-style.css     # Styling
├── invoice-script.js     # JavaScript functionality
└── INVOICE_README.md     # This file

backend/
├── invoice_app.py        # Flask backend (optional)
└── invoice_requirements.txt
```

## 🚀 Quick Start

### Frontend Only (Recommended)
1. **Open** `frontend/invoice.html` in your browser
2. **Start editing** - Click "Edit Invoice" button
3. **Print** - Use "Print Invoice" button
4. **Download** - Use "Download PDF" button

### With Flask Backend
1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r invoice_requirements.txt
   ```

2. **Run the server:**
   ```bash
   python invoice_app.py
   ```

3. **Open:** `http://localhost:5001`

## ✨ Features

### 🎨 **Clean Design**
- Professional black and gray color scheme
- Responsive layout
- Print-friendly styling

### ✏️ **Editable Fields**
- Invoice number and date
- From/To addresses
- Item details (name, quantity, price)
- Payment method
- Auto-calculates totals

### 📄 **Export Options**
- **Print Invoice** - Opens print dialog
- **Download PDF** - Creates printable PDF
- **Save Changes** - Preserves edits

### ⌨️ **Keyboard Shortcuts**
- `Ctrl + P` - Print invoice
- `Ctrl + S` - Save changes (when editing)

## 🔧 Customization

### Change Company Details
Edit these fields in `invoice.html`:
```html
<div class="logo">YOUR LOGO</div>
<p id="from-name">Your Company Name</p>
<p id="from-address">Your Address</p>
<p id="from-email">your@email.com</p>
```

### Modify Styling
Edit `invoice-style.css`:
```css
.logo {
    font-size: 24px;
    color: #333;
}
```

### Add More Features
Extend `invoice-script.js`:
```javascript
function addNewFeature() {
    // Your custom functionality
}
```

## 📱 Responsive Design

The invoice works on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ Print media

## 🎯 Usage Examples

### Basic Invoice
1. Open `invoice.html`
2. Click "Edit Invoice"
3. Change client details
4. Add/modify items
5. Click "Save Changes"
6. Print or download

### Professional Invoice
1. Customize company details
2. Add your logo
3. Set up recurring clients
4. Use consistent numbering
5. Save templates

## 🔌 API Endpoints (Flask Backend)

### Generate Invoice
```bash
POST /api/generate-invoice
Content-Type: application/json

{
    "from_name": "Your Company",
    "to_name": "Client Name",
    "items": [
        {"name": "Service", "quantity": "1", "price": "100", "amount": "100"}
    ],
    "total": 100
}
```

### Save Invoice
```bash
POST /api/save-invoice
Content-Type: application/json

{
    "invoice_number": "INV-001",
    "from_name": "Your Company",
    "to_name": "Client Name",
    "items": [...],
    "total": 100
}
```

### List Invoices
```bash
GET /api/invoices
```

### Download Invoice
```bash
GET /download/<filename>
```

## 🛠️ Troubleshooting

### Print Issues
- Ensure print styles are enabled
- Check browser print settings
- Use "Download PDF" for better results

### Edit Mode Problems
- Click "Save Changes" before switching modes
- Refresh page if editing gets stuck
- Check browser console for errors

### Backend Issues
- Verify Flask is installed: `pip install Flask`
- Check port 5001 is available
- Review error logs in terminal

## 📋 Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile browsers

## 🎨 Design Features

### Color Scheme
- **Primary:** #333 (Dark Gray)
- **Secondary:** #666 (Medium Gray)
- **Background:** #f4f4f4 (Light Gray)
- **Accent:** #4CAF50 (Green for buttons)

### Typography
- **Font:** Arial, sans-serif
- **Headers:** Bold, 16-24px
- **Body:** Regular, 14px
- **Small:** 12px for details

## 🚀 Advanced Features

### Auto-Save
- Changes are automatically saved
- No data loss during editing
- Real-time total calculation

### Dynamic Items
- Add unlimited items
- Remove items easily
- Automatic amount calculation

### Professional Output
- Clean, business-ready design
- Print-optimized layout
- PDF-compatible formatting

## 📞 Support

For issues or questions:
1. Check browser console for errors
2. Verify all files are in correct locations
3. Test with different browsers
4. Review this README for solutions

---

**Ready to create professional invoices! 🎉** 