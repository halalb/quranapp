document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    // Display user message
    const chatMessages = document.getElementById('chat-messages');
    const userMessage = document.createElement('div');
    userMessage.textContent = `You: ${userInput}`;
    chatMessages.appendChild(userMessage);

    // Clear the input field
    document.getElementById('user-input').value = '';

    // Send message to Python server
    fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => {
        if (!response.ok) throw new Error('Server error');
        return response.json();
    })
    .then(data => {
        // Display chatbot response
        const botMessage = document.createElement('div');
        botMessage.textContent = `Bot: ${data.response}`;
        chatMessages.appendChild(botMessage);
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMessage = document.createElement('div');
        errorMessage.textContent = `Error: Something went wrong`;
        chatMessages.appendChild(errorMessage);
    });
});