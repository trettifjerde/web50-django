const fadeDuration = 400;
const timerDelay = 7000;

let currentProjectI;
let currentProject;
let currentImg;
let timerId = null;
let projectLocked = false;

$(function(){
    if ($('main')[0])
    {
        setCurrentProject(0);
        showCurrentProject();
        toggleSidebar();

        timerId = setInterval(toggleGallery, timerDelay);

        $('.sidebar li').each(function(i) {
            $(this).on("mouseenter", () => showProject(i));
            $(this).on("click", () => lockProject(i));
        });

        $(".project").each(function(i) {
            $(this).on("click", () => toggleMobileDescription(i));
        });
    }
});

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

function loadLazy(imgDiv) {
    if (imgDiv && $(imgDiv).hasClass('lazy')) {
        $(imgDiv).find('img').each((_, img) => {img.src = img.dataset.src});
        $(imgDiv).removeClass('lazy');
    }
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

function showProject(i) {
    if (!projectLocked && i !== currentProjectI) 
        toggleProjects(i);
}

function lockProject(i){
    const li = $(`.sidebar li:eq(${i})`);

    if (! li.hasClass('locked')) {
        unlockProject();
        showProject(i);
        li.addClass('locked');
        projectLocked = true;

        $(document).one("click", unlockProject);
        event.stopPropagation();
    }
}

function unlockProject() {
    $('.locked').removeClass('locked');
    projectLocked = false;
}

function toggleMobileDescription(i) {
    if (window.innerHeight > window.innerWidth) {
        event.stopPropagation();
        if (!projectLocked) lockProject(i);
        currentProject.querySelector('.project-description').classList.toggle('visible');
    }
}