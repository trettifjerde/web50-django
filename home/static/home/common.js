function login()
{
    const pathname = window.location.pathname;
    if (pathname.startsWith('/login') || pathname.startsWith('/register'))
    {
        const params = new URLSearchParams(window.location.search);
        window.location.href = '/login?next=' + params.get('next')
    } 
    else
        window.location.href = '/login?next=' + window.location.pathname;
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
            else throw new Error();
            })
        .catch(err => location.reload(true));
    return false;
}

function register(project) {
    window.location.href = '/register?next=/' + project;
}