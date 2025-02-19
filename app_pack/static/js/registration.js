const name = document.getElementById("name");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirm = document.getElementById("confirm");


email.addEventListener("input", function (event) {
  if (email.validity.patternMismatch) {
    email.setCustomValidity("Не верный формат e-mail адреса!");
  } else {
    email.setCustomValidity("");
  }
});



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


check_box.addEventListener("input", function (event) {
  if (!check_box.checkValidity()) {
    check_box.classList.add('invalid');
    check_box_error.innerHTML = 'Для продолжения необходимо принять пользовательское соглашение!';
  } else {
    this.classList.remove('invalid');
    check_box_error.innerHTML = "";
  }
  if (!name.checkValidity()) {
    name.classList.add('invalid');
    name_error.innerHTML = 'Заполните это поле!';
  } 
  if (!email.checkValidity()) {
    email.classList.add('invalid');
    email_error.innerHTML = 'Поле заполнено не верно!';
  } 
  if (!password.checkValidity()) {
    password.classList.add('invalid');
    password_error.innerHTML = 'Некорректный пароль!';
  } 
  if (!confirm.checkValidity()) {
    confirm.classList.add('invalid');
    confirm_error.innerHTML = 'Пароли не совпадают!';
  } 
});


name.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    name_error.innerHTML = "";
  };
  name.reportValidity();
};

name.onblur = function() {
  if (!name.checkValidity()) {
    name.classList.add('invalid');
    name_error.innerHTML = 'Заполните это поле!';
  } 
};


email.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    email_error.innerHTML = "";
  };
  if (!name.checkValidity()) {
    name.classList.add('invalid');
    name_error.innerHTML = 'Заполните это поле!';
  } 
  email.reportValidity();
};

email.onblur = function() {
  if (!email.checkValidity()) {
    email.classList.add('invalid');
    email_error.innerHTML = 'Поле заполнено не верно!';
  } 
};


password.onfocus = function() {
  if (this.classList.contains('invalid')) {
    this.classList.remove('invalid');
    password_error.innerHTML = "";
  };
  if (!name.checkValidity()) {
    name.classList.add('invalid');
    name_error.innerHTML = 'Заполните это поле!';
  } 
  if (!email.checkValidity()) {
    email.classList.add('invalid');
    email_error.innerHTML = 'Поле заполнено не верно!';
  } 
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
  if (!name.checkValidity()) {
    name.classList.add('invalid');
    name_error.innerHTML = 'Заполните это поле!';
  } 
  if (!email.checkValidity()) {
    email.classList.add('invalid');
    email_error.innerHTML = 'Поле заполнено не верно!';
  } 
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


check_box.onblur = function() {
  if (!check_box.checkValidity()) {
    check_box.classList.add('invalid');
    check_box_error.innerHTML = 'Для продолжения необходимо принять пользовательское соглашение!';
  } 
};

