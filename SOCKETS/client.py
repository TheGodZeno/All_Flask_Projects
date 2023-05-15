import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 1729))

message = "Hello, server!"
client_socket.send(message.encode())

response = client_socket.recv(1024)
print(f"Response from server: {response.decode()}")

client_socket.close()
