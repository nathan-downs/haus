"""
Updated client.py to define a simple client for interacting with a key/value store server.
This includes functions for establishing a connection, sending various commands,
and handling server responses.
"""
import socket

# Client to test key-value store

server_address = ('localhost', 8080)
def send_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    try:
        sock.sendall(command)
        # limit response to prevent overflow
        response = sock.recv(1024)
    finally:
        sock.close()
    return response.decode()

def test_complex_transaction():
    
    # add
    commands = [
        b'START',
        b'PUT winstonc {"first_name":"Winston", "last_name":"Churchill", "role":"Prime Minister"}',
        b'PUT georgew {"first_name":"George", "last_name":"Washington", "role":"President"}',
        b'PUT alexh {"first_name":"Alexander", "last_name":"Hamilton", "role":"Secretary of the Treasury"}',
        b'COMMIT'
    ]

    # delete
    # commands = [
    #     b"START",
    #     b"DEL winstonc",
    #     b"DEL georgew",
    #     b"DEL alexh",
    #     b"COMMIT"
    # ]
    
    # rollback
    # commands = [
    #     b'START',
    #     b'PUT margrett {"first_name":"Margret", "last_name":"Thatcher", "role":"Prime Minister"}',
    #     b'ROLLBACK',
    #     b'COMMIT'
    # ]

    # get
    # commands = [
    #     b'START',
    #     b'GET alexh',
    #     b'COMMIT'
    # ]

    responses = send_command(b'\n'.join(commands))
    print(responses)

    # debug
    # for i in range(len(commands)):
    #     print(f'command[{i}] => {commands[i].decode("utf-8")}')

test_complex_transaction()
