function togglePassword() {

    const password = document.getElementById("password");

    const button = document.querySelector(".show-password");


    if (password.type === "password") {

        password.type = "text";

        button.textContent = "🙈";

    } else {

        password.type = "password";

        button.textContent = "👁";
    }
}