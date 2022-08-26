function redirect(url) {
    if (url)
        window.location.href = url;
    else
        location.reload(true);
}
function postAjax(url, data) {
    if (token)
    {
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
                redirect(data["redirect"]);
            else
                console.log(data["msg"]);
        });
    }
}
function deleteComment(url, listingId, commentId) {
    event.target.disabled = true;
    postAjax(url, {'listingId': listingId, 'commentId': commentId});
}

function sendListing(url, listingId) {
    postAjax(url, {'listingId': listingId}, event.target);
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
        'show', 'hide'
    )
    return false;
}

