from bluetooth import *

server_socket=BluetoothSocket( RFCOMM )

server_socket.bind(("", 3 ))
server_socket.listen(1)
print("gess")

client_socket, address = server_socket.accept()
print("EEEEE")

data = client_socket.recv(1024)

print("received", data)

client_socket.close()
server_socket.close()
