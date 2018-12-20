from jnius import autoclass
from plyer import storagepath
from os import remove
from kivy.uix.label import Label
from kivy.uix.popup import Popup

####Bluetooth stuff in android accessed via jnius####
BluetoothAdapter = autoclass(u"android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass(u"android.bluetooth.BluetoothDevice")
BluetoothSocket = autoclass(u"android.bluetooth.BluetoothSocket")
UUID = autoclass(u"java.util.UUID")


#Shared methods
def recieveFileList(rStream, buffAlreadyKnown=[]):
    buff = buffAlreadyKnown
    data = ""

    startList = [33, 70, 73, 76, 69, 76, 73, 83, 84, 33] #!FILELIST!
    endList   = [126, 33, 33, 69, 78, 68, 76, 73, 83, 84, 33]          #~!!ENDLIST!

    while buff[-11:] != endList:
        try:
            data = rStream.read()
        except Exception as e:
            print e, "Failed while getting file list."
            break
        else:
            buff.append(data)

    buff = buff[11:len(buff)-11]

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
    print("Recieve file has been called.")
    # File is sent with    !NAME!#!!<name here>!!~<data>~!!ENDF!   like a data sandwich.
    # To do: make dictionary with each nameInstruction, startHeader etc, so they can be
    # easily identified.
    downloadsDir = storagepath.get_downloads_dir()

    buff = buffAlreadyKnown
    data = ""
    nameInstruction = [33, 78, 65, 77, 69, 33]                  # !NAME!
    endFile         = [126, 33, 69, 78, 68, 70, 73, 76, 69, 33] # ~!ENDFILE!
    separator       = [126, 126, 33, 126, 126]                  # ~~!~~
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
                remove(downloadsDir+"/"+fileName)  # Remove incomplete file. (from os module)
            return False
        else:
            buff.append(data)

        if not nameFound:
            name = []
            for i in range(len(buff)-6):
                if buff[i:i+6] == nameInstruction:
                    z = i+6
                    while (buff[z:z+5] != separator) and (z+5 < len(buff)):
                        name.append(buff[z])
                        z += 1

                    if buff[z:z+5] == separator:
                        nameFound = True
                        buff[i:z+5] = [] # Clear name + separator

                        for letter in name:
                            fileName += chr(letter)

                        fw = open(downloadsDir+"/"+fileName, "wb") #Clear file
                        fw.close()
                        fo = open(downloadsDir+"/"+fileName, "ab")


        elif ((len(buff) > bufferSize+10) or (buff[-10:] == endFile)):
            if buff[-10:] == endFile:
                buff[-10:] = []
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


