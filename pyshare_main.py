import socket
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Progressbar, Style
from threading import Thread
import requests

BUFFER_SIZE = 1024

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def send_file():
    host = entry.get()
    if not host:
        return

    filename = askopenfilename()
    if not filename:
        return

    port = 5001
    filesize = os.path.getsize(filename)
    s = socket.socket()
    status_label.config(text="Trying to connect...")
    s.connect((host, port))
    status_label.config(text="Connected.")
    s.send(f"{filename}<SEPARATOR>{filesize}".encode())

    progress['maximum'] = filesize
    sent = 0

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            sent += len(bytes_read)
            progress['value'] = sent
    s.close()
    status_label.config(text="File sent.")

def receive_file():
    host = "0.0.0.0"
    port = 5001

    s = socket.socket()
    s.bind((host, port))
    s.listen(5)

    status_label.config(text="Listening for incoming connections...")
    conn, addr = s.accept()
    status_label.config(text=f"Accepted connection from {addr[0]}")

    data = conn.recv(BUFFER_SIZE)
    filename, filesize = data.decode().split("<SEPARATOR>")
    filename = os.path.basename(filename)
    filesize = int(filesize)

    filename = asksaveasfilename(initialfile=filename)
    if not filename:
        return

    progress['maximum'] = filesize
    received = 0

    with open(filename, "wb") as f:
        while True:
            bytes_read = conn.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            received += len(bytes_read)
            progress['value'] = received
    conn.close()
    s.close()
    status_label.config(text="File received.")

root = tk.Tk()
root.geometry('800x400')
root.configure(bg='#1e3c72')

style = Style()
style.configure("TProgressbar", thickness=25, troughcolor ='#1e3c72', background='white', )

label = tk.Label(root, text="Enter Receivers IP address", bg='#1e3c72', fg='white', font=("Helvetica", 16))
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=10)

ip_label = tk.Label(root, text=f"Your IP: {get_ip_address()}", bg='#1e3c72', fg='white', font=("Helvetica", 16))
ip_label.pack(pady=10)

send_button = tk.Button(root, text="Send file", command=lambda: Thread(target=send_file).start(), bg='white', fg='#1e3c72')
send_button.pack(pady=10)

receive_button = tk.Button(root, text="Receive file", command=lambda: Thread(target=receive_file).start(), bg='white', fg='#1e3c72')
receive_button.pack(pady=10)

progress = Progressbar(root, length=500, style="TProgressbar")
progress.pack(pady=10)

status_label = tk.Label(root, text="", bg='#1e3c72', fg='white', font=("Helvetica", 16))
status_label.pack(pady=10)

root.mainloop()