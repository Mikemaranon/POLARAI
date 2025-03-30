const TOKEN_KEY = "auth_token";

async function get_tokenFromServer(authEndpoint, credentials) {
    try {
        const response = await fetch(authEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(credentials)
        });

        if (!response.ok) {
            throw new Error("Failed to retrieve token.");
        }

        const data = await response.json();
        if (data.token) {
            store_token(data.token);
        } else {
            throw new Error("No token received.");
        }
    } catch (error) {
        console.error("Error fetching token:", error);
        throw error;
    }
}

function store_token(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

async function send_API_request(method, endpoint, body = null) {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        throw new Error("No authentication token found.");
    }

    const options = {
        method: method.toUpperCase(),
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    };

    if (body && method.toUpperCase() !== "GET") {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(endpoint, options);

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error("Error in API request:", error);
        throw error;
    }
}
