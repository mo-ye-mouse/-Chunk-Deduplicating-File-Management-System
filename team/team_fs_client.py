import socket

IP = "127.0.0.1"
PORT = 8080

name = input("Enter your name: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
s.send(name.encode())
while True:
    data = input("send: ")
    if not data:
        continue
    s.send(data.encode())
    datas = s.recv(1024).decode()
    if data == "exit":
        s.close()
        break
    if datas == "True":
        continue
    print("server: " + datas)
