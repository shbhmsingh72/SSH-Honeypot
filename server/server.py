import socket
import threading
import config
from reqhandler import Handler



class Server(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
	print 'starting server on ip '+self.ip+' port '+str(self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))

    def listen(self):
        self.sock.listen(60)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)	    
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        handler = Handler(client,address)
	handler.start_server()
