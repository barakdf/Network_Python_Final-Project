import socket
import threading
import tkinter
from time import sleep
from tkinter import simpledialog
import tkinter.scrolledtext

HOST = '127.0.0.1'
PORT = 55000


class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        lobby = tkinter.Tk()
        lobby.withdraw()

        self.id = simpledialog.askstring("ID", "Please choose name", parent=lobby)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightblue")

        self.chat_label = tkinter.Label(self.win, text="chat:", bg="lightgray")
        self.chat_label.config(font=("Ariel", 14))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.message_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.message_label.config(font=("Ariel", 14))
        self.message_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Ariel", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.id}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def download(self, file):
        transfer_port = 55001
        transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("ready ro receive")

        with open(f"downloaded_file_{file}", 'w') as f:

            packet_count = 0
            transfer_sock.bind((HOST, transfer_port))
            sleep(1)

            while True:

                try:
                    (packet, server_ads) = transfer_sock.recvfrom(1024)
                    # packet = packet.decode("utf-8")
                except Exception:
                    print("Error accrued while receiving file")
                    continue

                packet_message = packet.decode("utf-8").split('#')

                seq_num = packet_message[0]
                file_size = int(packet_message[1])
                packet_len = int(packet_message[2])
                packet_data = packet_message[3]
                print("data-len ", len(packet_data))
                print("Packet-len ", packet_len)
                print("file-size ", file_size)
                print(seq_num)

                progress = 0

                if int(seq_num) == packet_count:
                    print("Got here")
                    packet_count += 1

                    f.write(packet_data)

                    progress += packet_len

                    percentage_progress = (progress / file_size) * 100
                    print(percentage_progress)

                    ACK = str(seq_num).encode("utf-8")
                    transfer_sock.sendto(ACK, server_ads)

                else:
                    last_packet = str(packet_count).encode("utf-8")
                    transfer_sock.sendto(last_packet, server_ads)

                if packet_len < 500 or packet_len == file_size:
                    done = "done".encode("utf-8")
                    transfer_sock.sendto(done, server_ads)
                    break

            transfer_sock.close()
            print("Download Complete")

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                print(message)
                if message == "connect":
                    self.sock.send(self.id.encode('utf-8'))
                elif message == f"{self.id} has disconnected\n":
                    print("disconnected")
                    self.stop()
                    break
                elif message[:17] == "starting download":
                    file_name = message[19:-1]
                    print(file_name)
                    print("OK")
                    self.sock.send("OK".encode('utf-8'))
                    download_thread = threading.Thread(target=self.download, args=(file_name,))
                    download_thread.start()
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')


            except ConnectionAbortedError:
                self.stop()
                break
            except:
                print("Error")
                self.stop()
                break


client = Client(HOST, PORT)
