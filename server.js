const WebSocket = require('ws');

// Создаем WebSocket сервер на порту 8080
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws) {
    console.log('Новое подключение');

    // Когда получаем сообщение, отправляем его всем клиентам
    ws.on('message', function incoming(message) {
        console.log('получено: %s', message);

        // Отправляем сообщение всем подключенным клиентам
        wss.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    });
});

console.log('WebSocket сервер запущен на порту 8080');
