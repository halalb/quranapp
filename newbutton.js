// --- state ------------------------------------------------------------
let currentChat   = { id: Date.now(), messages: [] };   // active chat
const allChats    = [];                                 // finished chats

// --- DOM helpers ------------------------------------------------------
const chatBox     = document.getElementById('chat-messages');
const userInput   = document.getElementById('user-input');
const sendBtn     = document.getElementById('send-button');
const newChatBtn  = document.getElementById('new-chat-btn');
const chatHistory = document.getElementById('chat-history');

// add one message bubble ----------------------------------------------
function appendBubble(text, from = 'user') {
  const div = document.createElement('div');


  div.className = `bubble ${from}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;   // stay at bottom
}

// render an old chat into the main pane --------------------------------
function loadChat(chat) {
  chatBox.innerHTML = '';
  chat.messages.forEach(m => appendBubble(m.text, m.role));
  currentChat = chat;               // resume this thread
}

// sidebar entry --------------------------------------------------------
function addHistoryItem(chat) {
  const btn = document.createElement('button');
  btn.textContent = `Chat ${new Date(chat.id).toLocaleTimeString()}`;
  btn.onclick = () => loadChat(chat);
  chatHistory.appendChild(btn);
}

// --- chat workflow ----------------------------------------------------
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = '';

  // front‑end echo
  appendBubble(text, 'user');
  currentChat.messages.push({ role: 'user', text });

  // POST to Flask
  const r = await fetch('http://localhost:8080/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: text,
      // chat_id: currentChat.id     <‑‑ uncomment when you handle this in Flask
    })
  });
  const data = await r.json();
  appendBubble(data.response, 'bot');
  currentChat.messages.push({ role: 'bot', text: data.response });
}

function startNewChat() {
  // 1. archive previous conversation (only if it has at least one message)
  if (currentChat.messages.length) {
    allChats.push(currentChat);
    addHistoryItem(currentChat);
  }

  // 2. reset UI + state
  chatBox.innerHTML = '';
  currentChat = { id: Date.now(), messages: [] };
}

// --- hook up events ---------------------------------------------------
sendBtn .addEventListener('click', sendMessage);
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
newChatBtn.addEventListener('click', startNewChat);
