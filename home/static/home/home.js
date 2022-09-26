const fadeDuration = 400;
const timerDelay = 7000;

let currentProjectI;
let currentProject;
let currentImgI;
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
            $(this).parent().on("touchstart", (event) => {
                event.preventDefault();
                showProject(i);
            });
        });

        $(".project").each(function(i) {
            $(this).on("click", () => toggleMobileDescription(i));
            $(this).find('.project-img-btns button').each(function(j) {
                $(this).on("click", ()=> showImg(j));
            });
        });
    }
});

function toggleGallery() {
    let nextImgI;
    if (! currentImg.nextElementSibling)
    {
        if (!projectLocked) {
            toggleProjects();
            return;
        }
        else
            nextImgI = 0;
    }
    else
        nextImgI = currentImgI + 1;

    toggleImgs(nextImgI);
}

function setCurrentProject(i) {
    if (i !== null)
        currentProjectI = i;
    else if (currentProject.nextElementSibling) 
        currentProjectI++;
    else
        currentProjectI = 0;

    currentProject = $(`.project:eq(${currentProjectI})`)[0];
    setCurrentImg(0);
}

function setCurrentImg(i) {

    currentImgI = i;
    currentImg = currentProject.querySelectorAll('.project-img')[i];
    loadLazy(currentImg);
    $(currentProject).find('.img-btn-active').removeClass('img-btn-active');
    currentProject.querySelectorAll('.project-img-btns button')[i].classList.add('img-btn-active');
}

function toggleImgs(i) {
    const previousImg = currentImg;
    setCurrentImg(i);
    $(previousImg).fadeOut(fadeDuration, ()=> $(currentImg).fadeIn(fadeDuration));
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

function showImg(i) {
    event.stopPropagation();
    if (i !== currentImgI) {
        toggleImgs(i);
        clearInterval(timerId);
        timerId = setInterval(toggleGallery, timerDelay);
    }
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
        const desc = currentProject.querySelector('.project-description');
        if (desc.classList.contains('visible'))
            desc.classList.remove('visible');
        else {
            desc.classList.add('visible');
            lockProject(i);
            event.stopPropagation();
        }
    }
    else if (!projectLocked) lockProject(i);
}