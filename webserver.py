import socket
import asyncio
import functools
import logging
import random
from abc import ABC, abstractmethod
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 2 - Decorator to log each incoming request
def log_request(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        logging.info(f"Received request: {request['method']} {request['path']}")
        return func(*args, **kwargs)
    return wrapper

# 2 - Decorator to check if a request is authorized
def authorized_request(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if 'Authorization' not in request['headers'] or request['headers']['Authorization'] != 'Bearer token':
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper

# 3 - Generator function that generates HTTP responses
def response_generator():
    responses = [
        ("Hello, World!", 200),
        ("Not Found", 404),
        ("Internal Server Error", 500)
    ]
    for response in responses:
        yield response

# 3 - Generator function that yields parts of a response incrementally
async def streaming_response_generator(client_socket):
    response_parts = [
    "Once upon a time, ",
    "in a small village, ",
    "there lived kind villagers. ",
    "They loved welcoming travelers. ",
    "One sunny morning, ",
    "a weary traveler arrived. ",
    "He was greeted warmly, ",
    "given food and shelter. ",

    "The traveler shared stories ",
    "of distant lands and adventures. ",
    "The villagers listened eagerly ",
    "and enjoyed his tales. ",
    "He decided to stay, ",
    "building a small house. ",
    "He planted a garden ",
    "with fresh vegetables and herbs. "
]

    try:
        for part in response_parts:
            chunk_length = f"{len(part):X}\r\n"
            await asyncio.get_event_loop().sock_sendall(client_socket, chunk_length.encode('utf-8'))
            await asyncio.get_event_loop().sock_sendall(client_socket, part.encode('utf-8'))
            await asyncio.get_event_loop().sock_sendall(client_socket, b"\r\n")
            await asyncio.sleep(0.25)
        await asyncio.get_event_loop().sock_sendall(client_socket, b"0\r\n\r\n")
    except BrokenPipeError:
        print("Client disconnected")
    finally:
        client_socket.close()

def parse_http_request(request_data):
    lines = request_data.split('\r\n')
    request_line = lines[0].split(' ')
    method, path = request_line[0], request_line[1]

    headers = {}
    for line in lines[1:]:
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value

    return {
        'method': method,
        'path': path,
        'headers': headers
    }

# 4 - Iterator class to manage multiple requests
class RequestIterator:
    def __init__(self, requests):
        self._requests = requests
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._requests):
            request = self._requests[self._index]
            self._index += 1
            return request
        else:
            raise StopIteration

# 5 - Asynchronous function to process requests
async def async_request_handler(request):
    processing_time = random.uniform(0.5, 1.5)
    await asyncio.sleep(processing_time)
    return f"Async response for {request['method']} {request['path']}", 200

# 5 - Async iterator class to manage multiple requests
class AsyncRequestIterator:
    def __init__(self, requests):
        self._requests = requests
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index < len(self._requests):
            request = self._requests[self._index]
            self._index += 1
            await asyncio.sleep(random.uniform(0.1, 0.5))
            return request
        else:
            raise StopAsyncIteration

# 6 - Base class with an abstract method
class BaseRequestHandler(ABC):
    @abstractmethod
    def handle_request(self, request):
        pass

# 6 - Derived class for GET requests
class GetRequestHandler(BaseRequestHandler):
    def handle_request(self, request):
        return f"Handled GET request for {request['path']}", 200

# 6 - Derived class for POST requests
class PostRequestHandler(BaseRequestHandler):
    def handle_request(self, request):
        return f"Handled POST request for {request['path']}", 201

@log_request
@authorized_request
def handle_request(request):
    if request['path'] == '/generate-response':
        return next(response_generator())
    elif request['path'] == '/stream-response':
        return 'Streaming response initiated', 200
    elif request['method'] == 'GET':
        handler = GetRequestHandler()
    elif request['method'] == 'POST':
        handler = PostRequestHandler()
    else:
        return "Method not allowed", 405
    return handler.handle_request(request)

# 7 - Context manager to manage server lifecycle
class ServerContextManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    async def __aenter__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        return self.server_socket

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.server_socket.close()
        print("Server stopped")

# 8 - Singleton pattern for WebServer
class WebServer:
    _instance = None

    def __new__(cls, host, port):
        if cls._instance is None:
            cls._instance = super(WebServer, cls).__new__(cls)
            cls._instance.host = host
            cls._instance.port = port
        return cls._instance

    async def start(self):
        async with ServerContextManager(self.host, self.port) as server_socket:
            await self.run_server(server_socket)

    async def run_server(self, server_socket):
        while True:
            client_socket, addr = await asyncio.get_event_loop().sock_accept(server_socket)
            asyncio.create_task(self.handle_client(client_socket))

    async def handle_client(self, client_socket):
        try:
            request_data = await asyncio.get_event_loop().sock_recv(client_socket, 1024)
            request_text = request_data.decode('utf-8')

            if request_text.startswith('{'):
                
                request = json.loads(request_text)
                if 'requests' in request:
                    responses = await self.handle_async_requests(request['requests'])
                    response_data = json.dumps(responses)
                    await asyncio.get_event_loop().sock_sendall(client_socket, response_data.encode('utf-8'))
                    return
            else:
                request = parse_http_request(request_text)
                print(f"Received request: {request}")

            if request['path'] == '/stream-response':
                http_response_header = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nTransfer-Encoding: chunked\r\n\r\n"
                await asyncio.get_event_loop().sock_sendall(client_socket, http_response_header.encode('utf-8'))
                await streaming_response_generator(client_socket)
                return

            response = handle_request(request)
            response_body, status_code = response
            http_response = f"HTTP/1.1 {status_code} OK\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
            await asyncio.get_event_loop().sock_sendall(client_socket, http_response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    async def handle_async_requests(self, requests):
        async_request_iterator = AsyncRequestIterator(requests)
        tasks = [async_request_handler(request) async for request in async_request_iterator]
        responses = []
        for task in asyncio.as_completed(tasks):
            response = await task
            print(response)  # as it completes
            responses.append(response)
        return responses


def main():
    server = WebServer('127.0.0.1', 8080)
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
