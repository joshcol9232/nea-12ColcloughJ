from plyer import storagepath
from os import remove
from kivy.uix.label import Label
from kivy.uix.popup import Popup

#Shared methods
def recieveFileList(rStream, buffAlreadyKnown=[]):
    buff = buffAlreadyKnown    # If called from other places, some of they data may already 
    data = ""

    endList = [126, 33, 33, 69, 78, 68, 76, 73, 83, 84, 33]          #~!!ENDLIST!

    while buff[-11:] != endList:        # If last 11 elements of the buffer is ~!!ENDLIST!
        try:
            data = rStream.read()
        except Exception as e:
            print e, "Failed while getting file list."
            break
        else:
            buff.append(data)

    buff = buff[10:-11] # Get the actuall list of files from the buffer

    listOfFiles = "".join([chr(i) for i in buff]) # Join input into a string
    listOfFiles = listOfFiles.split("--")[1:]  # First element will be "" due to first part of string being "--""

    print "List of files given:", listOfFiles
    return listOfFiles

def recieveFile(rStream, buffAlreadyKnown=[]):
    print("Recieve file has been called.")
    # File is sent with    !NAME!<name here>~~!~<data>~!!ENDF!   like a data sandwich.
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

    while len(str(data)) > -1:   # While connection is open
        try:
            data = rStream.read()   # Read from the recieving stream
        except Exception as e:
            print e, u"Failed recieving file."
            if buffCount > 0:  # Clean up the file if it has been edited
                fo.close()
                remove(downloadsDir+"/"+fileName)  # Remove incomplete file. (from os module)
            return False
        else:
            buff.append(data)

        if not nameFound:
            name = []
            for i in range(len(buff)-6):  # -6 because that is the length of nameInstruction (scan is 6 wide)
                if buff[i:i+6] == nameInstruction:     # Are these 6 items the same as nameInstruction
                    z = i+6  # Move past nameInstruction
                    while (buff[z:z+5] != separator) and (z+5 < len(buff)):   # Scans current buffer for the name every time a new element is added to buffer, while the name has not been found.
                        name.append(buff[z])
                        z += 1

                    if buff[z:z+5] == separator:  # Once you get to the separator, then you know the name has been recieved.
                        nameFound = True          # Name has been found
                        buff[i:z+5] = [] # Clear name + separator

                        for letter in name:
                            fileName += chr(letter)

                        fo = open(downloadsDir+"/"+fileName, "wb") # Open for writing


        elif ((len(buff) > bufferSize+10) or (buff[-10:] == endFile)):   # If end of file header found
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


