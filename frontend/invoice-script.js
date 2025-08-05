// Invoice functionality
let isEditing = false;

// Calculate total amount
function calculateTotal() {
    const rows = document.querySelectorAll('#invoice-items tr');
    let total = 0;
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            const priceText = cells[2].textContent.replace(/[^0-9.-]+/g, '');
            const price = parseFloat(priceText);
            const qtyText = cells[1].textContent;
            // Extract quantity number from text like "2 kg" or "3 packets"
            const qtyMatch = qtyText.match(/(\d+(?:\.\d+)?)/);
            const qty = qtyMatch ? parseFloat(qtyMatch[1]) : 1;
            const amount = price * qty;
            cells[3].textContent = '₹' + amount.toFixed(2);
            total += amount;
        }
    });
    
    document.getElementById('total-amount').textContent = '₹' + total.toFixed(2);
    return total;
}

// Download PDF functionality
function downloadPDF() {
    // Create a new window with the invoice content
    const printWindow = window.open('', '_blank');
    const invoiceContent = document.querySelector('.invoice-box').innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice PDF</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .invoice-box { max-width: 800px; margin: auto; }
                header { display: flex; justify-content: space-between; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }
                .logo { font-weight: bold; font-size: 24px; }
                .address-section { display: flex; justify-content: space-between; margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background: #f5f5f5; padding: 12px; text-align: left; font-weight: bold; }
                td { padding: 12px; border-bottom: 1px solid #eee; }
                .summary { margin-top: 20px; text-align: right; font-size: 16px; border-top: 2px solid #eee; padding-top: 20px; }
                .buttons { display: none; }
            </style>
        </head>
        <body>
            <div class="invoice-box">
                ${invoiceContent}
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}

// Edit invoice functionality
function editInvoice() {
    if (isEditing) {
        // Save changes
        saveInvoice();
        return;
    }
    
    isEditing = true;
    document.querySelector('.edit-btn').textContent = 'Save Changes';
    
    // Make fields editable
    makeEditable('invoice-number');
    makeEditable('invoice-date');
    makeEditable('from-name');
    makeEditable('from-address');
    makeEditable('from-email');
    makeEditable('to-name');
    makeEditable('to-address');
    makeEditable('to-email');
    makeEditable('payment-method');
    
    // Make table editable
    const rows = document.querySelectorAll('#invoice-items tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach((cell, index) => {
            if (index < 3) { // Don't make amount column editable
                const currentText = cell.textContent;
                cell.innerHTML = `<input type="text" value="${currentText}" style="width: 100%; border: none; background: transparent;">`;
            }
        });
    });
    
    // Add new row button
    const tbody = document.getElementById('invoice-items');
    const addRowBtn = document.createElement('tr');
    addRowBtn.innerHTML = `
        <td colspan="4" style="text-align: center; padding: 10px;">
            <button onclick="addNewRow()" style="background: #4CAF50; color: white; border: none; padding: 8px 16px; cursor: pointer; border-radius: 4px;">
                + Add New Item
            </button>
        </td>
    `;
    tbody.appendChild(addRowBtn);
}

// Make element editable
function makeEditable(elementId) {
    const element = document.getElementById(elementId);
    const currentText = element.textContent;
    element.innerHTML = `<input type="text" value="${currentText}" style="width: 100%; border: 1px solid #ddd; padding: 4px; border-radius: 4px;">`;
}

// Add new row to table
function addNewRow() {
    const tbody = document.getElementById('invoice-items');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>
            <input type="text" value="New Product" style="width: 100%; border: none; background: transparent;">
            <br><small style="color: #666; font-size: 12px;">
                <i class="fas fa-tag"></i> Category <i class="fas fa-copyright"></i> Brand 
                <i class="fas fa-info-circle"></i> Product description...
            </small>
        </td>
        <td><input type="text" value="1 kg" style="width: 100%; border: none; background: transparent;"></td>
        <td><input type="text" value="₹0" style="width: 100%; border: none; background: transparent;"></td>
        <td>₹0.00</td>
    `;
    
    // Insert before the add row button
    const addRowBtn = tbody.querySelector('tr:last-child');
    tbody.insertBefore(newRow, addRowBtn);
}

// Save invoice changes
function saveInvoice() {
    isEditing = false;
    document.querySelector('.edit-btn').textContent = 'Edit Invoice';
    
    // Save text fields
    saveEditableField('invoice-number');
    saveEditableField('invoice-date');
    saveEditableField('from-name');
    saveEditableField('from-address');
    saveEditableField('from-email');
    saveEditableField('to-name');
    saveEditableField('to-address');
    saveEditableField('to-email');
    saveEditableField('payment-method');
    
    // Save table data
    const rows = document.querySelectorAll('#invoice-items tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            cells.forEach((cell, index) => {
                const input = cell.querySelector('input');
                if (input) {
                    cell.textContent = input.value;
                }
            });
        }
    });
    
    // Remove add row button
    const addRowBtn = document.querySelector('#invoice-items tr:last-child');
    if (addRowBtn && addRowBtn.querySelector('button')) {
        addRowBtn.remove();
    }
    
    // Recalculate total
    calculateTotal();
}

// Save editable field
function saveEditableField(elementId) {
    const element = document.getElementById(elementId);
    const input = element.querySelector('input');
    if (input) {
        element.textContent = input.value;
    }
}

// Auto-calculate total when page loads
document.addEventListener('DOMContentLoaded', function() {
    calculateTotal();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            if (isEditing) {
                saveInvoice();
            }
        }
    });
});

// Auto-save functionality
let autoSaveTimer;
function setupAutoSave() {
    if (isEditing) {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(() => {
            if (isEditing) {
                calculateTotal();
            }
        }, 1000);
    }
}

// Add event listeners for auto-save
document.addEventListener('input', setupAutoSave); 