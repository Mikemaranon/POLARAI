// Elementos del DOM
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-btn');
const chatHistory = document.getElementById('chat-history');

// Event Listeners
document.addEventListener('DOMContentLoaded', initializeChat);

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
        chatInput.style.height = '98    px';
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
    const containerHeight = newHeight + 40; // 40px para los paddings
    chatInput.style.height = Math.max(80, containerHeight) + 'px';
}

function clearInput() {
    messageInput.textContent = '';
    adjustInputHeight(); // Usar adjustInputHeight para manejar el reseteo
}

// Eliminar la función resetInputHeight ya que no es necesaria

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

function addMessageToChat(message, isUser = true) {
    chatHistory.appendChild(createMessageElement(message, isUser));
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

let aaa = 0;

async function sendMessageToServer(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data.response;

    } catch (error) {
        console.error('Error:', error);
        if (aaa < 5) {
            aaa++;
            return 'Lo siento, hubo un error al procesar tu mensaje.';
        } else {
            aaa = 0;
            return 'callate ya jdr';
        }
        
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