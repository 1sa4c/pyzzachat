import socket
import threading
import re
import utils
from datetime import datetime
from database import operations

MESSAGE_MASK = re.compile('\[\d\d\].*')
CREDENTIALS_MASK = re.compile('.{3,16}:.{3,16}')


class Server:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.active_clients = list()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        print(f'[*] Listening on {self.ip}:{self.port}')


    @staticmethod
    def receive_message(client_connection):
        buffer = client_connection.recv(3).decode()
        if not buffer:
            return None, None

        bufsize = int(buffer)
        message = client_connection.recv(bufsize).decode().strip()

        if not MESSAGE_MASK.match(message):
            return '30', None

        code, text = utils.parse_message(message)
        return code, text


    @staticmethod
    def send_message(client_connection, message):
        encoded_message = message.encode()
        bufsize = len(encoded_message)
        encoded_bufsize = ('%03d' % bufsize).encode()

        if len(str(bufsize).encode()) > 3:
            client_connection.send('004[34]'.encode())
            pass
        else:
            client_connection.send(encoded_bufsize)
            client_connection.send(encoded_message)
   

    def server_loop(self):
        while True:
            client_connection, client_address = self.socket.accept()
            print(f'[*] Incoming connection from {client_address[0]}:{client_address[1]}')
            self.send_message(client_connection, '[00]')

            t = threading.Thread(target=self.handle_handshake, args=(client_connection,))
            t.daemon = True
            t.start()


    def handle_handshake(self, client_connection):
        self.send_message(client_connection, '[01]')
        code, credentials = self.receive_message(client_connection)

        if code == '30' or not CREDENTIALS_MASK.match(credentials):
            client_connection.send('[30]'.encode())
            client_connection.close()
            return

        user_name, password = credentials.split(':')
        
        if code == '10':
            if self.handle_login(user_name, password, client_connection):
                self.messaging_loop(client_connection, user_name)
            return
        elif code == '11':
            if self.handle_register(user_name, password, client_connection):
                self.messaging_loop(client_connection, user_name)
            return


    def handle_login(self, user_name, password, client_connection):
        try:
            user = operations.get_user(user_name)
            if user and utils.verify_password(user[1], password):
                print(f'[*] {user_name} logged in')
                self.send_message(client_connection, '[02]')
                self.active_clients.append((client_connection, user_name))
                return True
            else:
                self.send_message(client_connection, '[31]')
                return False
        except:
            self.send_message(client_connection, '[33]')
            return False


    def handle_register(self, user_name, password, client_connection):
        try:
            if operations.get_user(user_name):
                self.send_message(client_connection, '[32]')
                return False

            hashed_password = utils.hash_password(password)
            operations.create_user(user_name, hashed_password)
            print(f'[*] {user_name} registered')

            self.send_message(client_connection, '[02]')
            self.active_clients.append((client_connection, user_name))
            return True
        except:
            self.send_message(client_connection, '[33]')
            return False


    def messaging_loop(self, client_connection, client_name):
        self.send_message(client_connection, f'[20]Welcome to {self.name}!')
        self.broadcast_message(f'[22]{datetime.now().hour}:{datetime.now().minute} <{self.name}> {client_name} has entered the chat')
        while True:
            code, text = self.receive_message(client_connection)
            if not text:
                if code == '30':
                    self.send_message(client_connection, '[30]')
                self.disconnect_client((client_connection, client_name))
                return

            else:
                if code == '21':
                    text = f'[22]{datetime.now().hour}:{datetime.now().minute} <{client_name}> {text}'
                    self.broadcast_message(text)


    def disconnect_client(self, client):
        client[0].close()
        print(f'[*] {client[1]} left')
        self.active_clients.remove(client)
        text = f'[22]{datetime.now().hour}:{datetime.now().minute} <{self.name}> {client[1]} has left the chat'
        self.broadcast_message(text)


    def broadcast_message(self, message):
        for client in self.active_clients:
            try:
                self.send_message(client[0], message)
            except:
                self.disconnect_client(client)


server = Server('127.0.0.1', 7777, 'pyzza')
server.server_loop()
