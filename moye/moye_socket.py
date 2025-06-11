import socket

IP = "127.0.0.1"
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

while True:
    data = input("11.py: ")
    s.send(data.encode())
    data = s.recv(1024).decode()
    print("back from server: " + data)
    if data == "exit":
        s.close()
        break
