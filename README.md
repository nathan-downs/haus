# In-Memory Key-Value Data Server

This directory contains the source code for an in-memory, key-value data server that supports transactions and persists data state. The server stores data state in JSON format locally and attempts to reload it upon initialization. It can handle multiple clients and supports the following commands:

- PUT: add or update a key-value pair
- GET: retrieve a value by key  
- DEL: delete a value by key
- START: start a new transaction
- COMMIT: commit the current transaction
- ROLLBACK: rollback the current transaction


## Requirements

- Python 3.x

## Setup

Install the required packages by running `pip install -r requirements.txt`.

Start the server by running `python InMemoryKeyValueStore.py`.  

Use a socket client to connect to the server and send commands, e.g., `python client.py`.

## Usage

Here's an example of how to use the server:

```python
import socket

# Connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8080)
sock.connect(server_address)

# Add a key-value pair
sock.sendall(b'PUT key1 value1')
# Receive the response from the server
# Limit the response to prevent overflow
response = sock.recv(1024).decode()
# Print the response
print(response)  

# Add another key-value pair
sock.sendall(b'PUT key2 value2')
response = sock.recv(1024).decode()
print(response)

# Get the value of a key
sock.sendall(b'GET key1')
response = sock.recv(1024).decode()
print(response)

# Start a new transaction
commands = [
  b'START'
  b'DEL key1',
  b'COMMIT'
]

sock.sendall(b'\n'.join(commands))
responses = send_command(b'\n'.join(commands))
print(responses)
# Close the socket
sock.close()
```

This example connects to the server, adds two key-value pairs as individual commands, retrieves the value of a key, and then starts a transaction, deletes a key, and commits the transaction. The response from the server is printed to the console.

Note that this is just a simple example, and you can modify it to suit your needs. You can also use other socket client libraries or tools to connect to the server and send commands.

## Assumptions

- The server is running on localhost and listening on port 8080.
- The server and client are communicating over a plain socket connection.
- All commands and server responses are encoded as UTF-8 strings.
- The START command starts a new transaction.
- The COMMIT command commits the current transaction.  
- The ROLLBACK command discards changes made in the current transaction.
- The PUT command adds or updates a key-value pair.
- The GET command retrieves the value of a key.
- The DEL command deletes a key-value pair.
- Commands are sent as UTF-8 strings.
- The server returns a JSON object with the following keys:
  - status: required, "Ok" or "Error"
  - result: optional, result of a command
  - message: optional, additional context, such as a human-readable message
- The server persists data state in JSON format.
- The server attempts to reload data state upon initialization.
- The server supports multiple clients.
- Transactions are limited to 1024 bytes to prevent arbitrary data lengths.

## Error Handling

If the server encounters an error, it will return a JSON object with a status field set to "Error" and a message field containing a human-readable error message.

## Example Command Sequence with Server Feedback

Here's an example command sequence with server feedback:

```
START
{"status": "Ok", "result": "Transaction started"}
PUT {"key": "key1", "value": "value1"}  
{"status": "Ok", "result": {"key": "key1", "value": "value1"}}
PUT {"key": "key2", "value": "value2"}  
{"status": "Ok", "result": {"key": "key2", "value": "value2"}} 
GET key1
{"status": "Ok", "result": {"key": "key1", "value": "value1"}}
COMMIT
{"status": "Ok", "result": "Transaction commited"}
```

This example shows a complete command sequence with the server's responses. The client starts by sending a START command to begin a new transaction. The server responds with a success message.

Next, the client sends two PUT commands to add two key-value pairs to the server. The server responds with success messages for each command. 

The client then sends a GET command to retrieve the value associated with the key "key1". The server responds with a JSON object containing the value "value1".

Finally, the client sends a COMMIT command to commit the current transaction. The server responds with a success message.

## Troubleshooting

If you encounter errors while using the server, check the following:

- Make sure that the server is running and listening on the correct port.
- Check that the commands you are sending to the server are in the correct format.
- Ensure that the client and server are encoding and decoding messages using the same character encoding (UTF-8).
- Check the server logs for any error messages or clues about what went wrong.

## Conclusion

This in-memory key-value data server is a simple and efficient way to store and retrieve key-value pairs in a transactional manner. The server can handle multiple clients and supports a variety of commands.

The server is implemented in Python and uses a plain socket connection for communication. The client and server communicate using JSON-encoded messages.

The server is designed to be easy to use and customize. You can modify the source code to add additional functionality or change the behavior of the server.

I hope you find this solution helpful! Let me know if you have any questions or feedback.
