const password = document.querySelector("#id_password");
const toggleButton = document.querySelector("#togglePassword");

toggleButton.addEventListener("click", function () {

    if (password.type === "password") {
        password.type = "text";
        toggleButton.textContent = "Hide";
    } else {
        password.type = "password";
        toggleButton.textContent = "Show";
    }

});