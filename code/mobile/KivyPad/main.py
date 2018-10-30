from __future__ import absolute_import
from jnius import autoclass
from plyer import storagepath

import time
import SHA
#from multiprocessing import Process

import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.config import Config


####Bluetooth stuff in android accessed via jnius####
BluetoothAdapter = autoclass(u"android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass(u"android.bluetooth.BluetoothDevice")
BluetoothSocket = autoclass(u"android.bluetooth.BluetoothSocket")
UUID = autoclass(u"java.util.UUID")


#Shared method
def createSocketStream(self, devName):
    pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
    socket = None
    found = False
    for dev in pairedDevs:
        print dev, type(dev), "DEV"
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


class PadScreen(Screen, FloatLayout):

    class DeviceSelectionPopup(Popup):

        class DeviceButton(Button):

            def __init__(self, devPopup, **kwargs):
                self.devicePop = devPopup
                super(Button, self).__init__(**kwargs)
                self.outerScreen = self.devicePop.outerScreen

        def __init__(self, padScreen, **kwargs):
            self.outerScreen = padScreen
            super(Popup, self).__init__(**kwargs)
            self.devName = ""
            self.connected = False
            self.setupAll()

        def setupAll(self, instance=None):
            paired = self.getDeviceList()
            if paired:
                self.setupDevButtons(paired)
            else:
                grid = GridLayout(cols=1)
                info = Label(text="No paired devices found.\nPlease make sure your Bluetooth\nis on, you are in range of\nyour device, and you are paired\nto your device.")
                btn = Button(text="Retry", size_hint_y=.2)
                btn.bind(on_release=self.setupAll)
                self.content = grid

        def setupDevButtons(self, listOfDevs):
            self.layout = GridLayout(cols=1, spacing=20, size_hint_y=None)
            self.layout.bind(minimum_height=self.layout.setter("height"))

            for devName in listOfDevs:
                btn = self.DeviceButton(self, text=devName, size_hint_y=None, height=Window.height/10, halign="left", valign="middle")
                self.layout.add_widget(btn)

            self.view = ScrollView(size_hint=(1, 1))
            self.view.add_widget(self.layout)
            self.content = self.view

        def getDeviceList(self):
            result = []
            pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
            for dev in pairedDevs:
                result.append(dev.getName())

            return result


        def changeToDeviceList(self, instance=None):
            self.content = self.view

        def setupBT(self, devName):
            print u"In setupBT"
            try:
                self.outerScreen.rStream, self.outerScreen.sStream = createSocketStream(self, devName)
            except Exception, e:
                print u"Can't connect to device."
                self.connected = False
                grid = GridLayout(cols=1)
                info = Label(text="Can't connect to device\nplease make sure the\ndevice has Bluetooth on,\nis in range, and is\nrunning the FileMate app.")
                btn = Button(text="Retry", size_hint_y=.2)
                btn.bind(on_press=self.changeToDeviceList)
                grid.add_widget(info)
                grid.add_widget(btn)
                self.content = grid
            else:
                print u"Connected to:", devName
                self.connected = True
                self.dismiss()


    def __init__(self, **kwargs):
        super(PadScreen, self).__init__(**kwargs)
        self.nums = []
        self.numsString = u""
        self.rStream = None
        self.sStream = None
        self.deviceSelection = self.DeviceSelectionPopup(self, title="Select your device:", title_align="center", size_hint=(1, 1), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=False)
        Clock.schedule_once(self.deviceSelection.open, 0.5)

    def addNum(self, num):
        if len(self.nums) < 16:
            self.nums.append(int(num))
            self.numsString += "*"
            self.updateDisplay()

    def updateDisplay(self):
        self.ids.display.text = self.numsString

    def backSpace(self):
        if len(self.nums) != 0:
            del self.nums[len(self.nums)-1]
            self.numsString = self.numsString[:len(self.nums)]
            self.updateDisplay()

    def confirm(self):
        pop = Popup(title="Please Wait...", content=Label(text="Waiting for confirmation."), size_hint=(1, 1), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=False)
        if self.rStream != None and self.sStream != None:
            self.sStream.write("{}".format("#"))
            self.nums = SHA.getSHA128of16(self.nums)
            for num in self.nums:
                self.sStream.write("{},".format(num))
                print u"Sent", num
            self.sStream.write("{}".format("~"))
            self.sStream.flush()
            print u"Numbers sent."
            pop.open()

            data = self.rStream.read()
            while True:
                print data, u"data"
                if len(str(data)) != 0:
                    print data, u"break"
                    break
                try:
                    data = self.rStream.read()
                except Exception as e:
                    print e, u"Couldn't recieve data."

            print u"Out of while loop"
            print data, u"Response"
            if data == 49:
                pop.dismiss()
                print u"Valid"
                self.manager.get_screen("Main").key = self.nums
                corPop = Popup(title="Valid.", content=Label(text="Valid passcode!\nPlease leave the app open in the background\notherwise the vault will lock."), size_hint=(.8, .5), pos_hint={"x_center": .5, "y_center": .5})
                corPop.open()
                self.manager.get_screen("Main").sStream, self.manager.get_screen("Main").rStream = self.sStream, self.rStream
                self.manager.current = "Main"

            elif data == 48:
                print u"Invalid."
                pop.dismiss()
                invPop = Popup(title="Invalid.", content=Label(text="Invalid passcode, please try again."), size_hint=(.8, .5), pos_hint={"x_center": .5, "y_center": .5})
                invPop.open()
            else:
                print type(data), "data"
        else:
            print u"Can't connect to device."
            noConnect = Popup(self, title="Can't connect.", content=Label(text="Can't connect to device\nplease make sure the\ndevice has Bluetooth on,\nis in range, and is\nrunning the FileMate app."), title_align="center", size_hint=(.6, .6), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=True)
            noConnect.open()
            self.deviceSelection.open()


class MainScreen(Screen, FloatLayout):

    class recievePopup(Popup):

        def __init__(self, mainScreen, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.downloadsDir = storagepath.get_downloads_dir()
            print self.downloadsDir, u"Downloads dir"

            self.content = Label(text="Waiting to fully recieve file.", halign="center")

        def on_open(self):
            time.sleep(0.2)
            self.recieveFile()
        #     self.recieveThread = Process(target=self.recieveFile, daemon=True)
        #     self.recieveThread.start()

        def recieveFile(self):
            # File is sent with    !NAME!#!!<name here>!!~<data>~!!ENDF!   like a data sandwich.
            # To do: make dictionary with each nameInstruction, startHeader etc, so they can be
            # easily identified.

            buff = []
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
                data = self.outerScreen.rStream.read()
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

                                print buff, u"Removed name header."
                                for letter in name:
                                    fileName += chr(letter)

                                fw = open(self.downloadsDir+"/"+fileName, "wb") #Clear file
                                fw.close()
                                fo = open(self.downloadsDir+"/"+fileName, "ab")


                elif ((len(buff) > bufferSize+8) or (buff[len(buff)-8:] == endFile)):
                    if buff[len(buff)-8:] == endFile:
                        buff[len(buff)-8:] = []
                        print u"End found"

                        fo.write(bytearray(buff))
                        fo.close()
                        self.dismiss()
                        print("Should be closed.")
                        return "Done"

                    else:
                        fo.write(bytearray(buff[:bufferSize]))
                        buff[:bufferSize] = []
                        buffCount += bufferSize


    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.sStream = None
        self.rStream = None
        self.key = ""

        self.recvPop = self.recievePopup(self)


class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file(u"pad.kv")

class uiApp(App):

    def build(self):
        return presentation

def runUI():
    ui = uiApp()
    ui.run()


if __name__ == u"__main__":
    runUI()
