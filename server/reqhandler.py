import config
import paramiko
from SshServer import SshServer

id_rsa = config.cfg.get("keys", "id_rsa")
id_dsa = config.cfg.get("keys", "id_dsa")

class Handler(object):
	def __init__(self , client , addr):
		self.transport = paramiko.Transport(client)
		rsakey = paramiko.RSAKey(filename=id_rsa)
		dsakey = paramiko.DSSKey(filename=id_dsa)
		self.transport.add_server_key(rsakey)
		self.transport.add_server_key(dsakey)
		

	def start_server(self):
		server = SshServer(transport = self.transport)
		try:
		        self.transport.start_server(server=server)
		except paramiko.SSHException as e:
			print e
		except Exception as e:
     			print e
			if server.pass_file is not None:
				server.pass_file.close()
			server.docker_trans.close()
     		try:
      			while True:
        			chann = self.transport.accept(60)            		
				if not self.transport._channels.values():
					if server.pass_file is not None:
						server.pass_file.close()
					break
		except Exception as e:
			print e
			if server.pass_file is not None:
				server.pass_file.close()
			server.docker_trans.close()
			
