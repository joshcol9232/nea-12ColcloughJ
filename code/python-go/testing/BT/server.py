import bluetooth

hostMACAddress = '00:1a:7d:da:71:0a' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 5
backlog = 1
size = 1024
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
    client, clientInfo = s.accept()
    while True:
        data = client.recv(size)
        if data:
            print(data)
            client.send(data) # Echo back to client
except bluetooth.btcommon.BluetoothError as e:
    print(e, "Closing socket")
    client.close()
    s.close()
    print("Lock Program")
