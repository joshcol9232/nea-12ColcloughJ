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

import aesFName
from configOperations import dirInputValid

class encPopup(Popup): #For single files

    def __init__(self, outerScreen, encType, labText, fileList, locList, op=True, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = outerScreen
        self.fileList = fileList
        self.locList = locList
        self.done = False

        # Kivy stuff
        self.title = "Please wait..."
        self.pos_hint = {"center_x": .5, "center_y": .5}
        self.size_hint = (.7, .4)
        self.auto_dismiss = False

        self.grid = GridLayout(cols=1)
        self.subGrid = GridLayout(cols=4)
        self.currFile = Label(text="")
        self.per = Label(text="")
        self.spd = Label(text="")
        self.tim = Label(text="")
        self.outOf = Label(text="")
        self.pb = ProgressBar(value=0, max=os.path.getsize(self.fileList[0]), size_hint=(.9, .2))
        self.wholePb = ProgressBar(value=0, max=self._getTotalSize(), size_hint=(.9, .2))
        self.grid.add_widget(Label(text=labText))
        self.grid.add_widget(self.currFile)
        self.subGrid.add_widget(self.per)
        self.subGrid.add_widget(self.spd)
        self.subGrid.add_widget(self.tim)
        self.subGrid.add_widget(self.outOf)
        self.grid.add_widget(self.subGrid)
        self.grid.add_widget(self.pb)
        self.grid.add_widget(self.wholePb)
        self.content = self.grid

        self.checkThread = Thread(target=self.enc, args=(encType, op,), daemon=True)
        self.checkThread.start()

    def _getTotalSize(self):
        total = 0
        for file in self.fileList:
            total += os.path.getsize(file)
        return total

    def _getGoodUnit(self, bps):
        divCount = 0
        divisions = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
        while bps > 1000:
            bps = bps/1000
            divCount += 1

        return ("%.2f" % bps) + divisions[divCount]

    def enc(self, encType, op):
        total = 0
        totalPer = 0
        for i in range(len(self.fileList)):
            self.done = False
            self.pb.value = 0
            self.pb.max = os.path.getsize(self.fileList[i])
            if i == len(self.fileList)-1:
                self.outerScreen.encDecTerminal(encType, self.fileList[i], self.locList[i], True, True, op=op)
            else:
                self.outerScreen.encDecTerminal(encType, self.fileList[i], self.locList[i], True, op=op)

            prevInt = 0
            timeFor1per = 0
            timeAtLastP = time()
            lastSize = 0
            per = 0
            self.outOf.text = str(i)+"/"+str(len(self.fileList))
            if encType == "n":
                fileName = self.fileList[i].split(self.outerScreen.fileSep)
                self.currFile.text = aesFName.decryptFileName(self.outerScreen.key, fileName[len(fileName)-1])
            else:
                self.currFile.text = self.fileList[i]

            while not self.done: # Padding can cause issues as original size is not known.
                try:
                    self.pb.value = os.path.getsize(self.locList[i])
                    self.wholePb.value = total + self.pb.value
                except:
                    pass
                else:
                    per = self.wholePb.value_normalized*100

                    if per-prevInt > 0.5:
                        timeFor1per = time()- timeAtLastP
                        timeAtLastP = time()

                        self.tim.text = "{0:.1f}\nSeconds left.".format(timeFor1per*(((self.wholePb.max - self.wholePb.value)/self.wholePb.max)*100))
                        sizeDelta = self.wholePb.value - lastSize
                        self.spd.text = self._getGoodUnit(sizeDelta/timeFor1per)

                        prevInt = per
                        lastSize = self.wholePb.value

                    self.per.text = "{0:.2f}%".format(per)

                if self.pb.value >= self.pb.max:
                    self.done = True

                if self.done and self.pb.value_normalized != 0: # Don't bother sleeping if the file is finished...
                    sleep(randUniform(0.08, 0.1)) # Sleep imported from time module
                # I added randomness to how long the program sleeps on each iteration, so that the value for the speed didn't just
                # flick between two values, as AES writes to the file every block the amount done is usually increments by one of two
                # values, so this randomness in measuring it makes the speed reading a bit more interesting.
            totalPer += 100
            total += self.pb.max

        self.dismiss()


class btTransferPop(encPopup):

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
        #print("!NAME!{}~~!~~".format(fileObj.name), "Sent")

        newLoc = self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep+fileObj.name
        if not os.path.isdir(self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep):
            os.makedirs(self.outerScreen.osTemp+"FileMate"+self.outerScreen.fileSep)

        self.outerScreen.passToPipe("n", fileObj.hexPath, newLoc, fileObj.name, op=False)   #self, type, d, targetLoc, newName=None, endOfFolderList=False

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
            self.spd.text = self._getGoodUnit(buffCount/(time() - start))

        self.outerScreen.clientSock.send("~!ENDFILE!")
        self.dismiss()


class decryptDirPop(Popup): # Input box for location of where directory is to be saved.

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj

    def checkCanDec(self, inp):
        if dirInputValid(inp, self.outerScreen.fileSep): # Re-use from settings pop, setting self as None because it isn't even used in the function, but is needed to run from within SettingsPop.
            if not os.path.exists(inp):
                os.makedirs(inp)
            if inp[len(inp)-1] != self.outerScreen.fileSep: inp += self.outerScreen.fileSep
            self.outerScreen.encDecDir("n", self.fileObj.hexPath, inp, op=False)

class addNewFolderPop(Popup):

    def __init__(self, mainScreen, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen

    def makeFolder(self, text):
        if dirInputValid(self.outerScreen.currentDir+text, self.outerScreen.fileSep):
            try:
                os.makedirs(self.outerScreen.currentDir+aesFName.encryptFileName(self.outerScreen.key, text))
            except OSError as e:
                if "[Errno 36]" in str(e):  #OSError doesn't store the error code for some reason.
                    pop = Popup(title="Invalid Folder Name", content=Label(text="Folder name too long.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5})
                    pop.open()

            self.outerScreen.refreshFiles()
            self.dismiss()

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
        sure = self.ConfirmationPopup(self, input)
        sure.open()


