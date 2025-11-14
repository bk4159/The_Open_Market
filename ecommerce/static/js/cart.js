document.addEventListener('DOMContentLoaded', () => {
    const updateBtnsHTMLCollection = document.getElementsByClassName('update-cart');
    const updateBtns = Array.from(updateBtnsHTMLCollection);

    updateBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const button = e.currentTarget;
            const productId = button.dataset.productid;
            const action = button.dataset.action;
            
            if (user === 'AnonymousUser') {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }
        });
    });

    // Function to update user order via API call
    function updateUserOrder(productId, action) {
        const url = '/update_item/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({'productId': productId, 'action': action})
        }).then((response) => {
            return response.json();
        }).then((data) => {
            location.reload();
        });
    }

    // Function to handle cart updates for anonymous users using cookies
    // TODO: Refactor this to use REST API
    function addCookieItem(productId, action) {
        if (action == 'add') {
            if (cart[productId] == undefined) {
                cart[productId] = {'quantity' : 1};
            } else {
                cart[productId]['quantity'] += 1;
            }
        } else if (action == 'remove') {
            cart[productId]['quantity'] -= 1;

            if (cart[productId]['quantity'] <= 0) {
                delete cart[productId];
            }
        }
        document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
        location.reload();
    }
});
