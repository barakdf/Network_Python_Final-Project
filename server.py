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
members: (socket,) = []
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
    for client in members:
        client.send(message)


""" functions between client and server only,
    this methods is for: getting chat info, change connectivity status etc """

def get_online_members():
    ids = [x for x in IDS]
    return ",".join(ids)

def get_file_list():
    return server_files




def disconnect(client):
    index = members.index(client)
    members.remove(client)
    client.close()
    IDS.pop(index)



def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{IDS[members.index(client)]} says {message}")
            readable_message = str(message)

            """ private messaging """
            if "message-" in readable_message:
                message_info = readable_message.split(":",2)
                addressee = message_info[1][9:]
                message_data = message_info[2][:-3]
                try:
                    addresse_index = IDS.index(addressee)
                    members[addresse_index].send(
                        f"*private from ({message_info[0][2:]})*: {message_data}\n".encode('utf-8'))
                    client.send(
                        f"*private to ({addressee})* {message_info[0][2:]}: {message_data}\n".encode('utf-8'))
                except:
                    client.send(f"could not find the specific client\n".encode('utf-8'))

            # """ getting online members list """
            elif "get_online_members" in readable_message:
                client.send(f"online members: {get_online_members()}\n".encode('utf-8'))

            # """ getting list of server files """
            elif "get_file_list" in readable_message:
                print(server_files)
                client.send(f"server files: {server_files}\n".encode('utf-8'))

            elif "disconnect" in readable_message:
                print(f"{IDS[members.index(client)]} has disconnected")
                 # client.send(f"{nicknames[clients.index(client)]} has disconnected".encode('utf-8'))
                broadcast(f"{IDS[members.index(client)]} has disconnected\n".encode('utf-8'))
                disconnect(client)
                break

            else:
                broadcast(message)

        except:
            disconnect(client)
            break











def server_lobby():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        """ 
            first connection with chat-server, 
            send to client side key word "connect" to register with ID
        """
        client.send(f"connect".encode('utf-8'))
        client_id = client.recv(1024).decode('utf-8')

        """ adding the new member """
        IDS.append(client_id)
        members.append(client)

        """ finish connectivity steps """
        print(f"ID of the member is {client_id}")
        broadcast(f"{client_id} has joined the chat")
        client.send("successfully connected to the server".encode('utf-8'))

        """ opening a communication thread for the client """
        client_thread = threading.Thread(target=, args=(client,))
        client_thread.start()

print("server running")
server_lobby()