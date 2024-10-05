from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form id="form">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id="messages">
        </ul>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const form = document.getElementById('form');
            const input = document.getElementById('messageText');
            const messages = document.getElementById('messages');
            
            ws.onmessage = function(event) {
                const messageItem = document.createElement('li');
                messageItem.textContent = event.data;
                messages.appendChild(messageItem);
            };
            
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                ws.send(input.value);
                input.value = '';
            });
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"User says: {data}")
    except:
        await manager.disconnect(websocket)
