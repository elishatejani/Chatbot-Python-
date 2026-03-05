import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

HOST = 'localhost'
PORT = 3000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


root = tk.Tk()
root.withdraw()

name = simpledialog.askstring("Login", "Enter your name:", parent=root)

if not name:
    exit()

root.destroy()


def send_name():
    while True:
        message = client.recv(1024).decode('utf-8')

        if "Enter your name" in message:
            client.send(name.encode('utf-8'))
            break


send_name()


window = tk.Tk()
window.title(f"Group Chat - {name}")
window.geometry("800x500")
window.configure(bg="black")


chat_frame = tk.Frame(window)
chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled')
chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

typing_label = tk.Label(chat_frame, text="", fg="gray")
typing_label.pack(anchor="w", padx=10)


user_frame = tk.Frame(window, width=150, bg="#1e1e1e")
user_frame.pack(side=tk.RIGHT, fill=tk.Y)

tk.Label(user_frame, text="Online Users", bg="#1e1e1e", fg="white").pack()

user_listbox = tk.Listbox(user_frame)
user_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


entry_frame = tk.Frame(chat_frame)
entry_frame.pack(fill=tk.X, padx=10, pady=10)

entry_field = tk.Entry(entry_frame)
entry_field.pack(side=tk.LEFT, fill=tk.X, expand=True)


def send_message():

    msg = entry_field.get()

    if msg.strip() == "":
        return

    message = f"{name}: {msg}"

    try:
        client.send(message.encode('utf-8'))
    except:
        pass

    entry_field.delete(0, tk.END)


send_button = tk.Button(entry_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

entry_field.bind("<Return>", lambda e: send_message())


def typing(event):
    client.send(f"TYPING:{name}".encode('utf-8'))


entry_field.bind("<KeyPress>", typing)


def update_users(user_string):

    user_listbox.delete(0, tk.END)

    users = user_string.split(",")

    for u in users:
        user_listbox.insert(tk.END, u)


def receive_messages():

    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message.startswith("USERLIST:"):
                users = message.replace("USERLIST:", "")
                update_users(users)
                continue

            if message.startswith("TYPING:"):
                typer = message.replace("TYPING:", "")

                if typer != name:
                    typing_label.config(text=f"{typer} is typing...")
                    window.after(1000, lambda: typing_label.config(text=""))

                continue

            chat_area.config(state='normal')
            chat_area.insert(tk.END, message + "\n")
            chat_area.config(state='disabled')
            chat_area.see(tk.END)

        except:
            break


thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

window.mainloop()
