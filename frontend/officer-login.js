
const loginForm = document.getElementById("login-form");
const loginButton = document.getElementById("login-button");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    loginButton.disabled = true;
    loginMessage.textContent = "Signing in...";

    try {
        const response = await fetch("/officer/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }

        // Store the demo token for subsequent officer API requests.
        sessionStorage.setItem("officer_token", data.access_token);
        sessionStorage.setItem("officer_details", JSON.stringify(data.officer));

        loginMessage.textContent = "Login successful. Opening dashboard...";

        // We'll create this page in the next step.
        window.location.href = "/officer-dashboard";
    } catch (error) {
        loginMessage.textContent = error.message;
    } finally {
        loginButton.disabled = false;
    }
});
