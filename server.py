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
        print "The server is ready to receive connections"
        mask = [self.sock, sys.stdin] # create a mask for multiplexing

        running = True
        while running:
            inputready, outputready, exceptready = select.select(mask, [], []) # begin multiplexing on socket and stdin
            for conn in inputready:

                #check if from the server socket connection
                if conn == self.sock:
                    connectionSocket, addr = self.sock.accept()
                    safeWrite("Connection request from " + str(addr))
                    _thread = commThread(connectionSocket, addr)
                    self.threads.append(_thread)
                    _thread.start()

                #check if from stdin input
                elif conn == sys.stdin:
                    stdInput = sys.stdin.readline()
                    stdInput = stdInput.strip() #remove leading and trailing white space
                    running = handleTermInput(stdInput)

        #quit has been called; close the server
        print "Closing down the server..."
        self.sock.close()
        for t in self.threads:
            try:
                t.shutdown()
            except:
                pass
            t.join()
        sys.exit()

class commThread (threading.Thread):
    def __init__(self, connectionSocket, addr):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.addr = addr

    def run(self):
        safeWrite("Connection to " + str(self.addr) + " successful")
        running = True
        while running:
            message = self.connectionSocket.recv(1024)
            running = handleCommInput(message, self.connectionSocket, str(self.addr))
        self.shutdown()
        return

    def shutdown(self):
        safeWrite("Closing connection from " + str(self.addr))
        self.connectionSocket.send("Bye")
        string = self.connectionSocket.recv(1024)
        if string != "Bye" and string != "":
            safeWrite("Incorrect response from client: " + string)
        self.connectionSocket.send("Bye")
        self.connectionSocket.close()
        return

"""FUNCTIONS"""
#thread-locked writing function (use when printing to the terminal)
def safeWrite(str):
    #TODO: check if needed for terminal i/o
    writeLock.acquire()
    print str
    writeLock.release()
    return

#handle any terminal commands
def handleTermInput(string):
    #if user requests to quit
    if string == "quit":
        return False
    elif string == "help":
        print ("Available commands:\n"
                "  help\t\tBring up this menu\n"
                "  quit\t\tQuits the program\n")
    else:
        print string + " is not a valid command.  Type help for assistance."
    return True

#handle any communication from the socket; message to send back to client is returned
def handleCommInput(string, clientSock, addr):
    safeWrite("Received message \"" + string + "\" from " + addr)
    if string == "Bye":
        return False
    else:
        response = string + " - Testing"
        clientSock.send(response)
        safeWrite("Sending message \"" + response + "\" to " + addr)
    return True

"""CODE STARTS HERE"""
thread = listenThread("127.0.0.1", 4001)
thread.startSocket()
writeLock = threading.Lock()
thread.start()
thread.join()
