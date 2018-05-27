#!/usr/bin/python
import paramiko
import config
from server import Server

ip = config.cfg.get("honeypot", "ip")
port = config.cfg.getint("honeypot", "port")

if __name__ == '__main__':
	Server(ip,port).listen()   
