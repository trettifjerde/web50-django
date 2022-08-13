function login()
{
    window.location.href = '/login?next=' + location.pathname;
}
function logout() {
    if (token) 
        fetch('/logout/', { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': token, 
                    'X-Requested-With': 'XMLHttpRequest'
                }}
        )
        .then(res => {
            if (res.status === 200) location.reload(true);
            else throw `Got status ${res.status} on logout`;
            })
        .catch(err => console.log(err));
    return false;
}