import bluetooth


import bluetooth

serverMACAddress = '00:1a:7d:Da:71:0a'
port = 5
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.connect((serverMACAddress, port))
while True:
    text = input() # Note change to the old (Python 2) raw_input
    if text == "quit":
        break
    s.send(text)
sock.close()
