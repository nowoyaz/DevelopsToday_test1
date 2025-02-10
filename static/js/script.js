document.addEventListener('DOMContentLoaded', () => {
  const chatContainer = document.getElementById('chat');
  const inputField = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');

  // Функция для добавления сообщения в чат
  function appendMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', sender);
    messageDiv.textContent = content;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Функция для отображения spinner
  function showSpinner() {
    const spinnerDiv = document.createElement('div');
    spinnerDiv.classList.add('spinner-message');
    spinnerDiv.innerHTML = `<div class="spinner-border text-primary" role="status">
      <span class="sr-only">Загрузка...</span>
    </div>`;
    chatContainer.appendChild(spinnerDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return spinnerDiv;
  }

  async function sendMessage() {
    const message = inputField.value.trim();
    if (!message) return;
    appendMessage("Пользователь: " + message, "user");
    inputField.value = "";

    // Показываем спиннер в том месте, где должно появиться новое сообщение
    const spinnerDiv = showSpinner();

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      spinnerDiv.remove();  // удаляем спиннер после получения ответа
      appendMessage("Бот: " + data.response, "bot");
    } catch (error) {
      spinnerDiv.remove();
      appendMessage("Ошибка при отправке запроса.", "bot");
      console.error(error);
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });
});
