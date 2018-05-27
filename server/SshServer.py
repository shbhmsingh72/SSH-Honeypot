import socket
import paramiko
import threading
import sys
import traceback
import time
import select
import os
import json
import config
from log import Out

def exec_service(hacker_session, docker_session, cmd):

    docker_session.exec_command(cmd)   

    try:
        while True:
            if hacker_session.recv_ready():
                text = hacker_session.recv(1024)
                print str(text.encode("hex"))
                docker_session.sendall(text)

            if docker_session.recv_ready():
                text = docker_session.recv(1024)
                hacker_session.sendall(text)

            if docker_session.recv_stderr_ready():
                text = docker_session.recv_stderr(1024)
                hacker_session.sendall_stderr(text)

            if docker_session.eof_received:
                hacker_session.shutdown_write()
                hacker_session.send_exit_status(0)

            if hacker_session.eof_received:
                docker_session.shutdown_write()
                docker_session.send_exit_status(0)

            if hacker_session.eof_received or docker_session.eof_received:
                break

    except Exception, e:
        print e
    finally:
        docker_session.close()
        hacker_session.close()

def shell_service(hacker_session, docker_session , out):

    hacker_session.settimeout(3600)
    try:
        command = "";
        while True:
            if hacker_session.recv_ready():
                text = hacker_session.recv(1)
                if text !='\r' :
                    command = command + text                    
                else :
                    if command != "":
                        out.out(command)		
                    command= ""
		#f.write(text)		
                docker_session.sendall(text)                

            if docker_session.recv_ready():
                text = docker_session.recv(1024)	
                hacker_session.sendall(text)

            if docker_session.recv_stderr_ready():
                text = docker_session.recv_stderr(1024)
                hacker_session.sendall_stderr(text)

            if docker_session.eof_received:
                hacker_session.shutdown_write()
                hacker_session.send_exit_status(0)

            if hacker_session.eof_received:
                docker_session.shutdown_write()
                docker_session.send_exit_status(0)

            if docker_session.eof_received or hacker_session.eof_received:
                break

    except Exception, e:
        print e
    finally:
        hacker_session.close()
        docker_session.close()


def reverse_handler(*args):
    t = threading.Thread(target=reverse_handler2, args=(args))
    t.setDaemon(True)
    t.start()


def reverse_handler2(docker_channel, origin, destination, hacker_trans):
    try:
        hacker_channel = hacker_trans.open_forwarded_tcpip_channel(origin,
                                                               destination)
    except:
        docker_channel.close()
        return

    try:
        while True:
            r, w, x = select.select([hacker_channel, docker_channel], [], [])
            if hacker_channel in r:
                text = hacker_channel.recv(1024)
                docker_channel.send(text)

            if docker_channel in r:
                text = docker_channel.recv(1024)
                hacker_channel.send(text)

            if docker_channel.eof_received:
                hacker_channel.shutdown_write()
                hacker_channel.send_exit_status(0)

            if hacker_channel.eof_received:
                docker_channel.shutdown_write()
                docker_channel.send_exit_status(0)

            if docker_channel.eof_received and hacker_channel.eof_received:
                break

    except Exception as e:
        print e
    finally:
        hacker_channel.close()
        docker_channel.close()



def direct_service(hacker_channel_id, hacker_trans, docker_channel):

    for i in range(10):
        if hacker_trans._channels.get(hacker_channel_id):
            break
        time.sleep(1)
    else:
        # print 'direct wait for channel timeout'
        docker_channel.close()
        return

    hacker_channel = hacker_trans._channels.get(hacker_channel_id)

    try:
        while True:

            r, w, x = select.select([hacker_channel, docker_channel], [], [])
            if hacker_channel in r:
                text = hacker_channel.recv(1024)
                docker_channel.send(text)

            if docker_channel in r:
                text = docker_channel.recv(1024)
                hacker_channel.send(text)

            if docker_channel.eof_received:
                hacker_channel.shutdown_write()
                hacker_channel.send_exit_status(0)

            if hacker_channel.eof_received:
                docker_channel.shutdown_write()
                docker_channel.send_exit_status(0)

            if docker_channel.eof_received and hacker_channel.eof_received:
                break

    except Exception, e:
        print e
    finally:
        hacker_channel.close()
        docker_channel.close()




class SshServer (paramiko.ServerInterface):

    def __init__(self, transport):

        paramiko.util.log_to_file("paramiko.log")
        self.attacker_trans = transport
        self.attacker_ip, self.attacker_port = transport.getpeername()
	    
        self.docker_ip = config.cfg.get("docker","dockerip")
        self.docker_port = config.cfg.getint("docker","dockerport")
	self.docker_ip = '172.27.20.2'
	self.docker_port = 22
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        sock.connect((self.docker_ip, self.docker_port))
	print 'attacker reached with ip : '+self.attacker_ip
        self.out = Out(self.attacker_ip)
        self.docker_trans = paramiko.Transport(sock)
        self.docker_trans.start_client()
	if config.cfg.get("password" , "enable") == 'true':
		self.pass_file = open ('log/password.txt','a')     
	else: 
		self.pass_file = None  
        self.chain = {}


    def get_allowed_auths(self, username):
        return 'password'

    def check_auth_password(self, username, password):        
        try:
	    if self.pass_file is not None:
		self.pass_file.write(self.attacker_ip+ ': '+username+' '+password+'\n')
            self.docker_trans.auth_password(username=username, password=password)
        except Exception:
            return paramiko.AUTH_FAILED
        else:
	    self.pass_file.close()
            return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED

    def check_global_request(self, kind, msg):
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        try:
            docker_channel = self.docker_trans.open_session()
            docker_channel.get_pty()
            self.chain[channel.get_id()] = docker_channel.get_id()
        except Exception:           
            return False
        else:
            return True

    def check_channel_shell_request(self, attacker_session):
        try:
            docker_id = self.chain[attacker_session.get_id()]
            docker_channel = self.docker_trans._channels.get(docker_id)
        except Exception as e:
	    #print "hello1"
	    print e
            docker_channel = self.docker_trans.open_session()
            docker_channel.get_pty()
            self.chain[attacker_session.get_id()] = docker_channel.get_id()

        try:
            docker_channel.invoke_shell()
            service_thread=threading.Thread(target=shell_service,args=(attacker_session,docker_channel, self.out))
	    service_thread.setDaemon(True)
            service_thread.start()

        except Exception as e:
	    #print "hello1"
	    print e            
            return False
        else:
            return True

    def check_channel_exec_request(self, hacker_session, command):
	
        try:
            docker_session = self.docker_trans.open_session()
            self.chain[hacker_session.get_id()] = docker_session.get_id()

            service_thread = threading.Thread(target=exec_service,args=(hacker_session,docker_session,command))
            service_thread.setDaemon(True)
            service_thread.start()
        except Exception:            
            return False
        else:
            return True

    # check for reverse forward channel
    def check_port_forward_request(self, address, port):
        def handler(chann, ori, dest):
            reverse_handler(chann, ori, dest, self.hacker_trans)

        flag = self.docker_trans.request_port_forward(address, port, handler=handler)
        return flag

    def check_channel_forward_agent_request(self, channel):       
        return False

    def check_channel_env_request(self, channel, name, value):
        try:
            docker_id = self.chain[channel.get_id()]
            docker_session = self.docker_trans._channels.get(docker_id)
            docker_session.set_environment_variable(name, value)
        except Exception:            
            return False
        else:
            return True

    def check_channel_direct_tcpip_request(self, chanid, origin, destination):
        try:
            docker_channel = self.docker_trans.open_channel('direct-tcpip', dest_addr=destination, src_addr=origin)
            self.chain[chanid] = docker_channel.get_id()

        except paramiko.ChannelException:            
            return paramiko.OPEN_FAILED_CONNECT_FAILED
        else:            
            service_thread = threading.Thread(target=direct_service,args=(chanid,self.attacker_trans,docker_channel))
            service_thread.setDaemon(True)
            service_thread.start()
            return paramiko.OPEN_SUCCEEDED
