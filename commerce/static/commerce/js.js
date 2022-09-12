document.addEventListener('scroll', () => {
    toggleNavBar();
});

function toggleNavBar() {
    const navBar = document.querySelector('nav');
    if (document.documentElement.scrollTop > 10) {
        navBar.classList.add("nav-sticky");
    }
    else {
        navBar.classList.remove("nav-sticky");
    }
}

function redirect(url) {
    if (url)
        window.location.href = url;
    else
        location.reload(true);
}
function postAjax(url, data, errorDiv=null) {
    if (token)
    {
        const btn = event.target;
        btn.disabled = true;
        data = JSON.stringify(data);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token, 
                'X-Requested-With': 'XMLHttpRequest'
            },
            mode: 'same-origin',
            body: data
        })
        .then(res => res.json())
        .then(data => {
            if ("redirect" in data)
                redirect(data.redirect);
            else if ("error" in data && errorDiv)
                errorDiv.innerHTML = data.error;
            else console.log(data);

            btn.disabled = false;
        })
        .catch(err => redirect(''));
    }
}

function placeBid(url, listingId) {
    const form = event.target.form;
    if (form.checkValidity()) {
        postAjax(
            url, 
            {pk: listingId, bid: form.bid.value}, 
            form.querySelector(".error-msg")
        );
    }
    else {
        form.querySelector('.error-msg').innerHTML = 'Enter a valid bid';
        form.bid.classList.add('invalid');
    };
}

function updateListing(url, listingId) {
    postAjax(url, {pk: listingId}, document.querySelector('.listing-info .error-msg'));
}

function toggleAnimation(el, toShow, changes, showClass, hideClass) {
    if (toShow) {
        for (let change of changes) {
            change();
        }
        el.classList.add(showClass);
        el.addEventListener('animationend', ()=> el.classList.remove(showClass), {once: true});
    }
    else {
        el.classList.add(hideClass);
        el.addEventListener('animationend', ()=> {
            el.classList.remove(hideClass);
            for (let change of changes) {
                change();
            }
        }, {once: true});
    }
}

function openMobileNav() {
    const navBar = document.querySelector('.nav-bar')

    toggleAnimation(
        navBar,
        navBar.classList.contains('nav-mobile-open') === false,
        [
            () => navBar.classList.toggle('nav-mobile-open'),
            () => document.querySelector('html').classList.toggle('locked')
        ],
        'show-slide', 'hide-slide'
    )
    return false;
}

