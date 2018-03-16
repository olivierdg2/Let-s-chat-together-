import socket
import struct
import sys
import threading

class PeertoPeer():

    def __init__(self, host=socket.gethostname(), port=5000, pseudo='Client'):
        self.__socket = socket.socket()
        self.__socket.bind((host, port))
        self.__pseudos=pseudo

        print('Écoute sur {}:{}'.format(host, port))

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/client': self._client
        }
        self.__running = True
        self.__address = None
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()

            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution.")
            else:
                print('Commande inconnue:', command)

    def _exit(self):
        self._send("/exit")
        self.__running = False
        self.__address = None
        self.__socket.close()

    def _quit(self):
        self._send("/quit")
        self.__address = None

    def _join(self, param):
        self.__pseudos=input("Veuillez choisir votre pseudo: ")
        pseudo=str('-' + self.__pseudos + '--->').encode()
        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__address = (tokens[0], int(tokens[1]))
                self.__socket.connect(self.__address)
                print('Connecté à {}:{}'.format(*self.__address))
            except OSError:
                print("Erreur lors de la connexion.")
        sent = self.__socket.send(pseudo)
    def _send(self, param):
        if self.__address is not None:
            try:
                message = param.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__socket.send(message[totalsent:])
                    totalsent += sent
                print(self.__socket.recv(1024).decode())
            except OSError:
                print('Erreur lors de la réception du message.')

    def _receive(self):
        while self.__running:
            try:
                data = self.__socket.recv(1024)
                print(data.decode())
            except socket.timeout:
                pass
            except OSError:
                return

    def _client(self):
        print(self.__address)

if _name_ == '_main_':

    if len(sys.argv) == 3:
        PeertoPeer(sys.argv[1], int(sys.argv[2])).run()
    else:
        PeertoPeer().run()