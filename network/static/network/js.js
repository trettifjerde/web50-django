document.addEventListener('scroll', () => {
    if (document.documentElement.scrollTop > window.innerHeight * 0.5) {
        document.querySelector('#scrollUpBtn').style.visibility = 'visible';
        document.querySelector('#scrollUpBtn').style.opacity = 1;
    }
    else {
        document.querySelector('#scrollUpBtn').style.visibility = 'hidden';
        document.querySelector('#scrollUpBtn').style.opacity = 0;
    }
});

function scrollUp() {
    window.scrollTo({top: 0, behavior: 'smooth'});
}

function getAjaxHeaders() {
    return {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': token,
        'Content-Type': 'application/json'
    };
}

function follow(userId) {
    const followBtn = event.target;
    followBtn.disabled = true;

    fetch(`/network/follow/`, {
        method: 'PUT',
        headers: getAjaxHeaders(),
        body: JSON.stringify({userId: userId})
    })
    .then(res => res.json())
    .then(data => {
        followBtn.disabled = false;

        if ('error' in data) showErrorMsg(data.error);
        else if ('text' in data) {
            followBtn.textContent = data.text;
            document.querySelector('#followersNumber').textContent = data.followers;
        }
        else throw new Error(`Error processing response: ${JSON.stringify(data)}`);
    })
    .catch(err => console.log(err));
}

function handleAvatarUpload(div) {
    const input = div.querySelector('input');
    const deleteBtn = div.nextElementSibling;
    if (input.value) {
        div.querySelector('label').style.display = 'none';
        div.querySelector('span').innerHTML = input.files[0].name;
        div.querySelectorAll('button').forEach(button => button.style.display = 'inline-block');
        if (deleteBtn) deleteBtn.style.display = 'none';
    }
    else {
        div.querySelector('label').style.display = '';
        if (deleteBtn) deleteBtn.style.display = '';
        div.querySelector('span').innerHTML = '';
        div.querySelectorAll('button').forEach(button => button.style.display = '');
    }
}

function cancelAvatarUpload(div) {
    div.querySelector('input').value = null;
    handleAvatarUpload(div);
}

function uploadAvatar(div) {
    const file = div.querySelector('input').files[0];
    fetch('/network/avatar/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('input[name=csrfmiddlewaretoken]').value
        },
        body: file 
    })
    .then(res => res.status === 200? location.reload() : console.log(res))
    .catch(err => console.log(err, 'from catch'));
}

function deleteAvatar() {
    fetch('/network/unload/', {
        method: 'PUT',
        headers: getAjaxHeaders(),
        body: JSON.stringify()
    })
    .then(res => res.status === 200 ? location.reload(true) : console.log(res))
    .catch(err => console.log(err));
}