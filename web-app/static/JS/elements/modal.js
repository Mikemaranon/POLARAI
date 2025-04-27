// Function to open the modal
function openModal() {
    const modal = document.getElementById("myModal");
    const fadeBackground = document.getElementById("fadeBackground");

    // Muestra el fondo opaco y el modal
    fadeBackground.style.display = "block";
    modal.style.display = "block";

    // Agrega las clases 'show' para la animación
    setTimeout(() => {
        fadeBackground.classList.add('show'); // Animar el fondo con fundido
        modal.classList.add('show'); // Animar el modal con deslizamiento
    }, 10); // Pequeño retraso para asegurar que el estilo se aplique correctamente
    
    fetchBots();
}

// Function to close the modal
function closeModal() {
    const modal = document.getElementById("myModal");
    const fadeBackground = document.getElementById("fadeBackground");

    // Quitar las clases 'show' para cerrar el modal y fondo
    modal.classList.remove('show');
    fadeBackground.classList.remove('show');

    // Después de la animación, ocultamos el modal y fondo
    setTimeout(() => {
        modal.style.display = "none"; // Ocultar el modal
        fadeBackground.style.display = "none"; // Ocultar el fondo
    }, 300); // Debe coincidir con el tiempo de la transición en CSS
}

// Close modal when clicking outside of the modal content
window.onclick = function(event) {
    const modal = document.getElementById("myModal");
    const fadeBackground = document.getElementById("fadeBackground");

    if (event.target == fadeBackground) {  // Si se hace clic fuera del modal
        closeModal(); // Cerrar el modal
    }
}


// Función para obtener la lista de bots desde la API
async function fetchBots() {

    response = await send_API_request("POST", "/api/get-models", null)
    
    if (!response.ok) {
        // console.log("error right here")
        const errorData = await response.json();
        alert(errorData.message || 'ERROR: bots could not be loaded');
        return;
    }
    //console.log("response: ", response)
    const data = await response.json();
    chat_displayBots(data.bots);
}

// Función para insertar los bots en el HTML como divs
function chat_displayBots(bots) {
    const container = document.getElementById('bots-container'); // Asegúrate de tener un contenedor con este id en tu HTML

    // Limpia el contenedor antes de agregar nuevos elementos
    container.innerHTML = '';

    if (bots.length === 0) {
        // Si no hay bots, muestra un mensaje
        container.innerHTML = '<p>No tienes bots disponibles.</p>';
        return;
    }

    // Recorre la lista de bots y crea un div para cada uno
    bots.forEach(bot => {
        const botDiv = document.createElement('div');
        botDiv.classList.add('bot-card');
        botDiv.innerHTML = `
            <h3>${bot}</h3>
        `;
    
        // Agregar el manejador de eventos para redirigir al usuario
        botDiv.addEventListener('click', () => {
            // Construir la URL con el nombre del bot como parámetro
            goToModelChat(bot)
        });
    
        // Agregar el div creado al contenedor
        container.appendChild(botDiv);
    });
}

async function goToModelChat(bot) {

    response = await send_API_request("POST", "/sites/polarai", { model: bot })

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    window.location.href = response.url;
    /*try {
        const response = await fetch('/sites/polarai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model: bot })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        window.location.href = response.url;

    } catch (error) {
        console.error('Error:', error);
        return 'Lo siento, hubo un error al procesar tu mensaje.';
    }*/
}