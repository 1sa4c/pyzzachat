import socket
import threading
import re
import utils

MESSAGE_MASK = re.compile('\[\d\d\].*')
CREDENTIALS_MASK = re.compile('\[1\d\].{3,16}:.{3,16}')


class Server:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.clients = dict()

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
            return False

        code, text = utils.parse_message(credentials)
        user_name, password = text.split(':')
        
        if code == '10':
            if self.handle_login(user_name, password):
                print(f'[*] {user_name} logged in')
                client_connection.send('[02]'.encode())
            else:
                client_connection.send('[31]'.encode())
        elif code == '11':
            if self.handle_register(user_name, password):
                client_connection.send('[02]'.encode())
                print(f'[*] {user_name} registered')
            else:
                client_connection.send('[32]'.encode())


    def handle_login(self, user_name, password):
        return user_name in self.clients.keys() and password == self.clients[user_name]


    def handle_register(self, user_name, password):
        if user_name in self.clients.keys():
            return False
        else:
            self.clients[user_name] = password
            return True


server = Server('127.0.0.1', 7777, 'pyzza')
server.server_loop()
