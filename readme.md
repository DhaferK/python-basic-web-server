## Project Overview
This project implements a basic web server in Python that handles HTTP requests and generates appropriate responses, including streaming responses using generators. The project demonstrates advanced features of Python, including:

- Decorators
- Generators
- Iterators
- Coroutines & async iterators
- Inheritance
- Singleton pattern
- Context managers

## Design Choices

### Decorators
- **log_request**: Logs each incoming request.
- **authorized_request**: Checks if a request is authorized by verifying the presence of the 'Authorization' header.

### Generators
- **response_generator**: Generates HTTP responses for predefined messages and status codes.
- **streaming_response_generator**: Yields parts of a response incrementally to simulate streaming.

### Iterators
- **RequestIterator**: Implements the iterator protocol to manage multiple requests.

### Coroutines & Async Iterators
- **async_request_handler**: Processes requests asynchronously.
- **AsyncRequestIterator**: Manages multiple requests asynchronously.

### Inheritance and Polymorphism
- **BaseRequestHandler**: Abstract base class with an abstract method `handle_request`.
- **GetRequestHandler** and **PostRequestHandler**: Derived classes that handle GET and POST requests, respectively.

### Singleton Pattern
- **WebServer**: Ensures only one instance of the server is created.

### Context Managers
- **ServerContextManager**: Manages the server's lifecycle (start and stop).

## File Structure
.
├── webserver.py # Server script
└── client.py # Client script


## Dependencies
- Python 3.7 or later

## How to Run the Server
1. Clone the repository or copy the scripts to your local machine.
2. Install Python if not already installed.
3. Run the server script:

python webserver.py


This will start the server on `127.0.0.1:8080`.

## How to Test the Server

### Using curl:
Open a terminal and use the following command to test the streaming response:
curl -X GET http://localhost:8080/stream-response -H "Authorization: Bearer token" -N

### Using the Custom Python Client:
Run the client script:

python client.py


This will send a request to the server and print the responses.

## Code Explanation

### webserver.py

- **Logging Configuration**: Sets up basic logging configuration.

- **Decorators**:
  - **log_request**: Logs incoming requests.
  - **authorized_request**: Checks for the 'Authorization' header in requests.

- **Generators**:
  - **response_generator**: Yields predefined HTTP responses.
  - **streaming_response_generator**: Yields parts of a response incrementally with a delay.

- **Request Parsing**:
  - **parse_http_request**: Parses raw HTTP requests into a structured format.

- **Iterators**:
  - **RequestIterator**: Manages multiple requests using the iterator protocol.

- **Async Handlers**:
  - **async_request_handler**: Processes requests asynchronously.
  - **AsyncRequestIterator**: Manages multiple requests asynchronously.

- **Request Handlers**:
  - **BaseRequestHandler**: Abstract base class for request handlers.
  - **GetRequestHandler**: Handles GET requests.
  - **PostRequestHandler**: Handles POST requests.

- **Server Management**:
  - **WebServer**: Implements the singleton pattern to ensure a single instance of the server.
  - **ServerContextManager**: Manages the server's lifecycle.

### client.py

- **send_request**: Sends an HTTP request to the server and prints the response incrementally.

## Example Output

### Terminal Output for curl

curl -X GET http://localhost:8080/stream-response -H "Authorization: Bearer token" -N


## Testing
Unittest was used for testing the server's functionalities. The tests include validating the server's responses to various HTTP requests and ensuring that streaming responses are handled correctly.

## Conclusion
This project demonstrates a simple yet comprehensive example of building a web server in Python with advanced features like decorators, generators, async handling, the singleton pattern, and context managers. The server can handle standard HTTP requests and stream responses, making it suitable for learning and extending with more features.



