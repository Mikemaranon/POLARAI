let i = 0;

function write_text(time) {
    const titleElement = document.getElementById("title");
    const cursorElement = document.getElementById("cursor");

    if (!titleElement) return; // error handling

    const text = titleElement.textContent; // save the content of the element
    titleElement.textContent = ""; // delete the content of the element
    i = 0; //  reset the index
    cursorElement.style.display = "inline"; // show the cursor
    setTimeout(type, 200); // wait 0.6 sec before starting

    function type() {
        if (i < text.length) {
            titleElement.textContent += text[i];
            i++;
            setTimeout(type, time); // Velocidad de escritura (en ms)
        } else {
            cursorElement.style.display = "none"; // Oculta el cursor al finalizar
        }
    }
}

// Hacer la función accesible globalmente
window.write_text = write_text;