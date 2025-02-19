
var genresBottom = document.getElementById('genres_bottom');
var genresBox = document.getElementsByClassName('genres_box')[0];
var addTitleButton = document.getElementsByClassName('to_add_in_my_list');


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


//ОТПРАВЛЯЕМ ЗАПРОСЫ НА СЕРВЕР!!!!!!!
function requestToServer(method, data) {
    const xhr = new XMLHttpRequest(); // создаем объект запроса
    xhr.open(method, '/change_viewed_seria/?'+data); // настраиваем запрос (метод и URL)
    xhr.send(); // отправляем запрос
    xhr.onreadystatechange = function () { // подписываемся на событие изменения состояния запроса
        if (xhr.readyState === 4) { // если запрос завершен
            if (xhr.status === 200) { // если статус код ответа 200 OK
                if (xhr.responseText) {
                    console.log(xhr.responseText); // выводим ответ сервера
                }
            } else {
                console.error(xhr.statusText); // выводим текст ошибки
            }
        }
    }};

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