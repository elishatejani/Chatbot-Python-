import socket
import threading
import os

HOST = 'localhost'
PORT = 3000
history_file = 'chat_history.txt'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []

print("🔵 Server is running and listening...")


def load_history():
    if not os.path.exists(history_file):
        return ""
    with open(history_file, "r", encoding="utf-8") as f:
        return f.read()


def save_message(message):
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            pass


def send_user_list():
    user_list = ",".join(usernames)
    message = f"USERLIST:{user_list}"
    broadcast(message)


def handle_client(client):

    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message.startswith("TYPING:"):
                broadcast(message)
                continue

            if message:
                save_message(message)
                broadcast(message)

        except:
            if client in clients:
                index = clients.index(client)
                name = usernames[index]

                clients.remove(client)
                usernames.remove(name)

                leave_msg = f"🔴 {name} has left the chat."
                broadcast(leave_msg)
                save_message(leave_msg)

                send_user_list()

                client.close()

            break


def receive_connections():

    while True:
        client, address = server.accept()
        print(f"🟢 Connected with {str(address)}")

        client.send("Enter your name:".encode('utf-8'))
        name = client.recv(1024).decode('utf-8')

        usernames.append(name)
        clients.append(client)

        history = load_history()

        if history:
            client.send((history + "\n").encode('utf-8'))

        join_msg = f"🟢 {name} has joined the chat!"
        broadcast(join_msg)
        save_message(join_msg)

        send_user_list()

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


receive_connections()