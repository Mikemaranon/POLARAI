// Elementos del DOM
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-btn');
const chatHistory = document.getElementById('chat-history');
const sumList = document.getElementById('right-menu-content')

const tempSlider = document.getElementById('temperature-slider');
const tempValue = document.getElementById('temperature-value');
const sysMsg = document.getElementById('system-message');

const showLeft = document.getElementById('showLeft')
const showRight = document.getElementById('showRight')


function toggleSection(sectionId, buttonId) {
    const section = document.getElementById(sectionId);
    const button = document.getElementById(buttonId);
    section.classList.toggle('hidden');
    if (section.classList.contains('hidden')) {
        button.style.display = 'block'; // Muestra el botón flotante
    } else {
        button.style.display = 'none';  // Oculta el botón flotante
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', initializeChat);
document.addEventListener("DOMContentLoaded", fetchChats);
document.addEventListener("DOMContentLoaded", setNewChatId);
document.addEventListener('click', (e) => {
    if (!e.target.closest('.opt-button') && !e.target.closest('.options-menu')) {
        document.querySelectorAll('.options-menu.active').forEach(menu => {
            menu.classList.remove('active');
        });
    }
});
tempSlider.addEventListener('input', function() {
    tempValue.textContent = this.value;
});

function initializeChat() {
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', handleKeyPress);
    messageInput.addEventListener('input', adjustInputHeight);
}

function adjustInputHeight() {
    // Guardar el contenido actual
    const content = messageInput.textContent;
    
    // Si está vacío, volver a la altura mínima
    if (!content.trim()) {
        messageInput.style.height = '20px';
        const chatInput = messageInput.closest('.chat-input');
        chatInput.style.height = '98px';
        return;
    }
    
    // Temporalmente establecer altura a auto para medir el contenido real
    messageInput.style.height = 'auto';
    
    // Calcular nueva altura basada en el contenido
    const scrollHeight = messageInput.scrollHeight;
    const newHeight = Math.max(20, Math.min(scrollHeight, 160));
    messageInput.style.height = newHeight + 'px';
    
    // Ajustar contenedor
    const chatInput = messageInput.closest('.chat-input');
    const containerHeight = newHeight + 40; // 40px for paddingss
    chatInput.style.height = Math.max(80, containerHeight) + 'px';
}

function clearInput() {
    messageInput.textContent = '';
    adjustInputHeight();
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
}


function createMessageElement(message, isUser = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'user-msg' : 'bot-msg';
    messageDiv.style.whiteSpace = 'pre-wrap';
    messageDiv.style.wordBreak = 'break-word';
    messageDiv.textContent = message;
    return messageDiv;
}

function createSummaryElement(summary, isActivated = true) {
    const sumDiv = document.createElement('div');
    sumDiv.className = isActivated ? 'summary-list active' : 'summary-list deactive';
    sumDiv.style.whiteSpace = 'pre-wrap';
    sumDiv.style.wordBreak = 'break-word';
    sumDiv.textContent = summary;
    return sumDiv;
}

function addMessageToChat(message, isUser = true) {
    chatHistory.appendChild(createMessageElement(message, isUser));
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function addSummaryToList(summary, isActivated = true) {
    sumList.appendChild(createSummaryElement(summary, isActivated));
    sumList.scrollTop = chatHistory.scrollHeight;
}

function addSystemMessage(msg) {
    sysMsg.innerHTML = msg;
}

async function sendMessageToServer(message) {
    try {
        const context = getChatContext()

        const response = await fetch('/api/send-message', {
            method: 'POST',
            headers: {  
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ context: context, message: message })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.sum == true) {
            getLatestSummary()
        }
        return data.response;

    } catch (error) {
        console.error('Error:', error);
        return 'Lo siento, hubo un error al procesar tu mensaje.';
    }
}

async function getLatestSummary() {
    try {
        const response = await fetch('/api/get-last-summary', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        } else {
            const summary = await response.json()
            addSummaryToList(summary, true)
        }
    }
    catch (error) {
        console.error(error)
    }
}

async function handleSendMessage() {
    const message = messageInput.textContent.trim();
    if (!message) return;

    // Add user message
    addMessageToChat(message, true);
    clearInput();

    // Get and add AI response
    const aiResponse = await sendMessageToServer(message);
    addMessageToChat(aiResponse, false);
}

function getChatContext() {
    
    // READ FAST CONFIG SECTION
    
    return ''
}

async function fetchChats() {

    try {
        const response = await fetch("/api/get-chats");
        if (!response.ok) throw new Error("Error al obtener los chats");

        const chats = await response.json();
        localStorage.setItem("chats", JSON.stringify(chats)); // Guarda en localStorage
        renderChats(chats); // Renderiza los chats en la UI
    } catch (error) {
        console.error("Error:", error);
    }
}

function renderChats(chats) {
    const container = document.getElementById("left-menu-content");
    container.innerHTML = ""; // Limpia el contenido anterior

    if (!chats || chats.length === 0) {
        container.innerHTML = "<p class='empty-message'>No hay chats disponibles</p>";
        return;
    }

    const addChat = document.createElement("div");
    addChat.classList.add("add-chat");
    addChat.textContent = `new chat`;
    addChat.addEventListener("click", () => {
        clearChat()
        setNewChatId()
    });
    container.appendChild(addChat);

    chats.forEach(chat => {
        const chatDiv = document.createElement("div");
        chatDiv.classList.add("chat-item");
        
        const chatContent = document.createElement("span");
        chatContent.textContent = `${chat.topic}`;
        chatDiv.appendChild(chatContent);
        
        // Crear el menú de opciones
        const optionsMenu = document.createElement("div");
        optionsMenu.classList.add("options-menu");
        
        // Crear botones del menú
        const summaryButton = document.createElement("button");
        summaryButton.classList.add("menu-button");
        summaryButton.textContent = "Hacer resumen de chat";
        summaryButton.onclick = (e) => {
            e.stopPropagation();
            console.log("Resumen del chat:", chat.id);
            optionsMenu.classList.remove('active');
        };

        const renameButton = document.createElement("button");
        renameButton.classList.add("menu-button");
        renameButton.textContent = "Cambiar título";
        renameButton.onclick = (e) => {
            e.stopPropagation();
            console.log("Cambiar título del chat:", chat.id);
            optionsMenu.classList.remove('active');
        };

        const deleteButton = document.createElement("button");
        deleteButton.classList.add("menu-button", "delete");
        deleteButton.textContent = "Eliminar chat";
        deleteButton.onclick = (e) => {
            e.stopPropagation();
            console.log("Eliminar chat:", chat.id);
            optionsMenu.classList.remove('active');
        };

        // Agregar botones al menú
        optionsMenu.appendChild(summaryButton);
        optionsMenu.appendChild(renameButton);
        optionsMenu.appendChild(deleteButton);
        
        // Crear el botón de opciones (tres puntos)
        const optButton = document.createElement("button");
        optButton.classList.add("opt-button");
        optButton.addEventListener("click", (e) => {
            e.stopPropagation();
            // Cerrar otros menús abiertos
            document.querySelectorAll('.options-menu.active').forEach(menu => {
                if (menu !== optionsMenu) {
                    menu.classList.remove('active');
                }
            });
            // Toggle del menú actual
            optionsMenu.classList.toggle('active');
        });

        chatDiv.appendChild(optButton);
        chatDiv.appendChild(optionsMenu);
        
        // Evento click para el chat-item
        chatDiv.addEventListener("click", () => {
            loadChatHistory(chat.id);
        });

        container.appendChild(chatDiv);
    });
}

async function loadChatHistory(id) {
    // Paso 1: Limpiar el historial del chat
    clearSumList()
    clearSysMsg()
    clearChat()

    // Paso 2: Enviar el `chatId` al servidor y recibir el chat
    try {
        // Enviar el chatId al servidor
        await setChatId(id);

        // Paso 3: Obtener la información del chat
        const data = await getChatInfo();  // Usamos await para esperar la respuesta

        // Paso 4: Cargar los mensajes del historial y los resúmenes
        data.messages.forEach((message) => {
            addMessageToChat(message.content, message.sender === 'user');
        });
        console.log("mensajes cargados");

        data.summary.forEach((sum) => {
            addSummaryToList(sum.content, sum.activated);
            console.log("resúmenes cargados");
        });

        addSystemMessage(data.system_msg);

        console.log("historial cargado");

    } catch (error) {
        console.error("Error al cargar el historial del chat:", error);
    }
}

async function setChatId(id) {
    try {
        const response_1 = await fetch("/api/set-chatId", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ chatId: id })
        });
        if (!response_1.ok) {
            throw new Error("Error al establecer el chatId");
        }  
    } catch (error) {
        console.error(error);
    }
}

async function getChatInfo() {
    try {
        const response_2 = await fetch("/api/get-singleChat", {
            method: "GET",
        });
        if (!response_2.ok) {
            throw new Error("Error al obtener la información del chat");
        }

        const data = await response_2.json();

        if (!data.messages || !Array.isArray(data.messages)) {
            throw new Error("La respuesta del servidor no contiene un historial de mensajes válido");
        }
        return data;

    } catch (error) {
        console.error(error);
        return { messages: [], summary: [] };  // Retornar valores vacíos en caso de error
    }
}

async function setNewChatId() {
    try {
        const response = await fetch("/api/create-chat", {
            method: "GET"
        });

        if (!response.ok) {
            throw new Error("Error al establecer nuevo chat");
        } else {
            console.log("Nuevo chat creado con éxito");
        }
    } catch (error) {
        console.error("Error al cargar el historial del chat:", error);
    }
}

function clearChat() {
    chatHistory.innerHTML = "";
}

function clearSumList() {
    sumList.innerHTML = ""; 
}

function clearSysMsg() {
    sysMsg.innerHTML = "";
}

