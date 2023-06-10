import websockets
import asyncio
import privat
import aiopath
import aiofile
import datetime


class Server:
    def __init__(self):
        self.clients = set()

    async def test_handler(self, websocket):
        message = await websocket.recv()
        if message == "exchange":
            await self.handle_exchange(websocket)
        else:
            print(message)

    async def handle_exchange(self, websocket):
        app = privat.ConsoleApp()  # Создание экземпляра класса ConsoleApp из модуля privat
        await app.run()

    async def handle_message(self, websocket, path):
        # Добавить клиента в список подключенных
        self.clients.add(websocket)

        try:
            while True:
                message = await websocket.recv()
                await self.log_exchange_command(message)
        except websockets.exceptions.ConnectionClosed:
            # Удалить клиента из списка подключенных при разрыве соединения
            self.clients.remove(websocket)

    async def log_exchange_command(self, message):
        log_file_path = aiopath.Path('exchange.log')

        async with aiofile.async_open(log_file_path, mode='a') as file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f'{timestamp}: {message}\n'
            await file.write(log_entry)

            await self._send_exchange_rates(log_file_path)

    async def _send_exchange_rates(self, log_file_path):
        async with aiofile.async_open(log_file_path, mode='r') as file:
            exchange_rates = await file.read()

        # Отправить курсы валют по веб-сокету всем подключенным клиентам
        for client in self.clients:
            await client.send(exchange_rates)

    async def main(self):
        async with websockets.serve(self.test_handler, 'localhost', 1234):
            await asyncio.Event().wait()

if __name__ == '__main__':
    import privat  # Импортируем модуль privat
    server = Server()
    asyncio.run(server.main())

