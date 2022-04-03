import socket
import threading
import time

HOST = '127.0.0.1'  # local host address.
PORT = 55000
transfer_port = {55006: True, 55007: True, 55008: True, 55009: True, 55010: True}

block = 500
N = 5

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

"""
    keep the clients in a data structure
    to manage the members in the chat
"""
members: (socket,) = []
IDS = []
server_files = ["One.txt", "Two.txt", "Three.txt"]

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


def send_file(c_address, transfer_sock, file, file_len, send_base, checked_ack):
    last_byte = ""
    for seq_num in range(checked_ack, send_base + N):
        if seq_num == int(file_len / block) + 1:
            packet = file[seq_num * block:]
        else:
            packet = file[seq_num * block: ((seq_num + 1) * block)]

        # print("SEQ", i)
        print(seq_num)
        packet_len = len(packet)

        full_packet = f"{seq_num}#{file_len}#{packet_len}#{packet}".encode("utf-8")
        transfer_sock.sendto(full_packet, c_address)
        last_byte = full_packet[-1]
        if seq_num == int(file_len / block) + 1:
            break
    return last_byte


""" Download server files from server to client using "fast reliable UDP",
    we implemented this method by "Go back N":
    in this function we will describe the server side (Sender)

    divide the requested file to packets. (each packet contain block of 500)
    using sliding window with size N (5)
    sending all the packets, and waiting for ACK from the client side,
    for each slide window we send we measure the time of it and initialize it as RTT.
    each ACK contain a seq_num that needs to be match the last seq_num of the last checked packet
    if we got wrong packet, or the time runs out (RTT) we send again the slide window starting from the last checked packet
    and increase the packet loss counter.
    each packet contain the details {seq_number, file length, packet length, packet}
    when we get ack on the last packet ("done" message by the client) we close the connection"""


def download_file(client, file_name):
    client.send("Nice Choice\n".encode("utf-8"))
    print("Nice")
    available_transfer_port = 0
    for p in transfer_port:
        if transfer_port[p]:
            available_transfer_port = p
            transfer_port[p] = False
            break

    c_address = (client.getsockname()[0], available_transfer_port)
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        with open(file_name, 'r') as f:
            file = f.read()
            client.sendto(f"PORT USE: {available_transfer_port}, file read successfully\n".encode("utf-8"), c_address)

    except Exception:
        f_error = "Error accrued while reading the file\n"
        print(f_error)
        client.sendto(f_error.encode("utf-8"), c_address)
        transfer_sock.close()

    time_measure = time.time()
    file_len = int(len(file))
    print(file_len)
    last_packet = int(file_len / block) + 1
    print("last packet", last_packet)
    send_base = 0

    pack_count = 0
    pack_loss = 0
    last_byte = ""
    checked_ack = send_base
    while send_base < last_packet:
        print("HERE")
        pack_count += 1
        RTT = time.time()
        last_byte = send_file(c_address, transfer_sock, file, file_len, send_base, checked_ack)

        RTT = time.time() - RTT

        while checked_ack < send_base + N - 1:
            delay = time.time()
            try:
                (ACK, c_address) = transfer_sock.recvfrom(1024)
            except:
                continue

            reply = ACK.decode('utf-8')
            print("ACKED =  ", reply)

            if reply == "done":
                if checked_ack == last_packet:
                    break

            elif int(reply) == checked_ack:
                print("CHECKED", checked_ack)
                checked_ack += 1

            elif (int(reply) > checked_ack) or (time.time() - delay > RTT):
                pack_loss += 1
                send_file(c_address, transfer_sock, file, file_len, send_base, checked_ack)

        print("send packet --> ", send_base)
        print("packet loss --> ", pack_loss)
        send_base = checked_ack

    transfer_sock.close()
    client.send(
        f"transfer complete, last byte: {last_byte}, last packet: {checked_ack}, packet_loss: {pack_loss}, PORT: {available_transfer_port}\n".encode(
            "utf-8"))
    transfer_port[available_transfer_port] = True


def disconnect(client):
    index = members.index(client)
    members.remove(client)
    client.close()
    IDS.pop(index)
    client.send(f"To_list:{get_online_members()}".encode('utf-8'))


def handle(client):
    global server_busy
    download_status = False
    new_client = True
    while True:
        try:
            message = client.recv(1024)
            print(f"{IDS[members.index(client)]} says {message}")
            readable_message = str(message)

            """ private messaging """
            if "message-" in readable_message:
                message_info = readable_message.split(":", 2)
                addressee = message_info[1][9:]
                message_data = message_info[2][:-3]
                try:
                    addresse_index = IDS.index(addressee)
                    members[addresse_index].send(
                        f"*private from ({message_info[0][2:]})*: {message_data}\n".encode('utf-8'))
                    client.send(
                        f"*private to ({addressee})* {message_info[0][2:]}: {message_data}\n".encode('utf-8'))
                except:
                    print(readable_message)
                    client.send(f"could not find the specific client\n".encode('utf-8'))



            # """ getting online members list """
            elif "get_online_members" in readable_message:
                client.send(f"online members: {get_online_members()}\n".encode('utf-8'))

            # """ get online list for private messaging """
            elif "to_list" in readable_message:
                client.send(f"To_list:{get_online_members()}".encode('utf-8'))

            # """ getting list of server files """
            elif "get_file_list" in readable_message:
                print(server_files)
                client.send(f"server files: {server_files}\n".encode('utf-8'))


            elif "download_file:" in readable_message:
                file_name = readable_message.split(":")[2][:-3]
                client.send(f"{file_name}---\n".encode("utf-8"))
                file_exist = False
                for f in server_files:
                    if f.__eq__(file_name):
                        file_exist = True
                        client.send(f"starting download: {file_name}\n".encode("utf-8"))
                        message = client.recv(1024)
                        if "OK" in str(message):
                            print("changed status")
                            download_status = True
                        if download_status:
                            print("Transferring")
                            UDP_SOCK = threading.Thread(target=download_file, args=(client, f))
                            UDP_SOCK.start()
                            # file_exist = False
                            server_busy = False

                if not file_exist:
                    error_msg = "the requested file does not exist in server\n"
                    client.send(error_msg.encode('utf-8'))




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
        client.send(f"To_list:{get_online_members()}".encode('utf-8'))

        """ finish connectivity steps """
        print(f"ID of the member is {client_id}")
        broadcast(f"{client_id} has joined the chat\n".encode('utf-8'))
        client.send("successfully connected to the server\n".encode('utf-8'))

        """ opening a communication thread for the client """
        client_thread = threading.Thread(target=handle, args=(client,))
        client_thread.start()


print("server running")
server_lobby()
