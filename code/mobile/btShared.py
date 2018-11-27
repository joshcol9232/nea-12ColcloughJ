from jnius import autoclass
from plyer import storagepath
from kivy.uix.label import Label
from kivy.uix.popup import Popup

####Bluetooth stuff in android accessed via jnius####
BluetoothAdapter = autoclass(u"android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass(u"android.bluetooth.BluetoothDevice")
BluetoothSocket = autoclass(u"android.bluetooth.BluetoothSocket")
UUID = autoclass(u"java.util.UUID")


#Shared methods
def createSocketStream(self, devName):
    pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
    socket = None
    found = False
    for dev in pairedDevs:
        if dev.getName() == devName:
            socket = dev.createRfcommSocketToServiceRecord(UUID.fromString("80677070-a2f5-11e8-b568-0800200c9a66")) #Random UUID from https://www.famkruithof.net/uuid/uuidgen
            rStream = socket.getInputStream()   #Recieving data
            sStream = socket.getOutputStream()  #Sending data
            self.devName = devName
            found = True
            break   #Stop when device found
    if found:
        socket.connect()
        return rStream, sStream
    else:
        raise ConnectionAbortedError(u"Couldn't find + connect to device.")


def recieveFileList(rStream, buffAlreadyKnown=[]):
    buff = buffAlreadyKnown
    data = ""

    startList = [33, 70, 73, 76, 69, 76, 73, 83, 84, 33, 35, 33, 33] #!FILELIST!#!!
    endList = [126, 33, 33, 69, 78, 68, 76, 73, 83, 84, 33]          #~!!ENDLIST!

    while buff[len(buff)-11:] != endList:
        try:
            data = rStream.read()
        except Exception as e:
            print e, "Failed while getting file list."
            break
        else:
            buff.append(data)

    buff = buff[13:len(buff)-11]

    listOfFiles = []
    for i in range(len(buff)):
        if (buff[i-1] == 45) and (buff[i] == 45):  #If two "--" in a row (what i used to separate the names).
            a = i + 1
            name = []
            while (buff[a] != 45 or buff[a+1] != 45) and (a < len(buff)-1):
                name.append(chr(buff[a]))
                a += 1

                if a == len(buff)-1:
                    name.append(chr(buff[a]))

            listOfFiles.append("".join(name))


    print "List of files given:", listOfFiles
    return listOfFiles

def recieveFile(rStream, buffAlreadyKnown=[]):
    # File is sent with    !NAME!#!!<name here>!!~<data>~!!ENDF!   like a data sandwich.
    # To do: make dictionary with each nameInstruction, startHeader etc, so they can be
    # easily identified.
    downloadsDir = storagepath.get_downloads_dir()

    buff = buffAlreadyKnown
    data = ""
    nameInstruction = [33, 78, 65, 77, 69, 33]
    endFile = [126, 33, 33, 69, 78, 68, 70, 33]
    startHeader = [35, 33, 33]
    endHeader = [33, 33, 126]
    nameFound = False
    name = []
    fo, fw = None, None
    fileName = ""
    bufferSize = 1024
    buffCount = 0

    while len(str(data)) > -1:
        try:
            data = rStream.read()
        except Exception as e:
            print e, u"Failed recieving file."
            if buffCount > 0:
                fo.close()
                fo = open(downloadsDir+"/"+fileName, "wb")  # At least empty file if not fully received, as to fully delete the file I would have to use entire os module due to buildozer.
                fo.close()
            return False
        else:
            buff.append(data)

        if not nameFound:
            for i in range(len(buff)-6):
                if buff[i:i+6] == nameInstruction and buff[i+6:i+9] == startHeader:
                    z = i+9
                    name = buff[z:z+3]
                    while (buff[z:z+3] != endHeader) and (z+3 < len(buff)):
                        name.append(buff[z+3])
                        z += 1

                    if name[len(name)-3:] == endHeader and len(name) != 0:
                        name = name[:len(name)-3]
                        nameFound = True
                        buff[i:z+len(endHeader)] = []

                        for letter in name:
                            fileName += chr(letter)

                        fw = open(downloadsDir+"/"+fileName, "wb") #Clear file
                        fw.close()
                        fo = open(downloadsDir+"/"+fileName, "ab")


        elif ((len(buff) > bufferSize+8) or (buff[len(buff)-8:] == endFile)):
            if buff[len(buff)-8:] == endFile:
                buff[len(buff)-8:] = []
                print u"End found"
                fo.write(bytearray(buff))
                fo.close()

                pop = Popup(title="Success!", content=Label(text="File recieved successfuly.\nYou can find your file in\nyour 'Download' folder."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.7, .4))
                pop.open()
                return True

            else:
                fo.write(bytearray(buff[:bufferSize]))
                buff[:bufferSize] = []
                buffCount += bufferSize


