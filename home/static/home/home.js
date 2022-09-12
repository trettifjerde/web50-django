const fadeDuration = 400;
const timerDelay = 7000;

let currentProjectI;
let currentProject;
let currentImg;
let timerId = null;
let projectLocked = false;

$(function(){
    if (document.querySelector('main'))
    {
        setCurrentProject(0);
        showCurrentProject();
        toggleSidebar();

        timerId = setInterval(toggleGallery, timerDelay);

        $(".sidebar li").on("mouseenter", showProject);
        $(".sidebar li").on("click", lockProject);
        $(".project").on("click", toggleMobileDescription);
    }
});

function loadLazy(imgDiv) {
    if (imgDiv && imgDiv.classList.contains('lazy')) {
        imgDiv.querySelectorAll('img').forEach(img => img.src = img.dataset.src);
        imgDiv.classList.remove('lazy');
    }
}

function toggleGallery() {
    let nextImg = currentImg.nextElementSibling;
    if (! nextImg) {
        if (! projectLocked){
            toggleProjects();
            return;
        }
        else 
            nextImg = currentProject.querySelector('.project-img');
    }

    const previousImg = currentImg;
    setCurrentImg(nextImg);

    $(previousImg).fadeOut(fadeDuration, ()=> $(currentImg).fadeIn(fadeDuration));
}

function setCurrentProject(i) {
    if (i !== null)
        currentProjectI = i;
    else if (currentProject.nextElementSibling) 
        currentProjectI++;
    else
        currentProjectI = 0;

    currentProject = $(`.project:eq(${currentProjectI})`)[0];
    setCurrentImg(currentProject.querySelector('.project-img'));
}

function setCurrentImg(img) {
    currentImg = img;
    loadLazy(img);
}

function toggleProjects(i=null) {

    const previousProject = currentProject;
    const previousImg = currentImg;

    setCurrentProject(i);

    clearInterval(timerId);
    timerId = setInterval(toggleGallery, timerDelay);

    toggleSidebar();
    $(previousProject).fadeOut(fadeDuration, ()=> {
        $(previousImg).hide();
        showCurrentProject();
    });
}

function toggleSidebar() {
    $('.li-active').removeClass('li-active');
    $(`.sidebar li:eq(${currentProjectI})`).addClass('li-active');
}

function showCurrentProject() {
    $(currentImg).show();
    $(currentProject).fadeIn(fadeDuration);
}

function showProject() {
    const nextProjectI = $(".sidebar li").index(this);
    if (!projectLocked && nextProjectI !== currentProjectI)
    {
        toggleProjects(nextProjectI);
    }
}

function lockProject(){
    if (!$(this).hasClass('locked')) {
        console.log(event);
        event.stopPropagation();
        $('.locked').removeClass('locked');
        if (! $(this).hasClass('li-active')) {
            projectLocked = false;
            showProject.bind(this)();
        }
        $(this).addClass('locked');
        projectLocked = true;

        document.addEventListener("click", function() {
            console.log('lock removed');
            $('.locked').removeClass('locked');
            projectLocked = false;
        }, {once: true});
    }
    
}

function toggleMobileDescription() {
    if (window.innerHeight > window.innerWidth) {
        event.stopPropagation();
        if (!projectLocked)
            lockProject.bind($(".li-active")[0])();
        this.querySelector('.project-description').classList.toggle('mobile');

    }
}