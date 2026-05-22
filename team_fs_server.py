import socket
import team_filesystem
from concurrent.futures import ThreadPoolExecutor


def handle_conn(addr, conn, fs):
    name = conn.recv(1024).decode("utf-8")
    print(f"{name} is {addr}")
    while True:
        try:
            get = conn.recv(1024).decode("utf-8")
            get = get.strip().split(" ")
            if get[0] == "exit":
                print(f"{name}finished: {addr}")
                break
            command = ' '.join(get)
            info = fs.parse_command(command)
            print(f"{name}: {get}——{str(info)}")
            conn.send(str(info).encode("utf-8"))
        except ConnectionResetError:
            break
    conn.close()
    print(f"{addr} disconnected")


def main():
    fs = team_filesystem.FileManager()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 8080))
    s.listen(5)
    print("Waiting for connection...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        features = []
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            feature = executor.submit(handle_conn, addr, conn, fs)
            features.append(feature)


if __name__ == "__main__":
    main()
