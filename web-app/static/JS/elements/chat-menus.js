const chatContainer = document.getElementById("chat-box");
const leftSection = document.getElementById("left-menu");  // Cambiar ID correcto
const rightSection = document.getElementById("right-menu"); // Cambiar ID correcto

const width_Limit = 970

function toggleSection(sectionId) {

    const section = document.getElementById(sectionId);
    if (!section || !leftSection || !rightSection) return; // Evita errores si no existen

    if (window.innerWidth <= width_Limit) {
        // Si la pantalla es pequeña, ocultamos el menú contrario
        if (sectionId === "left-menu" && rightSection.classList.contains("small-width-active")) {
            rightSection.classList.remove("small-width-active");
        }
        if (sectionId === "right-menu" && leftSection.classList.contains("small-width-active")) {
            leftSection.classList.remove("small-width-active");
        }
        section.classList.toggle("small-width-active");

        if (leftSection.classList.contains("small-width-active") || rightSection.classList.contains("small-width-active")) {
            chatContainer.classList.add("hide");
        } else {
            chatContainer.classList.remove("hide");
        }

    } else {
        section.classList.toggle("active");
    }
}

function updateLayout() {

    if (window.innerWidth > width_Limit) {
        leftSection.classList.remove("small-width-active");
        rightSection.classList.remove("small-width-active");

        leftSection.classList.add("active");
        rightSection.classList.add("active");

        chatContainer.classList.remove("hide");
    } else {
        leftSection.classList.remove("active");
        rightSection.classList.remove("active");
    }
}

// Se ejecuta al cambiar el tamaño de la pantalla
window.addEventListener("resize", updateLayout);

// Se ejecuta al cargar la página
document.addEventListener("DOMContentLoaded", () => {
    updateLayout();

    // Añadimos los eventos de los botones de toggle
    document.getElementById("showLeft").addEventListener("click", () => toggleSection("left-menu"));
    document.getElementById("showRight").addEventListener("click", () => toggleSection("right-menu"));

    // Evento para cambio de tamaño de pantalla
    window.addEventListener("resize", updateLayout);
});
