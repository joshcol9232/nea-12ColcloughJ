import bluetooth



def runServer():
    hostMACAddress = '00:1a:7d:da:71:0a' # mac of bt adapter
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
                client.send(data) # Echo back to client
                return data
    except bluetooth.btcommon.BluetoothError as e:
        client.close()
        s.close()
        return True
