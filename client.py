import socket
import threading
import tkinter
from time import sleep
from tkinter import simpledialog
import tkinter.scrolledtext
from tkinter.ttk import Progressbar

HOST = '127.0.0.1'
PORT = 55000
c_transfer_port = {55006: True, 55007: True, 55008: True, 55009: True, 55010: True}


class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        lobby = tkinter.Tk()
        lobby.withdraw()

        self.id = simpledialog.askstring("ID", "Please choose name", parent=lobby)

        self.gui_done = False
        self.running = True

        self.participant = ["All"]

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="#A9A9A9")

        self.disconnect_button = tkinter.Button(self.win, text="Disconnect", command=self.stop, width=10)
        self.disconnect_button.config(font=("Ariel", 14))
        # self.disconnect_button.pack(padx=20, pady=5)
        # self.disconnect_button.place(x=20, y=20)
        self.disconnect_button.grid(row=0, column=0)

        self.user_label = tkinter.Label(self.win, text=f"username: {self.id} | address: {HOST}")
        self.user_label.config(font=("Ariel", 14))
        self.user_label.grid(row=0, column=1)
        # self.user_label.pack()

        self.show_online = tkinter.Button(self.win, text="show online", command=self.ask_show_online, width=10)
        self.show_online.config(font=("Ariel", 14))
        # self.show_online.pack()
        # self.show_online.place(x=560, y=20)
        self.show_online.grid(row=0, column=2)

        self.server_files = tkinter.Button(self.win, text="Server Files", command=self.ask_server_files, width=10)
        self.server_files.config(font=("Ariel", 14))
        # self.server_files.place(x=560, y=65)
        self.server_files.grid(row=1, column=2)

        self.chat_label = tkinter.Label(self.win, text="chat:", bg="lightgray")
        self.chat_label.config(font=("Ariel", 14))
        # self.chat_label.place(x=50, y=20)
        # self.chat_label.pack(padx=20, pady=20)
        self.chat_label.grid(row=1, column=1)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="#FFFAFA")
        # self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')
        self.text_area.grid(row=2, column=1)

        self.message_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.message_label.config(font=("Ariel", 14))
        # self.message_label.pack(padx=20, pady=5)
        self.message_label.grid(row=3, column=1, pady=10)

        """ ----------- PRIVATE -----------"""

        self.message_to = tkinter.StringVar(self.win)
        self.message_to.set("All")

        self.private_message = tkinter.OptionMenu(self.win, self.message_to, "All", *self.participant)
        self.private_message.grid(row=4, column=0)

        self.input_area = tkinter.Text(self.win, height=3, bg="#FFFAFA")
        # self.input_area.pack(padx=20, pady=5)
        self.input_area.grid(row=4, column=1)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Ariel", 12))
        # self.send_button.pack(padx=20, pady=5)
        self.send_button.grid(row=5, column=1, pady=5)

        """ ----------- DOWNLOAD ----------"""

        self.download_button = tkinter.Button(self.win, text="Download", command=self.ask_for_download)
        self.download_button.config(font=("Ariel", 12))
        self.download_button.place(x=120, y=615)

        self.file_choose = tkinter.Text(self.win, width=10, height=2, bg="#FFFAFA")
        self.file_choose.grid(row=6, column=0, pady=5)

        self.proceed_button = tkinter.Button(self.win, text="Proceed", command=self.tranfer_to_download)
        self.proceed_button.config(font=("Ariel", 12))
        self.proceed_button.place(x=230, y=615)
        self.proceed_button["state"] = tkinter.DISABLED

        self.progress_bar = Progressbar(self.win, orient=tkinter.HORIZONTAL, length=200, mode='determinate')
        self.progress_bar.place(x=340, y=615)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        if self.message_to.get() == "All":
            message = f"{self.id}: {self.input_area.get('1.0', 'end')}"
        else:
            message = f"{self.id}: message-{self.message_to.get()}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def ask_show_online(self):
        self.sock.send("get_online_members".encode("utf-8"))

    def update_participants(self, text):
        updated_list = text.split(',')
        self.participant = updated_list

    def ask_server_files(self):
        self.sock.send("get_file_list".encode("utf-8"))

    def ask_for_download(self):
        self.progress_bar['value'] = 0
        ask_file = f"download_file:{self.file_choose.get('1.0', 'end')}"
        print("THE FILE", ask_file)
        self.sock.send(f"{self.id}: {ask_file}".encode("utf-8"))
        try:
            message = self.sock.recv(1024).decode('utf-8')
            if message[:17] == "starting download":
                self.proceed_button["state"] = tkinter.NORMAL
                self.download_button["state"] = tkinter.DISABLED
                self.text_area.config(state='normal')
                self.text_area.insert('end', "ready to proceed with download, chosen file: ")
                self.text_area.yview('end')
                self.text_area.config(state='disabled')
            else:
                self.text_area.config(state='normal')
                self.text_area.insert('end', message)
                self.text_area.yview('end')
                self.text_area.config(state='disabled')
        except:
            print("PROCCED BUTTON ERROR")

    def tranfer_to_download(self):
        file_name = f"{self.file_choose.get('1.0', 'end')}"
        self.sock.send("OK".encode('utf-8'))
        download_thread = threading.Thread(target=self.download, args=(file_name,))
        download_thread.start()

    def download(self, file: str):
        client_transfer_port = 0
        for p in c_transfer_port:
            if c_transfer_port[p]:
                client_transfer_port = p
                c_transfer_port[p] = False
                break
        transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("ready ro receive")
        file = file.replace("\n", "")

        with open(f"downloaded_file_{file}", 'w') as f:

            packet_count = 0
            transfer_sock.bind((HOST, client_transfer_port))

            while True:

                try:
                    (packet, server_ads) = transfer_sock.recvfrom(1024)
                    # packet = packet.decode("utf-8")
                except Exception:
                    print("Error accrued while receiving file")
                    c_transfer_port[client_transfer_port] = True
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
                    if file_size > 0:
                        percentage_progress = (progress / file_size) * 100
                        print(percentage_progress)
                        self.progress_bar['value'] += percentage_progress

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
            self.proceed_button["state"] = tkinter.DISABLED
            self.download_button["state"] = tkinter.NORMAL
            self.file_choose.delete('1.0', 'end')
            print("Download Complete")
            c_transfer_port[client_transfer_port] = True

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

                elif message == "Update_members":
                    print("got the message")
                    self.sock.send("to_list".encode("utf-8"))
                elif message == f"{self.id} has disconnected\n":
                    print("disconnected")
                    self.stop()
                    break
                elif message.split(':')[0] == "To_list":
                    print("participantos", self.participant)
                    print("list", message.split(':')[1])
                    self.update_participants(message.split(':')[1])
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
