from socket import *
serverName = 'localhost'
serverPort = 4000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
clientSocket.send("This is a test")
modifiedSentence = clientSocket.recv(1024)
print "From Server: ", modifiedSentence
clientSocket.close()
