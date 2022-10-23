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

function showErrorMsg(msg, form) {
    const errorMsg = form ? form.querySelector('.error-msg') : document.querySelector('.error-msg.main');
    errorMsg.scrollIntoView({behavior: 'smooth'});
    errorMsg.innerHTML = msg;
    errorMsg.classList.add('grow');
    errorMsg.addEventListener('animationend', () => errorMsg.classList.remove('grow'), {once: true});
}

function showFormErrors(form, errors) {
    let errorMsg = '';
    for (let key in errors) {
        form[key].style.borderColor = 'red';
        errorMsg += errors[key];
    }
    showErrorMsg(errorMsg, form);
}

function togglePostForm(toShow, toHide) {

    toHide.classList.add('hide');
    toHide.addEventListener('animationend', () => {

        toHide.style.display = 'none';
        if (toHide.className.includes('post-form'))
            toHide.innerHTML = '';
        toHide.classList.remove('hide');

        toShow.style.display = '';
        toShow.classList.add('show');
        toShow.addEventListener('animationend', () => toShow.classList.remove('show'), {once: true});

    }, {once: true});
}

function post(){
    event.preventDefault();
    const form = event.target;

    fetch('/network/new/', {
        method: 'POST',
        headers: getAjaxHeaders(),
        body: JSON.stringify({text: form.text.value})
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) showErrorMsg(data.error, form)
        else if ('post' in data) showPost(data.post)
        else throw new Error(data)
    })
    .catch(err => console.log(err));
}

function showPost(postHTML) 
{
    document.querySelector('#newpostta').value = '';
    document.querySelector('.feed h2').insertAdjacentHTML('afterend', postHTML);
    const newPost = document.querySelector('.feed .post');
    newPost.classList.add('show-slide');
    newPost.addEventListener('animationend', () => newPost.classList.remove('show-slide'), {once: true});
}

function updatePost(form, text, postId, post, event) {
    event.preventDefault();
    if (form.text.value === text)
    {
        showErrorMsg("You haven't changed anything", form);
        form.text.focus();
    }
    else 
    {
        fetch('/network/editPost/', {
            method: 'POST',
            headers: getAjaxHeaders(),
            body: JSON.stringify({postId: postId, text: form.text.value})
        })
        .then(res => res.json())
        .then(data => {
            if ('post' in data) showPostChanges(post, form, data.post);
            else if ('error' in data) showErrorMsg(data.error, form);
            else if ('errors' in data) showFormErrors(form, data.errors);
            else throw new Error(data);
        })
        .catch(err => console.log(err));
    }
}

function deletePost(postId) {
    const btn = event.target;
    btn.disabled = true;

    fetch('/network/deletePost/', {
        method: 'POST',
        headers: getAjaxHeaders(),
        body: JSON.stringify({postId: postId})
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;

        if ('error' in data) showErrorMsg(data.error);
        else if ('ok' in data) {
            const post = btn.closest('.post');
            post.classList.add('hide-slide');
            post.addEventListener('animationend', () => {
                post.remove();
            }, {once: true});
        }
        else throw new Error(data);
    })
    .catch(err => console.log(err));
}

function showPostChanges(post, form, data) {
    const edited = post.querySelector('.last-edited');
    edited.innerHTML = data.edited;
    edited.parentElement.classList.remove('hidden');
    post.querySelector('.post-body').innerHTML = data.text;
    
    togglePostForm(post, form);
}

function showEditPost(text, postId) {
    const div = document.querySelector(`#post_edit_${postId}`);
    const post = div.previousElementSibling;
    const form = document.createElement('form');

    const errorP = document.createElement('p');
    errorP.className = 'error-msg';
    form.append(errorP);

    const textarea = document.createElement('textarea');
    textarea.name = 'text';
    textarea.required = true;
    textarea.value = text;
    form.append(textarea);

    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.innerHTML = 'Save';
    form.append(submitBtn);

    const cancelBtn = document.createElement('button');
    cancelBtn.type = "button";
    cancelBtn.innerHTML = "Cancel";
    cancelBtn.onclick = () => togglePostForm(post, div);
    form.append(cancelBtn); 

    form.onsubmit = (event) => updatePost(form, text, postId, post, event);

    div.append(form);
    togglePostForm(div, post);
}

function getEditPost(postId) {
    fetch(`/network/getPost/?postId=${postId}`, {
        headers: {'X-Requested-With': 'XMLHttpRequest'},
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) showErrorMsg(data.error)
        else if ('text' in data) showEditPost(data.text, postId);
        else throw new Error(data);
    })
    .catch(err => console.log(err));    
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

function like(postId, btn) {
    const heart = btn.querySelector('.heart');
    fetch('/network/like/', {
        method: 'PUT',
        headers: getAjaxHeaders(),
        body: JSON.stringify({post_id: postId})
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) showErrorMsg(data.error)
        else if ('likes' in data) {
            btn.querySelector('.num-likes').innerHTML = data.likes;
            if (heart.className.includes('liked')) 
            {
                heart.classList.add('shrink');
                heart.addEventListener('animationend', () => heart.className = 'heart', {once: true});
            }
            else {
                heart.className = 'heart liked grow';
                heart.addEventListener('animationend', () => heart.classList.remove('grow'), {once: true});
            }
        }
        else throw new Error(data)
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