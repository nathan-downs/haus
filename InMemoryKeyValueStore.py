"""
Implements an in-memory key/value store with support for transactions.

Provides methods to add, update, delete, and get key-value pairs. Supports
starting, committing, and rolling back transactions to group multiple
operations together.

Exposes a TCP server that accepts commands to manipulate the store.
"""
import threading
import json
import socketserver
import os

class InMemoryKeyValueStore:
    def __init__(self):
        try:
            with open('data.json', 'r') as f:
                data_json = json.load(f)
                self.data = data_json.get('data', {})
                self.transaction_data = data_json.get('transaction_data', {})
                self.pre_transaction_data = data_json.get('pre_transaction_data', {})
        except FileNotFoundError:
            self.data = {}
            self.transaction_data = {}
            self.pre_transaction_data = {}

        self.lock = threading.Lock()
        self.in_transaction = False
        self.rollback = False
        if not hasattr(self, 'active_keys'):
            self.active_keys = set()



    def add_key_value(self, key, value):
        with self.lock:
            if key in self.active_keys:
                return {"status": "Error", "mesg": f"Key, {key}, already exists"}
            self.active_keys.add(key)
            if self.in_transaction:
                self.transaction_data[key] = value
                return True
            if key in self.data:
                return False
            self.data[key] = value
            self.save_data()
            return True

    def update_key_value(self, key, value):
        with self.lock:
            if key in self.active_keys:
                return False
            self.active_keys.add(key)
            if self.in_transaction:
                self.transaction_data[key] = value
                return True
            if key not in self.data:
                return False
            self.data[key] = value
            self.save_data()
            return True

    def delete_key_value(self, key):
        with self.lock:
            if key in self.active_keys:
                self.active_keys.remove(key)
                if self.in_transaction:
                    self.transaction_data[key] = None
                else:
                    try:
                        del self.data[key]
                        self.save_data()
                    except KeyError:
                        pass
                return True
            elif key in self.transaction_data:
                del self.transaction_data[key]
                return True
            elif key in self.data:
                del self.data[key]
                self.save_data()
                return True
            return False

    def get_key_value(self, key):
        with self.lock:
            if key in self.active_keys:
                return None
            if self.in_transaction and key in self.transaction_data:
                return self.transaction_data[key] if self.transaction_data[key] is not None else None
            if key in self.data:
                value = self.data[key]
                try:
                    return json.loads(value) if isinstance(value, str) and value.strip().startswith('{') else value
                except json.JSONDecodeError:
                    return value
            return None

    def start_transaction(self):
        with self.lock:
            self.in_transaction = True
            self.rollback = False
            self.transaction_data = {}
            self.pre_transaction_data = dict(self.data)
            self.transaction_data_state = dict(self.transaction_data)
            self.load_data()

    def commit_transaction(self):
        with self.lock:
            for key, value in self.transaction_data.items():
                if value is None and key in self.data:
                    del self.data[key]
                elif value is not None:
                    self.data[key] = value
            self.in_transaction = False
            self.rollback = False
            self.transaction_data = {}
            self.active_keys.clear()
            self.save_data()

    def rollback_transaction(self):
        with self.lock:
            self.in_transaction = False
            self.data = dict(self.pre_transaction_data)
            self.transaction_data = dict(self.transaction_data_state)
            self.active_keys.clear()
            self.rollback = True

    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump({'data': self.data}, f, indent=4)

    def load_data(self):
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                try:
                    loaded_data = json.load(f)
                    self.data = loaded_data.get('data', {})
                    return self.data
                except ValueError:
                    return {}
        else:
            return {}

    def process_command(self, command):
        parts = command.split()
        if parts[0] == "PUT":
            key = parts[1]
            value = " ".join(parts[2:])
            result = self.add_key_value(key, value)
            return json.dumps({"status": "Ok", "result": result, "mesg": {"key":key, "value":value}}) if result else json.dumps({"status": "Error", "mesg": "Key already exists"})
        elif parts[0] == "GET":
            key = parts[1]
            value = self.get_key_value(key)
            if value is not None:
                return json.dumps({"status": "Ok", "result": {"key":key, "value":value}})
            else:
                return json.dumps({"status": "Error", "mesg": "Key not found"})
        elif parts[0] == "DEL":
            key = parts[1]
            result = self.delete_key_value(key)
            if result is None or result == False:
                return json.dumps({"status": "Error", "mesg": "Key not found"})
            else:
                return json.dumps({"status": "Ok", "result": result, "mesg": "Key deleted"})

        elif parts[0] == "START":
            self.start_transaction()
            return json.dumps({"status": "Ok", "result": "Transaction started"})
        elif parts[0] == "COMMIT":
            if self.rollback == True:
                return json.dumps({"status": "Error", "mesg": "Transaction rolled back"})
            if not self.in_transaction and self.rollback == False:
                return json.dumps({"status": "Error", "mesg": "No transaction started"})
            elif self.transaction_failed:
                return json.dumps({"status": "Error", "mesg": "Transaction failed"})
            self.commit_transaction()
            return json.dumps({"status": "Ok", "result": "Transaction committed"})
        elif parts[0] == "ROLLBACK":
            if not self.rollback == False:
                return json.dumps({"status": "Error", "mesg": "No transaction started"})
            self.rollback_transaction()
            self.transaction_failed = True
            return json.dumps({"status": "Ok", "result": "Transaction rolled back"})
        else:
            return json.dumps({"status": "Error", "result": "Invalid command"})


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Limit the response to prevent overflow
        self.data = self.request.recv(1024).strip().decode()
        commands = self.data.split('\n')
        responses = []
        self.server.store.in_transaction = False
        self.server.store.transaction_failed = False
        for command in commands:
            if command: # Ignore empty lines
                try:
                    response = self.server.store.process_command(command.strip())
                    response_data = json.loads(response)
                    if response_data["status"] == "Error":
                        self.server.store.transaction_failed = True
                        self.server.store.in_transaction = False
                        responses = [response]
                        break
                    if response_data.get("result") == "Transaction started":
                        self.server.store.in_transaction = True
                    responses.append(response)
                except Exception as e:
                    self.server.store.transaction_failed = True
                    self.server.store.in_transaction = False
                    responses = [json.dumps({"status": "Error", "mesg": str(e)})]
                    break
        if not self.server.store.transaction_failed:
            final_response = "\n".join(responses)
            self.request.sendall(final_response.encode())
        else:
            error_response = responses[0] if responses else json.dumps({"status": "Error", "mesg": "Unknown error"})
            self.request.sendall(error_response.encode())

if __name__ == "__main__":
    store = InMemoryKeyValueStore()
    server = socketserver.TCPServer(("localhost", 8080), TCPHandler)
    server.store = store
    server.serve_forever()
