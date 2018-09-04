from bluetooth import *
import time

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "80677070-a2f5-11e8-b568-0800200c9a66"

advertise_service( server_sock, "FileMateServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ],)

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

numbers = []
append = True

try:
    while True:
        data = client_sock.recv(1024)
        if len(data) == 0: break
        print("received [%s]" % data)
        if append:
            numbers.append(str(data, "utf-8"))
        if b"~" in data:    ##End of message
            append = False
            print(numbers)
            tempNums = "".join(numbers)
            print(tempNums, "join")
            time.sleep(1)
            tempNums = tempNums.replace("#", "")
            tempNums = tempNums.replace("~", "")
            print(tempNums, "tempnums")
            if tempNums == "1234":
                numbers = []
                append = True
                client_sock.send("1")
                print("Send true.")
            else:
                numbers = []
                append = True
                client_sock.send("0")
                print("Send false.")

except IOError as e:
    print(e)

print("Closed.")

client_sock.close()
server_sock.close()
print("all done")
