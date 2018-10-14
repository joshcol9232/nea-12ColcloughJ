from bluetooth import *
import sys

def recieveFile(rootDir):
	server_sock = BluetoothSocket( RFCOMM )
	server_sock.bind(("",PORT_ANY))
	server_sock.listen(1)

	port = server_sock.getsockname()[1]

	uuid = "80677070-a2f5-11e8-b568-0800200c9a66" #Random UUID from https://www.famkruithof.net/uuid/uuidgen

	advertise_service( server_sock, "FileMateFileTransfer",
                       service_id = uuid,
                       service_classes = [ uuid, SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ],)

	print("[BT]: Waiting for connection on RFCOMM channel", port)

	client_sock, client_info = server_sock.accept()
	print("[BT]: Accepted connection from ", client_info)

	a = False
	while not a:
		data = client_sock.recv(1024)
		name = data.replace(b"~", b"").decode()
		print(name, "name?")
		a = True

	fileLoc = rootDir+name

	fo = open(fileLoc, "wb")
	fo.close()	#Empty file
	fo = open(fileLoc, "ab")
	data = ""
	try:
		while len(data) > -1:
			data = client_sock.recv(1024)
			fo.write(data)
	except:
		print("Connection closed by client.")
		client_sock.close()
		server_sock.close()
		fo.close()

recieveFile("/home/josh/")