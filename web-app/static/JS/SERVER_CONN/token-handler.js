const TOKEN_KEY = "auth_token";

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
            "Authorization": "Bearer " + token
        }
    };
    
    if (body && method.toUpperCase() !== "GET") {
        options.body = JSON.stringify(body);
    }

    console.log("Fetching:", endpoint, options);

    try {
        const response = await fetch(endpoint, options);

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        return response;
    } catch (error) {
        console.error("Error in API request:", error);
        throw error;
    }
}
