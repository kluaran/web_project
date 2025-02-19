
var genresBottom = document.getElementById('genres_bottom');
var genresBox = document.getElementsByClassName('genres_box')[0];
var addTitleButton = document.getElementsByClassName('to_add_in_my_list');
var deleteTitleButton = document.getElementsByClassName('delete_from_my_titles');


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
                location.reload();
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

    }

function deleteTitleFromList() {
    data = 'delete_title='+this.id;
    requestToServer('DELETE', data);
    }

function pressTitleButton() {
    for(let elem of addTitleButton) {
        elem.addEventListener('click',addTitleInList);
        }
    for(let elemD of deleteTitleButton) {
        elemD.addEventListener('click',deleteTitleFromList);
        }
    }

pressTitleButton();