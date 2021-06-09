import socket
import threading
import re
import utils
from datetime import datetime

MESSAGE_MASK = re.compile('\[\d\d\].*')
CREDENTIALS_MASK = re.compile('\[1\d\].{3,16}:.{3,16}')


class Server:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.stored_users = dict()
        self.active_clients = list()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        print(f'[*] Listening on {self.ip}:{self.port}')
    

    def server_loop(self):
        while True:
            client_connection, client_address = self.socket.accept()
            print(f'[*] Incoming connection from {client_address[0]}:{client_address[1]}')
            client_connection.send('[00]'.encode())

            t = threading.Thread(target=self.handle_handshake, args=(client_connection,))
            t.daemon = True
            t.start()


    def handle_handshake(self, client_connection):
        client_connection.send('[01]'.encode())
        credentials = client_connection.recv(1024).decode().strip()

        if not CREDENTIALS_MASK.match(credentials):
            client_connection.send('[30]'.encode())
            client_connection.close()
            return

        code, text = utils.parse_message(credentials)
        user_name, password = text.split(':')
        
        if code == '10':
            if self.handle_login(user_name, password):
                print(f'[*] {user_name} logged in')
                client_connection.send('[02]'.encode())
                self.active_clients.append((client_connection, user_name))
                self.messaging_loop(client_connection, user_name)
            else:
                client_connection.send('[31]'.encode())
                client_connection.close()
                return
        elif code == '11':
            if self.handle_register(user_name, password):
                print(f'[*] {user_name} registered')
                client_connection.send('[02]'.encode())
                self.active_clients.append((client_connection, user_name))
                self.messaging_loop(client_connection, user_name)
            else:
                client_connection.send('[32]'.encode())
                client_connection.close()
                return


    def handle_login(self, user_name, password):
        return user_name in self.stored_users.keys() and password == self.stored_users[user_name]


    def handle_register(self, user_name, password):
        if user_name in self.stored_users.keys():
            return False
        else:
            self.stored_users[user_name] = password
            return True


    def messaging_loop(self, client_connection, client_name):
        client_connection.send(f'[20]Welcome to {self.name}!'.encode())
        while True:
            try:
                message = client_connection.recv(1024).decode().strip()
                if not MESSAGE_MASK.match(message):
                    client_connection.send('[30]'.encode())
                    client_connection.close()
                    raise Exception

                code, text = utils.parse_message(message)
                if code == '21':
                    text = f'[22]{datetime.now().hour}:{datetime.now().minute} <{client_name}> {text}'

                    for client in self.active_clients:
                        client[0].send(text.encode())

            except:
                text = f'[22]{datetime.now().hour}:{datetime.now().minute} <{client_name}> has left the chat'
                for client in self.active_clients:
                    client[0].send(text.encode())
                    if client[0] is client_connection:
                        self.active_clients.remove(client)
                        client[0].close()


server = Server('127.0.0.1', 7777, 'pyzza')
server.server_loop()
