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
        self.recvLength = 1024
        self.threads = []
        

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
                    running = handleCommInput(message, self.sock)

                #check if from stdin input
                elif conn == sys.stdin:
                    stdInput = sys.stdin.readline()
                    stdInput = stdInput.strip() #remove leading and trailing white space
                    running = handleTermInput(stdInput, self.sock)

        #quit requested
        print "Ending connection. Goodbye."
        self.sock.close()
        sys.exit()


"""FUNCTIONS"""
#handle any terminal commands
def handleTermInput(string, serverSock):
    if string == "quit": #quit
        serverSock.send("Bye")
        str = serverSock.recv(1024)
        if str != "Bye":
            print "Incorrect message from server: " + str
        serverSock.send("Bye")
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
        if len(tmp) == 2:
            print "Please finish quotation marks"
        else:
            serverSock.send(tmp[1])
    else:
        print string + " is not a valid command.  Type help for assistance."
    return True

#handle any communication from the socket; message to send back to client is returned
def handleCommInput(string, serverSock):
    if string == "Bye":
        serverSock.send("Bye")
        str = serverSock.recv(1024)
        if str != "Bye":
            print "Incorrect message from server: " + str
        return False
    print "From Server: " + string
    return True #keep running

"""CODE STARTS HERE"""
thread = commThread("127.0.0.1", 4001)
thread.startSocket()
thread.start()
