import socket
import sys
import os
import threading
import utils


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = ''
        self.messages = list()

        try:
            server = self.get_server()
            self.socket.connect(server)
        except Exception as e:
            print(e)
            sys.exit(1)


    @staticmethod
    def get_server():
        ip = input('Server IP: ').strip()
        port = int(input('Server port: '))

        return (ip, port)


    def receive_message(self):
        buffer = self.socket.recv(3).decode()
        if not buffer:
            self.socket.close()
            sys.exit(1)

        bufsize = int(buffer)
        code, message = utils.parse_message(self.socket.recv(bufsize).decode())
        return code, message


    def send_message(self, message):
        encoded_message = message.encode()
        bufsize = len(encoded_message)
        encoded_bufsize = ('%03d' % bufsize).encode()

        if len(str(bufsize).encode()) > 3:
            print('[!] Message too long')
        else:
            self.socket.send(encoded_bufsize)
            self.socket.send(encoded_message)


    def handle_handshake(self):
        code, _ = self.receive_message()  # Server hello
        if code == '00':
            print('[*] Connected to server')
        else:
            print('[!] Connection failed')
            self.socket.close()
            sys.exit(1)

        code, _ = self.receive_message()  # Awaiting credentials
        if code == '01':
            print('[*] Starting authentication')
        else:
            print('[!] Server refuses to authenticate')
            self.socket.close()
            sys.exit(1)


        while True:
            option = input('[?] Do you want to login or register [l/r]')
            if option[0] in 'Ll':
                header = '[10]'
                break
            elif option[0] in 'Rr':
                header = '[11]'
                break
            else:
                print('[!] Choose a valid option')

        username = input('Username: ')
        password = input('Password: ')

        self.send_message(f'{header}{username}:{password}')
        code, _ = self.receive_message()  # Authentication

        if code == '02':
            print('[*] Successfully authenticated')
            self.name = username
            self.messaging_loop()

        if code == '30':
            print('[!] Server refused to connect')
        elif code == '31':
            print('[!] Username or password wrong')
        elif code == '32':
            print('[!] Username already in use')
        elif code == '33':
            print('[!] Database error')
        elif code == '34':
            print('[!] Message too long')
        else:
            print('[!] Authentication error ocurred')

        self.socket.close()
        sys.exit(1)


    def messaging_loop(self):
        t = threading.Thread(target=self.listen_for_messages)
        t.daemon = True
        t.start()

        while True:
            message = input('>>')
            if not t.is_alive():
                sys.exit(1)
            if not message:
                continue
            if message == '/quit':
                print('[*] Closing connection and quitting...')
                self.socket.close()
                sys.exit(0)
            else:
                self.send_message(f'[21]{message}')



    def listen_for_messages(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            for item in self.messages:
                print(item)

            code, text = self.receive_message()

            if code == '20' or code == '22':
                self.messages.append(text)
            else:
                print(f'[!] Something went wrong... disconnecting from server.')
                self.socket.close()
                return



client = Client()
client.handle_handshake()

