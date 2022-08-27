function login(project)
{
    window.location.href = '/login?next=/' + project;
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