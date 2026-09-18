// Sleep Disorder AI - Client Interactivity
document.addEventListener("DOMContentLoaded", () => {
    // 1. Interactive slider value indicators
    const sliders = document.querySelectorAll("input[type='range']");
    sliders.forEach(slider => {
        const valDisplay = document.getElementById(slider.id + "_val");
        if (valDisplay) {
            valDisplay.textContent = slider.value;
            slider.addEventListener("input", (e) => {
                valDisplay.textContent = e.target.value;
            });
        }
    });

    // 2. Chatbot interactive handler
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    const sendBtn = document.getElementById("send-btn");

    if (chatForm && chatInput && chatMessages) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Append User message
            appendMessage("user", message);
            chatInput.value = "";
            chatInput.disabled = true;
            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
            }

            // Show animated typing indicator
            const typingIndicator = appendMessage(
                "bot",
                '<span class="typing-dots me-2"><span></span><span></span><span></span></span> Clinical AI is analyzing your query...'
            );

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                typingIndicator.remove();

                if (response.ok) {
                    appendMessage("bot", data.response);
                } else {
                    appendMessage("bot", "⚠️ " + (data.error || "Unable to reach AI assistant."));
                }
            } catch (err) {
                typingIndicator.remove();
                appendMessage("bot", "⚠️ Network error connecting to chat service.");
            } finally {
                chatInput.disabled = false;
                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                }
                chatInput.focus();
            }
        });
    }

    function appendMessage(sender, text) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${sender}`;
        bubble.innerHTML = text.replace(/\n/g, "<br>");
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return bubble;
    }

    // Quick suggestion prompt buttons
    const suggestionBtns = document.querySelectorAll(".suggestion-btn");
    suggestionBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            if (chatInput) {
                chatInput.value = btn.getAttribute("data-prompt");
                if (chatForm) {
                    chatForm.dispatchEvent(new Event("submit"));
                }
            }
        });
    });
});
