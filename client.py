import socket
import sys
import utils


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


    def handle_handshake(self):
        hello = self.socket.recv(54).decode()
        code, _ = utils.parse_message(hello)
        if code == '00':
            print('[*] Connected to server')
        else:
            print('[!] Connection failed')
            self.socket.close()
            sys.exit(1)

        login = self.socket.recv(54).decode()
        code, _ = utils.parse_message(login)
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

        self.socket.send(f'{header}{username}:{password}'.encode())
        authentication = self.socket.recv(54).decode()
        code, _ = utils.parse_message(authentication)

        if code == '02':
            print('[*] Successfully authenticated')
            return True

        if code == '30':
            print('[!] Server refused to connect')
        elif code == '31':
            print('[!] Username or password wrong')
        elif code == '32':
            print('[!] Username already in use')
        else:
            print('[!] Authentication error ocurred')

        self.socket.close()
        sys.exit(1)



client = Client()
client.handle_handshake()

