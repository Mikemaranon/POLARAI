async function handleLoginSubmit(event) {
    event.preventDefault(); // Prevent default form submission

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");

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
            try {
                const homeResponse = await send_API_request("POST", "/home");
                // window.location.href = "/home";
            } catch (error) {
                errorMessage.textContent = "Failed to access home. Please try again.";
                errorMessage.style.display = "block";
            }
        } else {
            // Manejar el error si el login falla
            errorMessage.textContent = data.error || "An error occurred.";
            errorMessage.style.display = "block";
        }
    } catch (error) {
        console.error("Error during login:", error);
        errorMessage.textContent = "Incorrect user, please try again.";
        errorMessage.style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    
    loginForm.addEventListener("submit", handleLoginSubmit);
});
