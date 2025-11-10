// Authentication Check
(function() {
    const userType = localStorage.getItem('user_type');
    const userId = localStorage.getItem('user_id');
    if (!userType || !userId || userType !== 'supplier') {
        alert('Access denied. Only suppliers can access this dashboard.');
        window.location.href = 'login.html';
    }
})();

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const body = document.body;
const currentTheme = localStorage.getItem('theme') || 'light';
body.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const newTheme = body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Navigation
const navLinks = document.querySelectorAll('.nav-link');
const pageContents = document.querySelectorAll('.page-content');

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        pageContents.forEach(content => content.style.display = 'none');
        
        const targetPage = link.getAttribute('data-page');
        document.getElementById(targetPage + '-page').style.display = 'block';
        
        // Load data for the specific page
        if (targetPage === 'stocks') loadStocks();
        if (targetPage === 'orders') loadSupplierOrders();
        // Add other page load functions here
    });
});

// Stock Management
let currentStocks = [];
let editingStockId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    document.getElementById('categoryFilter').addEventListener('change', filterStocks);
    document.getElementById('stockForm').addEventListener('submit', handleStockFormSubmit);
});

function loadDashboardData() {
    const userId = localStorage.getItem('user_id');
    fetch(`/api/dashboard/${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentStocks = data.recent_stocks; // Assuming dashboard returns recent stocks
                updateDashboardStats(data.analytics);
                displayDashboardStocks(data.recent_stocks);
            }
        });
}

function loadStocks() {
    const userId = localStorage.getItem('user_id');
    fetch(`/api/stocks/supplier/${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentStocks = data.stocks;
                displayStocks(currentStocks);
            }
        });
}

function displayStocks(stocks) {
    const tbody = document.getElementById('stocksTableBody');
    const noStocksMessage = document.getElementById('noStocksMessage');
    tbody.innerHTML = '';

    if (stocks.length === 0) {
        noStocksMessage.style.display = 'block';
        return;
    }
    noStocksMessage.style.display = 'none';

    stocks.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stock.product_name}</td>
            <td>${stock.category}</td>
            <td>${stock.quantity_available} ${stock.unit}</td>
            <td>₹${stock.price_per_unit}</td>
            <td><span class="stock-status ${getStockStatusClass(stock.quantity_available)}">${getStockStatus(stock.quantity_available)}</span></td>
            <td>
                <button class="btn-3d" onclick="openStockModal('${stock._id}')">Edit</button>
                <button class="btn-3d btn-pink" onclick="deleteStock('${stock._id}')">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function displayDashboardStocks(stocks) {
    const tbody = document.getElementById('dashboardStocksTableBody');
    tbody.innerHTML = '';
    if (stocks.length === 0) {
        document.getElementById('dashboardNoStocksMessage').style.display = 'block';
        return;
    }
    document.getElementById('dashboardNoStocksMessage').style.display = 'none';

    stocks.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stock.product_name}</td>
            <td>${stock.category}</td>
            <td>${stock.quantity_available}</td>
            <td><span class="stock-status ${getStockStatusClass(stock.quantity_available)}">${getStockStatus(stock.quantity_available)}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function updateDashboardStats(analytics) {
    document.getElementById('totalProducts').textContent = analytics?.total_products || 0;
    document.getElementById('lowStockItems').textContent = analytics?.low_stock_items || 0;
    document.getElementById('outOfStockItems').textContent = analytics?.out_of_stock_items || 0;
    document.getElementById('totalValue').textContent = `₹${(analytics?.total_value || 0).toLocaleString()}`;
}

function filterStocks() {
    const category = document.getElementById('categoryFilter').value;
    const filtered = category ? currentStocks.filter(s => s.category === category) : currentStocks;
    displayStocks(filtered);
}

function getStockStatus(quantity) {
    if (quantity === 0) return 'Out of Stock';
    if (quantity <= 10) return 'Low Stock';
    return 'In Stock';
}

function getStockStatusClass(quantity) {
    if (quantity === 0) return 'status-out-of-stock';
    if (quantity <= 10) return 'status-low-stock';
    return 'status-in-stock';
}

function openStockModal(stockId = null) {
    editingStockId = stockId;
    const modal = document.getElementById('stockModal');
    const form = document.getElementById('stockForm');
    form.reset();

    if (stockId) {
        document.getElementById('modalTitle').textContent = 'Edit Stock';
        const stock = currentStocks.find(s => s._id === stockId);
        if (stock) {
            // Populate form
            for (const key in stock) {
                if (form.elements[key]) {
                    form.elements[key].value = stock[key];
                }
            }
        }
    } else {
        document.getElementById('modalTitle').textContent = 'Add New Stock';
    }
    modal.style.display = 'block';
}

function closeStockModal() {
    document.getElementById('stockModal').style.display = 'none';
}

async function handleStockFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const stockData = Object.fromEntries(formData.entries());
    stockData.supplier_id = localStorage.getItem('user_id');

    const url = editingStockId ? `/api/stocks/${editingStockId}` : '/api/stocks';
    const method = editingStockId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(stockData)
        });
        const result = await response.json();
        if (result.success) {
            closeStockModal();
            loadStocks();
            loadDashboardData();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('An error occurred.');
    }
}

async function deleteStock(stockId) {
    if (!confirm('Are you sure you want to delete this stock item?')) return;
    try {
        const response = await fetch(`/api/stocks/${stockId}`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) {
            loadStocks();
            loadDashboardData();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('An error occurred.');
    }
}

// Orders
function loadSupplierOrders() {
    // Implementation for loading orders
}

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.clear();
    window.location.href = 'login.html';
});

window.onclick = function(event) {
    if (event.target == document.getElementById('stockModal')) {
        closeStockModal();
    }
};
