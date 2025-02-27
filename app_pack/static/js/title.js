
var videoContainer = document.getElementById('video');
var videoControls = document.getElementsByClassName('video-control');
var video = document.getElementById('myVideo');
var videoUrl = document.getElementsByClassName('mp4')[0];
var videoUrlDop = document.getElementsByClassName('mp4_720')[0];
var videoUrlFrame = document.getElementsByClassName('mp4_frame')[0];
var progressBar = document.getElementById('video-progress');
var nowTime = document.getElementById('video-time-now');
var allTime = document.getElementById('video-time-all');
var possibleTime = document.getElementsByClassName('video-time-change')[0];
var fullscreenBtn = document.getElementsByClassName('expand')[0];
var volumeChange = document.getElementsByClassName('volume-change')[0];
var volumeMax = document.getElementsByClassName('volume-max')[0];
var volumeNow = document.getElementsByClassName('volume-now')[0];
var muteButton = document.getElementsByClassName('volume-img')[0];
var muteButtonMain = document.getElementsByClassName('volume')[0];
var rewindFirst = document.getElementsByClassName('rewind-30')[0];
var rewindSecond = document.getElementsByClassName('rewind-60')[0];
var rewindThird = document.getElementsByClassName('rewind-90')[0];
var seasonsButton = document.getElementsByClassName('choice_season')[0];
var seasonsBox = document.getElementsByClassName('any_seasons')[0];
var seriesButton = document.getElementsByClassName('choice_seria')[0];
var previousSeria = document.getElementsByClassName('previous_seria')[0];
var nextSeria = document.getElementsByClassName('next_seria')[0];
var bottomLine = document.getElementsByClassName('bottom-line')[0];
var bottomLineSecond = document.getElementsByClassName('bottom-line-2')[0];
var genresBottom = document.getElementById('genres_bottom');
var genresBox = document.getElementsByClassName('genres_box')[0];
var addTitleButton = document.getElementsByClassName('to_add_in_my_list');
var isSent = false;


function videoAct() {
    if (video.paused) {
        video.play();
        for (let control of videoControls) {
            control.style.visibility = 'hidden';
        }
    } else {
        video.pause();
        for (let control of videoControls) {
            control.style.visibility = 'visible';
        }
    }
    if(allTime.innerHTML == '00:00' || allTime.innerHTML == 'NaN:NaN') {
        allTime.innerHTML = videoTime(video.duration);
    }
    };

videoControls[0].addEventListener('click', videoAct);
video.addEventListener('click', videoAct);

function keyVideoAct(key) {//Воспроизведение/пауза при нажатии пробела и перемотка видео стрелочками
    if (key.code == 'Space') {
        videoAct()
    }
    if (key.code == 'ArrowLeft') {
        if (video.currentTime > 15) {
            video.currentTime = video.currentTime - 15
        } else {
        video.currentTime = 0
        }
    }
    if (key.code == 'ArrowRight') {
        if (video.currentTime + 15 < video.duration) {
            video.currentTime = video.currentTime + 15
        } else {
        video.currentTime = video.duration
        }
    }
    }

document.addEventListener('keydown',keyVideoAct);

function videoTime(time) { //Рассчитываем время в секундах и минутах
    time = Math.floor(time);
    var minutes = Math.floor(time / 60);
    var seconds = Math.floor(time - minutes * 60);
    var minutesVal = minutes;
    var secondsVal = seconds;
    if(minutes < 10) {
    minutesVal = '0' + minutes;
    }
    if(seconds < 10) {
    secondsVal = '0' + seconds;
    }
    return minutesVal + ':' + secondsVal;
    }

function videoProgress() { //Отображаем время воспроизведения
    progress = (Math.floor(video.currentTime) / (Math.floor(video.duration) / 100));
    progressBar.value = progress;
    nowTime.innerHTML = videoTime(video.currentTime);
    if(allTime.innerHTML == '00:00' || allTime.innerHTML == 'NaN:NaN') {
        allTime.innerHTML = videoTime(video.duration);
    }
    if(video.currentTime == video.duration) {
        for (let control of videoControls) {
            control.style.visibility = 'visible';
        }
    }
    }

function videoChangeTime(e) { //Перематываем
    var mouseX = Math.floor(e.pageX - progressBar.getBoundingClientRect().left);
    var progress = mouseX / (progressBar.offsetWidth / 100);
    video.currentTime = video.duration * (progress / 100);
    }

function videoPossibleTime(e) { //Показываем время при наведении
    var mouseX = Math.floor(e.clientX - progressBar.getBoundingClientRect().left);
    var progress = mouseX / (progressBar.offsetWidth / 100);
    if (video.duration * (progress / 100) > 0) {
    possibleTime.innerHTML = videoTime(video.duration * (progress / 100));
    } else {
    possibleTime.innerHTML = '00:00'
    }
    possibleTime.style.visibility = 'visible';
    possibleTime.style.marginLeft = mouseX-possibleTime.offsetWidth/2+'px';
    }

function hiddenPossibleTime(e) { //Прячем время при отводе курсора
    possibleTime.style.visibility = 'hidden';
    }

//Отображение времени
video.addEventListener('timeupdate',videoProgress);
//Перемотка
progressBar.addEventListener('click',videoChangeTime);
progressBar.addEventListener('mousemove',videoPossibleTime);
progressBar.addEventListener('mouseout',hiddenPossibleTime);


function fullScreenVideo() { //разворачиваем видео на весь экран
    if (!document.fullscreenElement) {
        if (videoContainer.requestFullscreen) {
            videoContainer.requestFullscreen();
        } else if (videoContainer.mozRequestFullScreen) { // Firefox
            videoContainer.mozRequestFullScreen();
        } else if (videoContainer.webkitRequestFullscreen) { // Chrome, Safari и Opera
            videoContainer.webkitRequestFullscreen();
        } else if (videoContainer.msRequestFullscreen) { // IE/Edge
            videoContainer.msRequestFullscreen();
        }
        videoContainer.style.border = '0';
        videoContainer.style.borderRadius = '0';
        video.style.borderRadius = '0';
    }else {
        // Если уже в полноэкранном режиме, выходим из него
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { // Firefox
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { // Chrome, Safari и Opera
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }
    }
    }

fullscreenBtn.addEventListener('click',fullScreenVideo);

function exitHandler(){
    if (!document.fullscreenElement){
         videoContainer.style.border = '5px solid hwb(25 0% 20% / 1)';
         videoContainer.style.borderRadius = '50px';
         video.style.borderRadius = '45px';
    }
    }

document.addEventListener('webkitfullscreenchange', exitHandler);
document.addEventListener('mozfullscreenchange', exitHandler);
document.addEventListener('fullscreenchange', exitHandler);
document.addEventListener('MSFullscreenChange', exitHandler);


function videoChangeVolume(e) { //Меняем громкость
    var mouseY = Math.floor(volumeMax.getBoundingClientRect().bottom - e.clientY);
    volumeNow.style.height = mouseY+'px';
    var volume = volumeNow.offsetHeight / 70;
    video.volume = volume;
    if(video.volume == 0) {
        muteButton.style.boxShadow = 'inset 6px 0 hwb(0 22% 100% / 1)';
        muteButton.style.borderRightColor = 'hwb(0 22% 100% / 1)';
    } else {
        muteButton.style.boxShadow = 'inset 6px 0 hwb(25 0% 20% / 1)';
        muteButton.style.borderRightColor = 'hwb(25 0% 20% / 1)';
    }
    }

function videoMute() { //Убираем звук
    if(video.volume == 0) {
        video.volume = volumeNow.offsetHeight / 70;
        muteButton.style.boxShadow = 'inset 6px 0 hwb(25 0% 20% / 1)';
        muteButton.style.borderRightColor = 'hwb(25 0% 20% / 1)';
    } else {
        video.volume = 0;
        muteButton.style.boxShadow = 'inset 6px 0 hwb(0 22% 100% / 1)';
        muteButton.style.borderRightColor = 'hwb(0 22% 100% / 1)';
    }
    }

//Звук
muteButtonMain.addEventListener('click',videoMute);
volumeMax.addEventListener('click',videoChangeVolume);

function visibleVolume() {
    volumeChange.style.visibility = 'visible';
    }

function hiddenVolume(e) {
    if(e.relatedTarget !== volumeChange) {
        volumeChange.style.visibility = 'hidden';
    }
    }

muteButtonMain.addEventListener('mouseover',visibleVolume);
muteButtonMain.addEventListener('mouseout',hiddenVolume);
volumeChange.addEventListener('mouseover',visibleVolume);
volumeChange.addEventListener('mouseout',hiddenVolume);

rewindFirst.addEventListener('click',(event) => {
    if (video.currentTime + 30 < video.duration) {
        video.currentTime = video.currentTime + 30
    } else {
        video.currentTime = video.duration
    }
    });

rewindSecond.addEventListener('click',(event) => {
    if (video.currentTime + 60 < video.duration) {
        video.currentTime = video.currentTime + 60
    } else {
        video.currentTime = video.duration
    }
    });

rewindThird.addEventListener('click',(event) => {
    if (video.currentTime + 90 < video.duration) {
        video.currentTime = video.currentTime + 90
    } else {
        video.currentTime = video.duration
    }
    });



//ОТПРАВЛЯЕМ ЗАПРОСЫ НА СЕРВЕР!!!!!!!
function requestToServer(method, data) {
    const xhr = new XMLHttpRequest(); // создаем объект запроса
    xhr.open(method, '/change_viewed_seria/?'+data); // настраиваем запрос (метод и URL)
    xhr.send(); // отправляем запрос
    xhr.onreadystatechange = function () { // подписываемся на событие изменения состояния запроса
        if (xhr.readyState === 4) { // если запрос завершен
            if (xhr.status === 200) { // если статус код ответа 200 OK
                if (xhr.responseText.includes('http://video.animetop.info/')) {
                    urls_list = xhr.responseText.split(', ')
                    videoUrl.src = urls_list[0]; // выводим ответ сервера
                    videoUrlDop.src = urls_list[0].replace('info/', 'info/720/');
                    videoUrlFrame.src = urls_list[1]
                    video.load();
                    video.pause();
                    for (let control of videoControls) {
                        control.style.visibility = 'visible';
                    }
                    nowTime.innerHTML = '00:00';
                    allTime.innerHTML = '00:00';
                    progressBar.value = 0;
                } else if (xhr.responseText.includes('last_seria')) {
                    if(addTitleButton[0].id.includes('viewed')) {
                        titleId = addTitleButton[0].id.replace('viewed_', '');
                    } else {
                        titleId = addTitleButton[0].id.replace('want_', '');
                    }
                    elem = document.getElementById('viewed_'+titleId);
                    if(elem.className == 'to_add_in_my_list') {
                        elem.className = 'to_add_in_my_list_press';
                        elem.removeEventListener('click',addTitleInList);
                    }
                }
            } else {
                console.error(xhr.statusText); // выводим текст ошибки
            }
        }
    }};

//Находим нужную серию и сезон и выделяем их в списках
function getSeriaSeason() {
    isSent = false;
    seriaID = videoUrl.id.replace('its_', '');
    seria = document.getElementById(seriaID);
    seria.style.border = '3px solid hwb(25 0% 20% / 1)';
    seasonID = seria.parentNode.id;
    seriesBox = document.getElementById(seasonID);
    seriesBox.addEventListener('mouseover',visibleSeries);
    seriesBox.addEventListener('mouseout',hiddenSeries);
    season = document.getElementById(seasonID.replace('its_', ''));
    season.style.border = '3px solid hwb(25 0% 20% / 1)';
    previousSeria.style.visibility ='visible';
    previousSeria.classList.remove('hidden');
    nextSeria.style.visibility ='visible';
    nextSeria.classList.remove('hidden');
    if (seria == seriesBox.children[0]) {
        previousSeria.style.visibility ='hidden';
        previousSeria.classList.add('hidden');
    }
    if (seria == seriesBox.children[seriesBox.children.length-1]) {
        nextSeria.style.visibility ='hidden';
        nextSeria.classList.add('hidden');
    }
    for (let elem of seasonsBox.children) {
        if (elem != season) {
            elem.addEventListener('click',changeSeason);
        }
    }
    for (let elem of seriesBox.children) {
        if (elem != seria) {
            elem.addEventListener('click',changeSeria);
        }
    }
    }

requestToServer('GET', 'seria_id='+videoUrl.id.replace('its_seria_', ''));
getSeriaSeason();

// Функция для переключения серии
function changeSeria() {
    previousSeria.style.visibility ='visible';
    previousSeria.classList.remove('hidden');
    nextSeria.style.visibility ='visible';
    nextSeria.classList.remove('hidden');
    if (this == seriesBox.children[0]) {
        previousSeria.style.visibility ='hidden';
        previousSeria.classList.add('hidden');
    }
    if (this == seriesBox.children[seriesBox.children.length-1]) {
        nextSeria.style.visibility ='hidden';
        nextSeria.classList.add('hidden');
    }
    seriaID = videoUrl.id.replace('its_', '');
    seria = document.getElementById(seriaID);
    seria.style.border = '0';
    seria.addEventListener('click',changeSeria);
    this.style.border = '3px solid hwb(25 0% 20% / 1)';
    this.removeEventListener('click',changeSeria);
    videoUrl.id = 'its_'+this.id;
    data = 'seria_id='+videoUrl.id.replace('its_seria_', '');
    requestToServer('GET', data);
    isSent = false;
    }

//Переключить на предыдущую серию
function enterPrevious() {
  seriaID = videoUrl.id.replace('its_', '');
  seria = document.getElementById(seriaID);
  previous = seria.previousElementSibling;
  changeSeria.call(previous);
  }

previousSeria.addEventListener('click',enterPrevious);

//Переключить на следующую серию
function enterNext() {
  seriaID = videoUrl.id.replace('its_', '');
  seria = document.getElementById(seriaID);
  next = seria.nextElementSibling;
  changeSeria.call(next);
  }

nextSeria.addEventListener('click',enterNext);

//Функция для переключения сезона
function changeSeason() {
    seriaID = videoUrl.id.replace('its_', '');
    seria = document.getElementById(seriaID);
    seria.style.border = '0';
    seasonID = seria.parentNode.id;
    seriesBox = document.getElementById(seasonID);
    for (let elem of seriesBox.children) {
        if (elem != seria) {
            elem.removeEventListener('click',changeSeria);
        }
    }
    seriesBox.style.visibility ='hidden';
    seriesBox.removeEventListener('mouseover',visibleSeries);
    seriesBox.removeEventListener('mouseout',hiddenSeries);
    season = document.getElementById(seasonID.replace('its_', ''));
    season.style.border = '0';
    this.removeEventListener('click',changeSeason);
    videoUrl.id = 'its_' + document.getElementById('its_'+this.id).children[0].id
    data = 'seria_id='+videoUrl.id.replace('its_seria_', '');
    requestToServer('GET', data);
    getSeriaSeason();
    }

function visibleSeasons() {
    seasonsBox.style.visibility = 'visible';
    }

function hiddenSeasons(e) {
    if(e.relatedTarget !== seasonsBox) {
        seasonsBox.style.visibility = 'hidden';
    }
    }

function regScrollSeas() {
    visibleSeriaID = videoUrl.id.replace('its_', '');
    visibleSeria = document.getElementById(visibleSeriaID);
    visibleSeasonID = visibleSeria.parentNode.id;
    visibleSeason = document.getElementById(visibleSeasonID.replace('its_', ''));
    seasonsBox.scrollTop = visibleSeason.offsetTop-seasonsBox.offsetHeight/2;
    }

seasonsButton.addEventListener('mouseover',regScrollSeas);
seasonsButton.addEventListener('mouseover',visibleSeasons);
seasonsButton.addEventListener('mouseout',hiddenSeasons);
seasonsBox.addEventListener('mouseover',visibleSeasons);
seasonsBox.addEventListener('mouseout',hiddenSeasons);

function visibleSeries() {
    seriesBox.style.visibility = 'visible';
    }

function hiddenSeries(e) {
    if(e.relatedTarget !== seriesBox) {
        seriesBox.style.visibility = 'hidden';
    }
    }

function regScrollSer() {
    visibleSeriaID = videoUrl.id.replace('its_', '');
    visibleSeria = document.getElementById(visibleSeriaID);
    seriesBox.scrollTop = visibleSeria.offsetTop-seriesBox.offsetHeight/2;
    }

seriesButton.addEventListener('mouseover',regScrollSer);
seriesButton.addEventListener('mouseover',visibleSeries);
seriesButton.addEventListener('mouseout',hiddenSeries);

let timer;

function hideControls() {
    for (let control of videoControls) {
            control.style.visibility = 'hidden';
        }
    seasonsButton.style.visibility = 'hidden';
    seriesButton.style.visibility = 'hidden';
    previousSeria.style.visibility ='hidden';
    nextSeria.style.visibility = 'hidden';
    rewindSecond.style.visibility = 'hidden';
    rewindThird.style.visibility = 'hidden';
    bottomLine.style.visibility = 'hidden';
    bottomLineSecond.style.visibility = 'hidden';
    video.style.cursor = 'none';
    }

function showControls() {
    clearTimeout(timer);
    if (video.paused) {
        for (let control of videoControls) {
            control.style.visibility = 'visible';
        }
    }
    seasonsButton.style.visibility = 'visible';
    seriesButton.style.visibility = 'visible';
    if (!previousSeria.classList.contains('hidden')) {
        previousSeria.style.visibility ='visible';
    }
    if (!nextSeria.classList.contains('hidden')) {
        nextSeria.style.visibility = 'visible';
    }
    rewindSecond.style.visibility = 'visible';
    rewindThird.style.visibility = 'visible';
    bottomLine.style.visibility = 'visible';
    bottomLineSecond.style.visibility = 'visible';
    video.style.cursor = 'auto';
    }

function resetTimer() {
    showControls(); // Показывать элементы при движении мыши
     // Сбрасываем таймер
    timer = setTimeout(hideControls, 3000); // Устанавливаем новый таймер
    }

video.addEventListener('mousemove', resetTimer);
video.addEventListener('mouseout', showControls);


function visibleGenres() {
    genresBox.style.visibility = 'visible';
    }

function hiddenGenres(e) {
    if(e.relatedTarget !== genresBox) {
        genresBox.style.visibility = 'hidden';
    }
    }

genresBottom.addEventListener('mouseover',visibleGenres);
genresBottom.addEventListener('mouseout',hiddenGenres);
genresBox.addEventListener('mouseover',visibleGenres);
genresBox.addEventListener('mouseout',hiddenGenres);


function addTitleInList() {
    data = 'list_title='+this.id;
    requestToServer('POST', data);
    this.className = 'to_add_in_my_list_press';
    this.removeEventListener('click',addTitleInList);
    if(this.id.includes('viewed')) {
    elem = document.getElementById(this.id.replace('viewed', 'want'));
    elem.className = 'to_add_in_my_list';
    elem.addEventListener('click',addTitleInList);
    } else {
    elem = document.getElementById(this.id.replace('want', 'viewed'));
    elem.className = 'to_add_in_my_list';
    elem.addEventListener('click',addTitleInList);
    }
    }

function pressTitleButton() {
    for(let elem of addTitleButton) {
        elem.addEventListener('click',addTitleInList);
        }
    }

pressTitleButton();

function newVideoViewed() {
    watchedPercentage = (video.currentTime / video.duration) * 100;
    if(watchedPercentage>0.01 && !isSent) {
        data = 'new_seria='+videoUrl.id.replace('its_seria_', '');
        requestToServer('POST', data);
        isSent = true;
        if(addTitleButton[0].id.includes('viewed')) {
            titleId = addTitleButton[0].id.replace('viewed_', '');
        } else {
            titleId = addTitleButton[0].id.replace('want_', '');
        }
        elem = document.getElementById('want_'+titleId);
        if(elem.className == 'to_add_in_my_list_press') {
            elem.className = 'to_add_in_my_list';
            elem.addEventListener('click',addTitleInList);
        }
    }}

video.addEventListener('timeupdate',newVideoViewed);