import threading
import select
from socket import *
import socket
import sys

"""CLASSES"""
class listenThread (threading.Thread):
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)
        self.host = hostname
        self.port = port
        self.sock = None
        self.threads = []

    #open up the server socket to listen for incoming connections
    def startSocket(self):
        try:
            self.sock = socket.socket(AF_INET,SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
        except socket.error, (value,message):
            if self.sock:
                self.sock.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        print "The server is ready to receive"
        mask = [self.sock, sys.stdin] # create a mask for multiplexing

        running = True
        while running:
            inputready, outputready, exceptready = select.select(mask, [], []) # begin multiplexing on socket and stdin
            for conn in inputready:

                #check if from server socket connection
                if conn == self.sock:
                    connectionSocket, addr = self.sock.accept()
                    _thread = commThread(connectionSocket, addr);
                    _thread.start()
                    self.threads.append(_thread)

                #check if from stdin input
                elif conn == sys.stdin:
                    stdInput = sys.stdin.readline()
                    stdInput = stdInput.strip() #remove leading and trailing white space
                    running = handleTermInput(stdInput)

        #quit has been called; close the server
        for t in self.threads:
            t.join();

class commThread (threading.Thread):
    def __init__(self, connectionSocket, addr):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.addr = addr

    def run(self):
        message = self.connectionSocket.recv(1024)
        response = handleCommInput(message)
        self.connectionSocket.send(response)
        self.connectionSocket.close()

"""FUNCTIONS"""
#handle any terminal commands
def handleTermInput(string):
    #if user requests to quit
    if string == "quit":
        return False

    else:
        print string
        return True

#handle any communication from the socket; message to send back to client is returned
def handleCommInput(string):
    response = string + "; Testing Testing 123"
    return response

"""CODE STARTS HERE"""
print "Type quit to exit server program"
thread = listenThread("127.0.0.1", 4000)
thread.startSocket()
thread.start()