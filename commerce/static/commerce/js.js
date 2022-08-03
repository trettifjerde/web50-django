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
        .then(res => {return res.json()})
        .then(data => {
            if ("redirect" in data)
                redirect(data["redirect"]);
            else
                console.log(data["msg"]);
        });
    }
}
function deleteComment(url, listingId, commentId) {
    postAjax(url, {'listingId': listingId, 'commentId': commentId});
}

function sendListing(url, listingId) {
    postAjax(url, {'listingId': listingId})
}