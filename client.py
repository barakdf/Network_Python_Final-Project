import socket
import threading
import tkinter
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

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                print("mes=====", message)
                print(f"{self.id} has disconnected")
                if message == "connect":
                    self.sock.send(self.id.encode('utf-8'))
                elif message == f"{self.id} has disconnected\n":
                    print("disconnected")
                    self.stop()
                    break
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
