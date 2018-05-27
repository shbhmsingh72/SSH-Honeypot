#!/usr/bin/env python
import logging
import threading
import config

class Out:
	def __init__(self,attacker_ip):
		self.attacker_ip = str(attacker_ip)
		self.logger = logging.getLogger(self.attacker_ip)
		self.logger.setLevel(logging.INFO)
		l_file = config.cfg.get("log","file")
		self.fh = logging.FileHandler(l_file+self.attacker_ip)
		self.fh.setLevel(logging.INFO)
		self.formatter=  logging.Formatter('%(asctime)s - '+ self.attacker_ip +' : %(message)s')
		self.fh.setFormatter(self.formatter)
		self.logger.addHandler(self.fh)

	def log(self, message):
		#print str(threading.current_thread().name)
		self.logger.info(message)

	def out(self, *args):
		thread = threading.Thread(target=self.log, args=args)		
		thread.setDaemon(True)
		#print thread.get_ident
		thread.start()		       
        
		
