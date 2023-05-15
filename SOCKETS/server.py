import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 1729))
server_socket.listen(1)

print("Server is listening for connections...")

client_socket, address = server_socket.accept()
print(f"Connection established from: {address}")

while True:
    data = client_socket.recv(1024)
    if not data:
        break
    print(f"Received data: {data.decode()}")

    response = "Message received"
    client_socket.send(response.encode())

client_socket.close()
server_socket.close()
