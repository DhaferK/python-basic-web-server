import socket
import asyncio
import json

# Server host and port
HOST = '127.0.0.1'
PORT = 8080

def send_request(method, path, headers):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    request = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    request += "\r\n"

    client_socket.sendall(request.encode('utf-8'))

    response = client_socket.recv(4096).decode('utf-8')
    client_socket.close()
    print(response)

async def async_send_request(method, path, headers):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    request = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    request += "\r\n"

    writer.write(request.encode('utf-8'))
    await writer.drain()

    response = await reader.read(4096)
    print(response.decode('utf-8'))

    writer.close()
    await writer.wait_closed()

async def async_stream_response(method, path, headers):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    request = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    request += "\r\n"

    writer.write(request.encode('utf-8'))
    await writer.drain()

    headers = await reader.readuntil(b'\r\n\r\n')
    print(headers.decode('utf-8'), end='')

    while True:
        try:
            length_str = await reader.readuntil(b'\r\n')
            length = int(length_str.decode('utf-8').strip(), 16)
            if length == 0:
                break
            chunk = await reader.read(length + 2)
            print(chunk.decode('utf-8')[:-2], end='', flush=True)
        except asyncio.IncompleteReadError:
            break

    writer.close()
    await writer.wait_closed()

async def main():
    # Example GET request
    print("Synchronous GET request:")
    send_request('GET', '/test', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Example POST request
    print("\nSynchronous POST request:")
    send_request('POST', '/submit', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Example unauthorized request
    print("\nSynchronous DELETE request (Unauthorized):")
    send_request('DELETE', '/delete', {'Host': f'{HOST}:{PORT}'})

    # Example async GET request
    print("\nAsynchronous GET request:")
    await async_send_request('GET', '/test', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Example async POST request
    print("\nAsynchronous POST request:")
    await async_send_request('POST', '/submit', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Test response_generator via server
    print("\nTesting response_generator via server:")
    send_request('GET', '/generate-response', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})
    send_request('GET', '/generate-response', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})
    send_request('GET', '/generate-response', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Test streaming_response_generator via server
    print("\nTesting streaming_response_generator via server:")
    await async_stream_response('GET', '/stream-response', {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'})

    # Test AsyncRequestIterator with server
    print("\nTesting AsyncRequestIterator with server:")
    requests = [
        {'method': 'GET', 'path': '/test', 'headers': {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'}},
        {'method': 'POST', 'path': '/submit', 'headers': {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'}},
        {'method': 'DELETE', 'path': '/delete', 'headers': {'Host': f'{HOST}:{PORT}'}},
        {'method': 'GET', 'path': '/test', 'headers': {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'}},
        {'method': 'POST', 'path': '/submit', 'headers': {'Authorization': 'Bearer token', 'Host': f'{HOST}:{PORT}'}}
    ]

    reader, writer = await asyncio.open_connection(HOST, PORT)
    request_data = json.dumps({'requests': requests})
    writer.write(request_data.encode('utf-8'))
    await writer.drain()

    response = await reader.read(4096)
    print(response.decode('utf-8'))

    writer.close()
    await writer.wait_closed()

# Run the async main function
asyncio.run(main())
