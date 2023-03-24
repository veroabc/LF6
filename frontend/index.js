window.onload = () => {
    const messages = []

    const inputEl = document.getElementById("message-input")
    const sendButton = document.getElementById("send-btn")
    const chatInput = document.getElementById("chat")

    sendButton.onclick = () => {
        const message = inputEl.value

        fetch("127.0.0.1:8000/ask", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message
            })
        }).then(res => {
            console.log("Request complete! response:", res);
        });
    }
}