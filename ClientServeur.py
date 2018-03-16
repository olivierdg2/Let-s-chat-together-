import socket
import struct
import sys
import threading

SERVERADDRESS = (socket.gethostname(), 6000)


class ClientServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__server = socket.socket()
        self.ConnectedClients = {}
        self.commands = {
            '/quitter': self._quitter,
            '/clients': self._clients,
            '/help': self._help
        }

        try:
            self.__server.bind(SERVERADDRESS)
        except socket.error:
            print('Connexion échouée {}'.format(socket.error))

        self.__server.listen()

    def run(self):


        print( "En écoute sur {}".format(SERVERADDRESS))

        while True:
            client, address = self.__server.accept()
            self.ConnectedClients[client]=address
            try:
                threading.Thread(target=self._handle, args=(client, address)).start()
            except OSError:
                print('Erreur lors du traitement de la requête du client.')

    def exit(self):
        self.__server.close()

    def _handle(self, client, address):

        print('Coordonnées du client: {};{}'.format(address[0], str(address[1])))

        self.ConnectedClients[address] = [client, ""]
        print('Il y a actuellement {} personnes connectées'.format((len(self.ConnectedClients)) / 2))

        Dico ={}

        while 1:

            data = str(client.recv(1024).decode())

            if data[0]=='-':   # '-' est le caractère indiquant qu'il faut ajouter le nouveau pseudo dans le dictionnaire
                Truedata = data.split('-')
                global pseudo
                pseudo = Truedata[1]
                Dico[address[0]] = pseudo  #Dans Dico[address[0]] est noté le psoeudo du client


            elif data[0] == "/":

                line = data.rstrip() + ' '
                command = line[:line.index(' ')]
                param = line[line.index(' ')+1:].rstrip()
                params = [param, address]
                if command in self.commands:
                    try:
                        self.commands[command](client) if param == '' else self.commands[command](params)
                    except:
                        print("Erreur lors de l'exécution de la commande")

                else:
                    print('Commande inconnue', command)
            else:

                if self.ConnectedClients[address][1] != "":
                    print("<{}> {}".format(Dico[address[0]],data)) #On affiche le pseudo au lieu de l'adresse IP
                    client.send(("<{}> {}".format(Dico[address[0]],data)).encode())

                else:
                    print("<{}> {}".format(Dico[address[0]],data))
                    client.send(("<{}> {}".format(Dico[address[0]], data)).encode())

        client.close()

    def _quitter(self, client):
        for ConnectedClients in self.ConnectedClients:
            if self.ConnectedClients[ConnectedClients][0] == client:
                del self.ConnectedClients[ConnectedClients]
                print("Client déconnecté")
                client.close()

    def _clients(self, client):

        client.send(('Voici la liste des clients: \nPseudo:{} | Adresse IP:{} | Port:{}'.format(pseudo,self.ConnectedClients[client][0],self.ConnectedClients[client][1])).encode())

    def _help(self, client):

        client.send('/clients ====> Donne la liste des clients\n /quitter ====> Ferme la connexion avec le serveur'.encode())
        

if _name_ == '_main_':

    ClientServer().run()
