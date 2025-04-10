const client_id = Date.now();

let web_socket = new WebSocket(`ws://myddnslol.ddns.net:8000/wss/${client_id}`);

web_socket.onopen = () => {
    console.log('WebSocket Connection established');
};

web_socket.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log(response)
    hideTypingIndicator()
    addMessage(response.content, false);
};

const dialogEditor = document.getElementById('dialogEditor');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.querySelector('.typing-indicator');

function showTypingIndicator() {
    console.log("showTypingIndicator");
    typingIndicator.style.display = 'block';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    console.log("hideTypingIndicator");
    typingIndicator.style.display = 'none';
}

function addMessage(message, isUser = true) {
    console.log("addMessage");
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'tutor'}`;
    messageDiv.textContent = message;
    chatMessages.insertBefore(messageDiv, typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function submitDialog() {
    console.log("submitDialog");
    const message = dialogEditor.value;
    if (!message.trim()) return;

    addMessage(message, true);
    dialogEditor.value = '';
    showTypingIndicator();
    try {
        if (web_socket.readyState === WebSocket.OPEN) {
            const data_dialog = {
                type: 'chat',
                content: message,
                timestamp: new Date().toISOString()
            };
            web_socket.send(JSON.stringify(data_dialog));
            console.log(data_dialog.content)
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Error submitting dialog:', error);
        alert('Error submitting dialog. Please try again.');
    }
}


window.addEventListener('load', () => {
    addMessage('Здравствуйте! Я ваш виртуальный тьютор. Чем могу помочь?', false);
});

dialogEditor.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitDialog();
    }
});
