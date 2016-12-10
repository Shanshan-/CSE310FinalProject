import threading
import select
from socket import *
import socket
import sys

"""CLASSES"""
class commThread (threading.Thread):
    def __init__(self, servername, port):
        threading.Thread.__init__(self)
        self.server = servername
        self.port = port
        self.sock = None
        self.threads = []
        self.recvLength = 1024

    #open up the client socket to communicate with server
    def startSocket(self):
        try:
            self.sock = socket.socket(AF_INET,SOCK_STREAM)
            self.sock.connect((self.server, self.port))
            print "Connection to ", self.server, " on port ", self.port, " successful"
        except socket.error, (value,message):
            if self.sock:
                self.sock.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        print "The client is ready to send"
        mask = [self.sock, sys.stdin] # create a mask for multiplexing

        running = True
        while running:
            inputready, outputready, exceptready = select.select(mask, [], []) # begin multiplexing on socket and stdin
            for conn in inputready:

                #check if from server socket connection
                if conn == self.sock:
                    message = self.sock.recv(self.recvLength)
                    response, running = handleCommInput(message)
                    if response != "":
                        self.sock.send(response)

                #check if from stdin input
                elif conn == sys.stdin:
                    stdInput = sys.stdin.readline()
                    stdInput = stdInput.strip() #remove leading and trailing white space
                    running = handleTermInput(stdInput, self.sock)

        #quit requested
        self.sock.close()


"""FUNCTIONS"""
#handle any terminal commands
def handleTermInput(string, commSock):
    if string == "quit": #quit
        return False
    elif string == "help": #help
        print ("Available commands:\n"
                "  help\t\tBring up this menu\n"
                "  quit\t\tQuits the program\n"
                "  send \"string\"\tSends the contents of \"string\" to the server for processing\n")
    elif "send" in string: #send message to server
        tmp = string.split("\"")
        if len(tmp) == 1:
            print "Please enclose the message to be sent in quotation marks"
        else:
            commSock.send(tmp[1])
    else:
        print string + " is not a valid command.  Type help for assistance."
    return True

#handle any communication from the socket; message to send back to client is returned
def handleCommInput(string):
    if string == "server Shutdown":
        return "", False
    print "From Server: " + string
    return "", True

"""CODE STARTS HERE"""
thread = commThread("127.0.0.1", 4001)
thread.startSocket()
thread.start()