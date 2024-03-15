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

## Questions and future improvments

Here are some questions from Yen as well as some clarification and additional information:

-Q: Some notes on key/value visibility conditions during a transaction (for example, what is the behavior when multiple clients are trying to access the same key and one client connection is in the middle of a transaction and has modified a key)?

-A: The server utilizes a lock to ensure that only one thread can access the dictionary at a time. This means that if one client connection is in the middle of a transaction and has modified a key, any other client connection that tries to access the same key will be blocked until the transaction is committed or rolled back. Once the transaction is commited or rolled back, any changes will then be visible to other clients. 

If the transaction is committed, the changes to the key will be persisted and will be visible to other clients immediately. If the transaction is rolled back, the key will be restored to its previous state and any changes made during the transaction will be discarded.

It's important to note that the `InMemoryKeyValueStore` class does not support concurrent transactions that modify the same key. If two client connections try to start a transaction that modifies the same key at the same time, the second client connection will be blocked until the first transaction is committed or rolled back.

Additionally, the `InMemoryKeyValueStore` class does not support the concept of "dirty reads," which is when a client connection reads a key that is in the process of being modified by another client connection. If a client connection tries to read a key that is being modified by another client connection, it will be blocked until the modification is complete.

Overall, the `InMemoryKeyValueStore` class is designed to ensure data consistency and prevent data corruption by using locks to control access to the dictionary and by not allowing concurrent transactions that modify the same key. This helps to ensure that the data in the store is always in a consistent state, even when multiple clients are accessing the store simultaneously.

-Q:  What is the role of the active_keys set?  It seems like it is only cleared when a transaction is committed so what happens when commands are run outside of a transaction?

-A: The `active_keys` set is used to track the keys that are currently being modified during a transaction. When a key is added, updated, or deleted during a transaction, it is added to the `active_keys` set, which allows the class to keep track of which keys are being modified and to prevent other clients from modifying the same keys at the same time.

If commands are run outside of a transaction, the `active_keys` set is not used. This is because there is no need to track which keys are being modified, since there is no risk of data corruption or inconsistency.

-Q: Other questions that come to mind are around performance bottlenecks given that you are saving to disk for every modification (not a requirement of the problem) and how you'll want to address those.  Would also look into event based IO vs. threading.

-A: Yes, writing to disk would provide a performance bottleneck, especially if the store is being modified frequently. This was initially implemented to provide ease and repeatibility for testing, as well as state recovery for restarts. It can be removed and maintain the in-memory functionality.
