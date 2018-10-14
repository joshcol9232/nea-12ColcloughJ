from bluetooth import *
import sys

def sendFile(file, nameToGive):
	addr = None

	# search for the SampleServer service
	uuid = "80677070-a2f5-11e8-b568-0800200c9a66"
	service_matches = find_service(name="FileMateFileTransfer", address="00:1A:7D:DA:71:0A")

	print(service_matches, "services")

	first_match = service_matches[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]

	print("connecting to \"%s\" on %s" % (name, host))

	# Create the client socket
	sock = BluetoothSocket( RFCOMM )
	sock.connect((host, port))

	print("connected")
	bufferSize = 1024

	#Send file name
	sock.send(nameToGive) #Send name

	fo = open(file, "rb")

	buff = fo.read(bufferSize)
	while buff:
	    sock.send(buff)
	    buff = fo.read(bufferSize)

	sock.close()

sendFile("/home/josh/trumpu.jpg", "geg.png")