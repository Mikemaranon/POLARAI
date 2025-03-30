document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const errorMessage = document.getElementById("error-message");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            // Sending credentials via fetch
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username, password: password })
            });

            const data = await response.json();

            if (response.ok && data.token) {
                store_token(data.token);
                window.location.href = "/home"; // Redirect after successful login
            } else {
                // Handle error response from server
                errorMessage.textContent = data.error || "An error occurred.";
                errorMessage.style.display = "block";
            }
        } catch (error) {
            console.error("Error during login:", error);
            errorMessage.textContent = "An error occurred, please try again.";
            errorMessage.style.display = "block";
        }
    });
});
