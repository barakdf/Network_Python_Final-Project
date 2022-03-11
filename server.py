import socket
import threading

HOST = '127.0.0.1'  # local host address.
PORT = 55000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

"""
    keep the clients in a data structure
    to manage the members in the chat
"""
clients: (socket,) = []
IDS = []
server_files = []

"""
 open 'receive function' to listen for connection ,
 also we need 'handle function' to keep this connection to the client 
 after client connect to the server...

 using threads to use multiple function at the same time
"""

""" broadcast function is to send the messages to all the members in chat """


def broadcast(message):
    for client in clients:
        client.send(message)


""" functions between client and server only,
    this methods is for: getting chat info, change connectivity status etc """

def get_online_members():
    ids = [x for x in IDS]
    return ",".join(ids)

def get_file_list():
    return server_files




def disconnect(client):
    index = clients.index(client)
    clients.remove(client)
    client.close()
    IDS.pop(index)




def server_lobby():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send(f"Welcome to chat".encode('utf-8'))
        
