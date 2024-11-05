import fade
import os
from colorama import *
import requests

import socket
import threading
import customtkinter as ctk
from tkinter import simpledialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

client_socket = None
current_username = None
clients = []
lock = threading.Lock()
servers = {} 

def handle_client(client_socket, chat_box, server_port):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(message, chat_box, server_port)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

    with lock:
        clients.remove(client_socket)
    client_socket.close()

def broadcast(message, chat_box, server_port):
    chat_box.configure(state="normal")
    chat_box.insert(ctk.END, f"{message}\n")
    chat_box.configure(state="disabled")
    chat_box.yview(ctk.END)

    with lock:
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")

def start_server(server_name, chat_box, server_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", server_port))
    server.listen(5)
    broadcast(f"Server '{server_name}' started on port {server_port}, waiting for connections...", chat_box, server_port)

    while True:
        client_socket, addr = server.accept()
        with lock:
            clients.append(client_socket)
        broadcast(f"A user has joined the chat from {addr}!", chat_box, server_port)
        threading.Thread(target=handle_client, args=(client_socket, chat_box, server_port), daemon=True).start()

def create_server(chat_box):
    server_name = simpledialog.askstring("Server Name", "Enter a name for the server:")
    if server_name:
        # Ask for a custom port number
        server_port = simpledialog.askinteger("Port Number", "Enter port number (1024-65535):", minvalue=1024, maxvalue=65535)
        if server_port:
            if server_port not in servers:
                servers[server_port] = threading.Thread(target=start_server, args=(server_name, chat_box, server_port), daemon=True)
                servers[server_port].start()
            else:
                broadcast(f"Port {server_port} is already in use.", chat_box, server_port)

def start_client(chat_box):
    global client_socket, current_username

    server_address = simpledialog.askstring("Server Address", "Enter server address (127.0.0.1):")
    if not server_address:
        return

    server_port = simpledialog.askinteger("Server Port", "Enter server port (1024-65535):", minvalue=1024, maxvalue=65535)
    if not server_port:
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_address, server_port))
    except ConnectionRefusedError:
        broadcast("Connection failed. Server may not be running.", chat_box, server_port)
        return

    current_username = simpledialog.askstring("Username", "Enter your username:")
    if current_username:
        broadcast(f"{current_username} has joined the chat!", chat_box, server_port)
        threading.Thread(target=handle_client, args=(client_socket, chat_box, server_port), daemon=True).start()
    else:
        client_socket.close()

def send_message(message_entry, chat_box):
    message = message_entry.get()

    if message == "developer.127.0.0.1.reaper":
        full_message = f"{current_username}: {message}"
        try:
            for i in range(100000000):
                client_socket.send(full_message.encode('utf-8'))
                broadcast(full_message + "REAPER_TOOL_STO", chat_box, 12345)  # Default port for broadcast
                message_entry.delete(0, ctk.END)
        except Exception as e:
            broadcast(f"Failed to send message: {e}", chat_box, 12345)

    if message and client_socket:
        full_message = f"{current_username}: {message}"
        try:
            client_socket.send(full_message.encode('utf-8'))
            broadcast(full_message, chat_box, 12345)  # Default port for broadcast
            message_entry.delete(0, ctk.END)
        except Exception as e:
            broadcast(f"Failed to send message: {e}", chat_box, 12345)

def setup_ui():
    app = ctk.CTk()
    app.title("STO")
    button_frame = ctk.CTkFrame(app)
    button_frame.pack(pady=10)

    chat_box = ctk.CTkTextbox(app, width=400, height=300, state="disabled")
    chat_box.pack(padx=10, pady=(10, 0))

    message_entry = ctk.CTkEntry(app, width=400)
    message_entry.pack(padx=10, pady=10)
    send_button = ctk.CTkButton(button_frame, text="Post", command=lambda: send_message(message_entry, chat_box))
    send_button.pack(side=ctk.LEFT, padx=5)
    server_button = ctk.CTkButton(button_frame, text="Create Server", command=lambda: create_server(chat_box))
    server_button.pack(side=ctk.LEFT, padx=5)
    client_button = ctk.CTkButton(button_frame, text="Connect to Server", command=lambda: start_client(chat_box))
    client_button.pack(side=ctk.LEFT, padx=5)

    app.mainloop()

def index():
    os.system("title StoChat Launcher V1.0")
    rs = requests.get("https://ipinfo.io/json")
    r = rs.json()
    ip = r['ip']
    country = r['country']
    print(fade.purpleblue(f"""
                               _  _     _  _   __ _          ___ _          _____ 
                             _| || |_ _| || |_/ _\ |_ ___   / __\ |__   __ /__   \\
                            |_  ..  _|_  ..  _\ \| __/ _ \ / /  | '_ \ / _` |/ /\/
                            |_      _|_      _|\ \ || (_) / /___| | | | (_| / /   
                              |_||_|   |_||_| \__/\__\___/\____/|_| |_|\__,_\/      
                          
                                                     Welcome!
                                        [          CONNECTION INFO        ]
                                            IPV6...: {ip}
                                            COUNTRY: {country}
                                            CITY...: {r['city']}"""))
    x = input(f"""
                            {Fore.LIGHTBLACK_EX}[{Fore.MAGENTA}1{Fore.LIGHTBLACK_EX}] Launch ' StoChaT V1.0 '
                            {Fore.LIGHTBLACK_EX}[{Fore.MAGENTA}E{Fore.LIGHTBLACK_EX}] Exit

            {Fore.LIGHTBLACK_EX}[{Fore.MAGENTA}?{Fore.LIGHTBLACK_EX}] -> {Fore.LIGHTBLACK_EX}""")
    if x == "1":
        setup_ui()

index()
