import unittest
import asyncio
import socket
import time
from webserver import WebServer, parse_http_request

HOST = '127.0.0.1'
PORT = 8080  # Changed port to avoid conflicts

class TestWebServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = WebServer(HOST, PORT)
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.server_task = cls.loop.create_task(cls.server.start())
        cls.loop.run_until_complete(asyncio.sleep(1))  

    @classmethod
    def tearDownClass(cls):
        cls.server_task.cancel()
        try:
            cls.loop.run_until_complete(cls.server_task)
        except asyncio.CancelledError:
            pass
        cls.loop.stop()
        cls.loop.close()
        cls.release_port(HOST, PORT)
        time.sleep(1)  

    @staticmethod
    def release_port(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.close()

    async def send_request(self, method, path, headers):
        reader, writer = await asyncio.open_connection(HOST, PORT)

        request = f"{method} {path} HTTP/1.1\r\n"
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
        request += "\r\n"

        writer.write(request.encode('utf-8'))
        await writer.drain()

        response = await reader.read(4096)
        writer.close()
        await writer.wait_closed()

        return response.decode('utf-8')

    def test_get_request(self):
        async def run_test():
            response = await self.send_request('GET', '/test', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})
            self.assertIn("HTTP/1.1 200 OK", response)
            self.assertIn("Handled GET request for /test", response)

        self.loop.run_until_complete(run_test())

    def test_post_request(self):
        async def run_test():
            response = await self.send_request('POST', '/submit', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})
            self.assertIn("HTTP/1.1 201 OK", response)
            self.assertIn("Handled POST request for /submit", response)

        self.loop.run_until_complete(run_test())

    def test_unauthorized_request(self):
        async def run_test():
            response = await self.send_request('DELETE', '/delete', {'Host': f'{HOST}:{PORT}'})
            self.assertIn("HTTP/1.1 401 OK", response)
            self.assertIn("Unauthorized", response)

        self.loop.run_until_complete(run_test())

    def test_streaming_response(self):
        async def run_test():
            reader, writer = await asyncio.open_connection(HOST, PORT)

            request = f"GET /stream-response HTTP/1.1\r\nAuthorization: Bearer token\r\nHost: {HOST}:{PORT}\r\n\r\n"
            writer.write(request.encode('utf-8'))
            await writer.drain()

            headers = await reader.readuntil(b'\r\n\r\n')
            self.assertIn(b"HTTP/1.1 200 OK", headers)
            self.assertIn(b"Transfer-Encoding: chunked", headers)

            body = b""
            while True:
                length_str = await reader.readuntil(b'\r\n')
                length = int(length_str.decode('utf-8').strip(), 16)
                if length == 0:
                    break
                chunk = await reader.read(length + 2)
                body += chunk[:-2]

            writer.close()
            await writer.wait_closed()

            self.assertIn(b"Hello My name is Dhafer This is your streaming response", body)

        self.loop.run_until_complete(run_test())

    def test_response_generator(self):
        async def run_test():
            response = await self.send_request('GET', '/generate-response', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})
            self.assertIn("HTTP/1.1 200 OK", response)
            self.assertIn("Hello, World!", response)

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
