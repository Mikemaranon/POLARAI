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
    try {
        // Realiza una solicitud POST a la API
        const response = await fetch('/api/get-models', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });

        // Si la respuesta no es exitosa, lanza un error
        if (!response.ok) {
            console.log("aqui esta el error")
            const errorData = await response.json();
            alert(errorData.message || 'Error al obtener los bots');
            return;
        }
        // Obtiene los datos en formato JSON
        const data = await response.json();

        // Llama a la función para insertar los bots en la interfaz
        displayBots(data.bots);

    } catch (error) {
        console.error('Error al obtener los bots:', error);
        alert('Error al obtener los bots');
    }
}

// Función para insertar los bots en el HTML como divs
function displayBots(bots) {
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
            const url = `/sites/polarai?bot=${bot}`;
            
            // Redirigir a la URL construida
            window.location.href = url;
        });
    
        // Agregar el div creado al contenedor
        container.appendChild(botDiv);
    });
    
}
