
var genresBottom = document.getElementById('genres_bottom');
var genresBox = document.getElementsByClassName('genres_box')[0];
const password = document.getElementById("password");
const confirm = document.getElementById("confirm");
const delete_acc = document.getElementById("delete_acc");


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


password.addEventListener("input", function (event) {
  if (password.validity.patternMismatch) {
    password.setCustomValidity("Пароль должен содержать минимум одну цифру, строчную букву, заглавную букву и спецсимвол!");
  } else {
    password.setCustomValidity("");
  }
  if (confirm.value !== password.value) {
    confirm.setCustomValidity("Пароли не совпадают!");
    confirm.classList.add('invalid');
    confirm_error.innerHTML = 'Пароли не совпадают!';
  } else {
    confirm.setCustomValidity("");
    confirm.classList.remove('invalid');
    confirm_error.innerHTML = "";
  }
});

confirm.addEventListener("input", function (event) {
  if (confirm.value !== password.value) {
    confirm.setCustomValidity("Пароли не совпадают!");
  } else {
    confirm.setCustomValidity("");
  }
});

password.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    password_error.innerHTML = "";
  };
  password.reportValidity();
};

password.onblur = function() {
  if (!password.checkValidity()) {
    password.classList.add('invalid');
    password_error.innerHTML = 'Некорректный пароль!';
  }
};

confirm.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    confirm_error.innerHTML = "";
  };
  if (!password.checkValidity()) {
    password.classList.add('invalid');
    password_error.innerHTML = 'Некорректный пароль!';
  }
  confirm.reportValidity();
  if (confirm.value !== password.value) {
    confirm.setCustomValidity("Пароли не совпадают!");
  } else {
    confirm.setCustomValidity("");
  }
};

confirm.onblur = function() {
  if (!confirm.checkValidity()) {
    confirm.classList.add('invalid');
    confirm_error.innerHTML = 'Пароли не совпадают!';
  }
};

delete_acc.addEventListener("input", function (event) {
  if (delete_acc.validity.patternMismatch) {
    delete_acc.setCustomValidity('Введите слово "УДАЛИТЬ" заглавными буквами');
  } else {
    delete_acc.setCustomValidity("");
  }
});

delete_acc.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    delete_acc_error.innerHTML = "";
  };
  delete_acc.reportValidity();
};

delete_acc.onblur = function() {
  if (!delete_acc.checkValidity()) {
    delete_acc.classList.add('invalid');
    delete_acc_error.innerHTML = 'Подтверждение введено не верно!';
  }
};