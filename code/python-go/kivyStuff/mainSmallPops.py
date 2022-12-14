import os
from threading import Thread
from time import time, sleep
from random import uniform as randUniform

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup

from configOperations import dirInputValid
from mainBtns import deleteButton, decButton, restoreButton

class encDecPop(Popup): #For single files

    def __init__(self, outerScreen, encType, fileList, locList, op=True, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = outerScreen
        self.fileList = fileList
        self.locList = locList

        # Kivy stuff
        self.title = "Please wait..."
        self.pos_hint = {"center_x": .5, "center_y": .5}
        self.size_hint = (.7, .4)
        self.auto_dismiss = False

        self.grid = GridLayout(cols=1)
        self.subGrid = GridLayout(cols=4)
        self.currFile = Label(text="", halign="center", valign="center")
        self.currFile.bind(size=self.currFile.setter("text_size"))  # Wrap text inside label
        self.per = Label(text="")
        self.spd = Label(text="")
        self.tim = Label(text="")
        self.outOf = Label(text="")
        self.pb = ProgressBar(value=0, max=os.path.getsize(self.fileList[0]), size_hint=(.9, .2))
        self.wholePb = ProgressBar(value=0, max=self.__getTotalSize(), size_hint=(.9, .2))
        labText = "Encrypting..."
        if encType == "n":
            labText = "Decrypting..."
        self.grid.add_widget(Label(text=labText, size_hint=(1, .4)))
        self.grid.add_widget(self.currFile)
        self.subGrid.add_widget(self.per)
        self.subGrid.add_widget(self.spd)
        self.subGrid.add_widget(self.tim)
        self.grid.add_widget(self.subGrid)
        if len(self.fileList) > 1:   # Don't bother showing 2 progress bars if the user is only doing 1 file.
            self.grid.add_widget(self.pb)
            self.subGrid.add_widget(self.outOf)
        self.grid.add_widget(self.wholePb)
        self.content = self.grid

        self.checkThread = Thread(target=self.encDec, args=(encType, op,), daemon=True)
        self.checkThread.start()

    def __getTotalSize(self):
        total = 0
        for file in self.fileList:
            total += os.path.getsize(file)
        return total

    def getGoodUnit(self, bps):
        divCount = 0
        divisions = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
        while bps > 1000:
            bps = bps/1000
            divCount += 1

        return ("%.2f" % bps) + " " + divisions[divCount]

    def __getGoodUnitTime(self, time):
        divCount = 0
        times = [(0.001, "Miliseconds"), (1, "Seconds"), (60, "Minutes"), (3600, "Hours"), (86400, "Days"), (604800, "Weeks"), (2419200, "Months"), (31557600, "Years")]   # 1 second, 1 minute, 1 hour, 1 day, 1 week, 1 month, 1 year in seconds
        i = 0
        while i < len(times):  # Is broken when return is found
            if time > times[i][0]:
                i += 1
            else:
                return ("%.2f" % float(time/times[i-1][0])) + " " + times[i-1][1] + " left"

        return "A lot of time left."

    def __getRelPathDec(self, path):   # Similar to decryptRelPath in fileClass
        splitPath = (path.replace(self.outerScreen.path, "")).split(self.outerScreen.fileSep)
        return "/Vault/"+self.outerScreen.fileSep.join(self.outerScreen.decListString(splitPath))

    def __getMeanOfList(self, l):
        out = 0
        for i in l:
            out += i
        return out/len(l)

    def encDec(self, encType, op):
        total = 0
        totalPer = 0
        factor = 0.5
        timeLast = 0
        lastSize = 0
        timeDelta = 0
        perDelta = 0
        per = 0
        prevPer = 0
        lastPerDeltas = [] # Stores 8 of the last percentage deltas so that a mean can be obtained.
        for i in range(len(self.fileList)):
            done = False
            self.pb.value = 0
            self.pb.max = os.path.getsize(self.fileList[i])

            self.outOf.text = str(i)+"/"+str(len(self.fileList))
            if encType == "n":
                self.currFile.text = self.__getRelPathDec(self.fileList[i])
            else:
                self.currFile.text = self.fileList[i]

            while not done: # Padding can cause issues as original size is not known.
                if os.path.exists(self.locList[i]):
                    self.pb.value = os.path.getsize(self.locList[i])
                    self.wholePb.value = total + self.pb.value
                    per = self.wholePb.value_normalized*100

                    a = time()   # Temporary variable to hold the time
                    timeDelta = a - timeLast     # Get time difference
                    if timeDelta >= 0.5:  # Update every 0.5 seconds
                        perDelta = per - prevPer   # Change in percentage in that time.
                        if len(lastPerDeltas) == 8:
                            lastPerDeltas = lastPerDeltas[1:]
                        lastPerDeltas.append(perDelta)
                        perDelta = self.__getMeanOfList(lastPerDeltas)

                        timeLast = a
                        sizeDelta = self.wholePb.value - lastSize  # Get change in size of the file being encrypted
                        speed = sizeDelta/timeDelta  # Get speed of encryption in bytes/second

                        if speed != 0:
                            self.tim.text = self.__getGoodUnitTime((100 - (self.wholePb.value_normalized*100))/(perDelta/timeDelta))
                            self.spd.text = self.getGoodUnit(speed)

                        lastSize = self.wholePb.value
                        prevPer = per

                    self.per.text = "{0:.2f}%".format(per)

                if self.pb.value >= self.pb.max-64:  # -64 is due to padding and key.
                    done = True
                else:
                    sleep(0.01) # Reduces the rate the file is checked, so python doesn't use too much CPU. AES will still run the same regardless, the file just doesn't need to be checked as soon as possible.

            self.pb.value = self.pb.max
            totalPer += 100
            total += self.pb.max


class btTransferPop(encDecPop):

    def __init__(self, mainScreen, fileObjTmp, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.title = "Please wait..."
        self.size_hint = (.7, .4)
        self.pos_hint = {"center_x": .5, "center_y": .5}
        self.auto_dismiss = False
        self.grid = GridLayout(cols=1)
        self.subGrid = GridLayout(cols=3)
        self.currFile = Label(text=fileObjTmp.path)
        self.per = Label(text="")
        self.spd = Label(text="")
        self.tim = Label(text="")
        self.pb = ProgressBar(value=0, max=1, size_hint=(.9, .2))
        self.grid.add_widget(Label(text="Sending..."))
        self.grid.add_widget(self.currFile)
        self.subGrid.add_widget(self.per)
        self.subGrid.add_widget(self.spd)
        self.subGrid.add_widget(self.tim)
        self.grid.add_widget(self.subGrid)
        self.grid.add_widget(self.pb)
        self.content = self.grid

        self.sendThread = Thread(target=self.sendFile, args=(fileObjTmp,), daemon=True) # can be cancelled mid way through
        self.sendThread.start()

    def sendFile(self, fileObj):
        # File name is sent with !NAME!#!!<name here>!!~
        # File data is sent right afterwards, ending with ~!!ENDF!
        # Overall, it is sent as: !NAME!#!!<name here>!!~<datahere>~!!ENDF!
        self.outerScreen.clientSock.send("!NAME!{}~~!~~".format(fileObj.name))

        newLoc = self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep+fileObj.name
        if not os.path.isdir(self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep):
            os.makedirs(self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep)

        self.outerScreen.passToPipe("n", fileObj.hexPath, newLoc)

        bufferSize = 1024
        buff = []
        fr = open(newLoc, "rb")
        buff = fr.read(bufferSize)    #Read 1Kb of data
        buffCount = 0
        self.per.text = "{0:.2f}%".format(0)

        start = time()
        #Send data
        while buff:
            self.outerScreen.clientSock.send(buff)
            buffCount += bufferSize
            buff = fr.read(bufferSize)

            self.pb.value = buffCount/fileObj.rawSize
            self.per.text = "{0:.2f}%".format(self.pb.value*100)
            self.spd.text = self.getGoodUnit(buffCount/(time() - start))

        self.outerScreen.clientSock.send("~!ENDFILE!")
        self.dismiss()


class decryptFileToLocPop(Popup): # Input box for location of where directory is to be saved.

    def __init__(self, mainScreen, fileObj, **kwargs):
        self.outerScreen = mainScreen
        self.fileObj = fileObj
        super(Popup, self).__init__(**kwargs)

    def makeDirs(self, dir):
        try:
            os.makedirs(dir)
        except OSError as e:
            if "[Errno 13]" in str(e): # OSError doesn't store the error code.
                Popup(title="Invalid", content=Label(text="Can't decrypt here.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5}).open()
                return False
            elif "[Errno 36]" in str(e):
                Popup(title="Invalid", content=Label(text="File name too long.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5}).open()
                return False
        else:
            return True

    def checkCanDec(self, inp):
        valid = True
        if dirInputValid(inp, self.outerScreen.fileSep): # Re-use from settings pop, setting self as None because it isn't even used in the function, but is needed to run from within SettingsPop.
            if self.fileObj.isDir:
                if not os.path.exists(inp):
                    valid = self.makeDirs(inp)
                if inp[-1] != self.outerScreen.fileSep: inp += self.outerScreen.fileSep

                if valid:
                    self.outerScreen.encDec("n", self.fileObj.hexPath, inp, op=False)
            else:
                if inp[-1] == self.outerScreen.fileSep:   # If ends with "/", then decrypt with it's file name.
                    if not os.path.exists(inp):
                        valid = self.makeDirs(inp)
                    inp += self.fileObj.name

                if valid:
                    self.outerScreen.encDec("n", self.fileObj.hexPath, inp, op=False)
        else:
            Popup(title="Invalid", content=Label(text="Can't decrypt here, path is invalid.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5}).open()

    def getTitle(self):
        if self.fileObj.isDir:
            return "Decrypt Folder"
        else:
            return "Decrypt File"


class addNewFolderPop(Popup):

    def __init__(self, mainScreen, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen

    def makeFolder(self, text):
        if dirInputValid(self.outerScreen.currentDir+text, self.outerScreen.fileSep):
            try:
                os.makedirs(self.outerScreen.currentDir+self.outerScreen.encString(text))
            except OSError as e:
                if "[Errno 36]" in str(e):  #OSError doesn't store the error code for some reason.
                    Popup(title="Invalid Folder Name", content=Label(text="Folder name too long.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5}).open()

            self.outerScreen.refreshFiles()
            self.dismiss()
        else:
            Popup(title="Invalid", content=Label(text="Invalid folder name.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5}).open()

class addFilePop(Popup):     #The screen (it's actually a Popup) for adding folders/files to the vault.

    def __init__(self, mainScreen, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen

    class ConfirmationPopup(Popup):     #Popup for confirming encryption.

        def __init__(self, fileScreen, input, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.fileScreen = fileScreen
            self.inputText = input


    def checkIfSure(self, input):
        self.ConfirmationPopup(self, input).open()

class fileInfoPop(Popup):

    def __init__(self, mainScreen, fileObj, **kwargs):
        self.outerScreen = mainScreen
        self.fileObj = fileObj
        super(fileInfoPop, self).__init__(**kwargs)
        self.recData = None

        self.ids.infoGrid.bind(minimum_height=self.ids.infoGrid.setter("height"))

        self.inRec = self.outerScreen.recycleFolder in self.fileObj.hexPath   # Bool value of if the file is in recycling
        if self.inRec and not self.fileObj.isDir:
            self.recData, _ = self.outerScreen.getRecycleData(self.fileObj)

        if self.fileObj.extension == "png" or self.fileObj.extension == "jpg":
            self.preview = self.outerScreen.getImgPreview(self.fileObj)
            self.size_hint = (.8, .5)

            self.ids.fileInfoBox.add_widget(self.preview)

        self.loadInfo()

        self.ids.mainBtnsBox.add_widget( deleteButton(self, self.outerScreen, self.fileObj, text="Delete") )

        if self.inRec:
            self.ids.mainBtnsBox.add_widget( restoreButton(self, self.outerScreen, self.fileObj) )
        else:
            self.ids.mainBtnsBox.add_widget( decButton(self, self.outerScreen, self.fileObj, text=self.getDecButtonText()) )


    def on_dismiss(self):
        if os.path.exists(self.fileObj.thumbDir):  # Remove temporary thumnail directory once done with thumbnail
            os.remove(self.fileObj.thumbDir)

    def loadInfo(self):
        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text="File Name:") )
        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text=self.fileObj.name) )

        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text="Location:") )
        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text="/"+self.fileObj.decryptRelPath(),
                                                                 shorten=True, shorten_from="left",
                                                                 split_str=self.outerScreen.fileSep))

        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text="Size:") )
        self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text=self.fileObj.size) )

        if self.inRec and not self.fileObj.isDir:
            self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text="Date deleted:") )
            self.ids.infoGrid.add_widget( self.outerScreen.infoLabel(text=self.recData.dateDeleted) )
            
    
    def getDecButtonText(self):
        if self.fileObj.isDir:
            return "Decrypt Folder"
        else:
            return "Decrypt File"


