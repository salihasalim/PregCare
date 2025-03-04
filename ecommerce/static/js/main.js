// main.js

// Ensure the DOM is fully loaded before running scripts
document.addEventListener("DOMContentLoaded", function () {
    // Initialize Bootstrap dropdowns
    var dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            var dropdownMenu = this.nextElementSibling;
            dropdownMenu.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.matches('.dropdown-toggle')) {
            var dropdownMenus = document.querySelectorAll('.dropdown-menu');
            dropdownMenus.forEach(function (menu) {
                if (menu.classList.contains('show')) {
                    menu.classList.remove('show');
                }
            });
        }
    });

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.add('fade');
            alert.classList.remove('show');
            setTimeout(function () {
                alert.remove();
            }, 150); // Wait for fade-out animation to complete
        }, 5000); // 5 seconds
    });

    // Update cart badge dynamically
    function updateCartBadge(count) {
        var cartBadge = document.querySelector('.navbar .badge');
        if (cartBadge) {
            cartBadge.textContent = count;
        }
    }

    // Example: Simulate adding an item to the cart
    var addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            var productId = this.dataset.productId;
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF token is included
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quantity: 1 }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCartBadge(data.cart_total_items);
                        alert('Item added to cart!');
                    } else {
                        alert('Failed to add item to cart.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Basic form validation for search form
    var searchForm = document.querySelector('.navbar form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            var searchInput = this.querySelector('input[name="search"]');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                alert('Please enter a search term.');
            }
        });
    }
});