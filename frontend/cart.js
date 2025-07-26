function renderCart() {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    let cartItemsHTML = '';
    let total = 0;

    if (cart.length === 0) {
        document.getElementById('cartItems').innerHTML = '<p class="empty">Your cart is empty</p>';
        document.getElementById('totalAmount').innerText = '0';
        return;
    }

    cart.forEach((item, index) => {
        cartItemsHTML += `
            <li>
                <span>${item.name}</span> 
                <span>₹${item.price}</span>
                <button class="remove-btn" onclick="removeItem(${index})">Remove</button>
            </li>`;
        total += item.price;
    });

    document.getElementById('cartItems').innerHTML = cartItemsHTML;
    document.getElementById('totalAmount').innerText = total;
}

function removeItem(index) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
}

function clearCart() {
    localStorage.removeItem('cart');
    renderCart();
}

function makePayment() {
    let total = document.getElementById('totalAmount').innerText;
    if (total === '0') {
        alert("Your cart is empty, please add items before paying.");
    } else {
        showPopup();
        localStorage.removeItem('cart');
        renderCart();
    }
}

function showPopup() {
    let popup = document.getElementById('paymentPopup');
    popup.style.display = 'block';
    setTimeout(() => popup.style.display = 'none', 2000);
}

renderCart();
