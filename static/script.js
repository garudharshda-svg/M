const messageInput = document.getElementById("message-input");
const sendButton = document.querySelector(".send-btn");
const chatArea = document.querySelector(".chat-area");
const welcomeScreen = document.querySelector(".welcome-screen");


// Send message when button is clicked
sendButton.addEventListener("click", sendMessage);


// Send message when Enter is pressed
messageInput.addEventListener("keydown", function(event) {

    // Enter without Shift = send
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }

});


async function sendMessage() {

    const message = messageInput.value.trim();

    // Don't send empty messages
    if (!message) {
        return;
    }


    // Hide welcome screen
    welcomeScreen.style.display = "none";


    // Show user's message
    addMessage(message, "user");


    // Clear input
    messageInput.value = "";


    // Disable button while waiting
    sendButton.disabled = true;


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        if (data.response) {

            // Show Gemini's response
            addMessage(data.response, "bot");

        } else {

            addMessage(
                "Sorry, something went wrong.",
                "bot"
            );

        }


    } catch (error) {

        console.error("Error:", error);

        addMessage(
            "Unable to connect to Gemini.",
            "bot"
        );

    }


    // Enable button again
    sendButton.disabled = false;
}


function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    messageDiv.textContent = message;


    // Find or create message container
    let chatMessages = document.getElementById("chat-messages");


    if (!chatMessages) {

        chatMessages = document.createElement("div");

        chatMessages.id = "chat-messages";

        chatArea.insertBefore(
            chatMessages,
            document.querySelector(".input-container")
        );

    }


    chatMessages.appendChild(messageDiv);


    // Scroll to latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}