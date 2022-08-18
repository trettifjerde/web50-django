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

        toShow.style.display = 'block';
        toShow.classList.add('show');
        toShow.addEventListener('animationend', () => toShow.classList.remove('show'), {once: true});
    }, {once: true});
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
        fetch('/network/edit/' + postId, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'text': form.text.value})
        })
        .then(res => res.json())
        .then(data => {
            if ('errors' in data) showFormErrors(form, data.errors);
            else if ('error' in data) throw new Error(data.error);
            else if ('post' in data) showPostChanges(post, form, data.post);
            else throw new Error(data);
        })
        .catch(err => showErrorMsg(err, form));
    }
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
    fetch(`/network/edit/${postId}`, {
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) throw new Error(data.error)
        else showEditPost(data.text, postId);
    })
    .catch(err => showErrorMsg(err));    
}

function follow(userId) {
    fetch(`/network/follow/${userId}`, {
        method: 'PUT',
        headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': token,
                'Content-Type': 'application/json'
        },
        body: JSON.stringify({'userId': userId})
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) throw new Error(data.error);
        else location.reload(true);
    })
    .catch(err => showErrorMsg(err));
}

function like(postId, btn) {
    const heart = btn.querySelector('.heart');
    fetch('/network/like/', {
        method: 'PUT',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'post_id': postId})
    })
    .then(res => res.json())
    .then(data => {
        if ('error' in data) throw new Error(data.error)
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
    .catch(err => showErrorMsg(err));
}