from __future__ import absolute_import
from jnius import autoclass

import time
import SHA

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
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.config import Config


####Bluetooth stuff in android accessed via jnius####
BluetoothAdapter = autoclass(u"android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass(u"android.bluetooth.BluetoothDevice")
BluetoothSocket = autoclass(u"android.bluetooth.BluetoothSocket")
UUID = autoclass(u"java.util.UUID")


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
                btn.bind(self.setupAll)
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

        # print u"Can't connect to device."
        # noConnect = Popup(self, title="Can't connect.", content=Label(text="Can't connect to device\nplease make sure the\ndevice has Bluetooth on,\nis in range, and is\nrunning the FileMate app."), title_align="center", size_hint=(.6, .6), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=True)
        # noConnect.open()

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

        def changeToDeviceList(self, instance=None):
            self.content = self.view

        def setupBT(self, devName):
            try:
                self.outerScreen.rStream, self.outerScreen.sStream = self.createSocketStream(devName)
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
            #print(self.nums, self.numsString)
            self.updateDisplay()

    def confirm(self):
        pop = Popup(title="Please Wait...", content=Label(text="Waiting for confirmation."), size_hint=(1, 1), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=False)
        if self.rStream != None and self.sStream != None:
            self.sStream.write("{}".format("#"))
            print self.nums, u"self.nums"
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

            print data, u"Response"
            if data == 49:
                pop.dismiss()
                print u"Valid"
                corPop = Popup(title="Valid.", content=Label(text="Valid passcode!\nPlease leave the app open in the background\notherwise the vault will lock."), size_hint=(.8, .5), pos_hint={"x_center": .5, "y_center": .5})
                corPop.open()
                self.deviceSelection.connected = False #Reset connected value, as you are disconnected when the screens change.
                print self.deviceSelection.connected, u"connected var"
                while not self.deviceSelection.connected:
                    self.deviceSelection.setupBT(self.deviceSelection.devName)

            elif data == 48:
                print u"Invalid."
                pop.dismiss()
                invPop = Popup(title="Invalid.", content=Label(text="Invalid passcode, please try again."), size_hint=(.8, .5), pos_hint={"x_center": .5, "y_center": .5})
                invPop.open()
            else:
                print type(data), "AAA data"
        else:
            print u"Can't connect to device."
            noConnect = Popup(self, title="Can't connect.", content=Label(text="Can't connect to device\nplease make sure the\ndevice has Bluetooth on,\nis in range, and is\nrunning the FileMate app."), title_align="center", size_hint=(.6, .6), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=True)
            noConnect.open()
            self.deviceSelection.open()

# class ConfirmationScreen(Screen, FloatLayout):
#
#     def __init__(self, **kwargs):
#         super(ConfirmationScreen, self).__init__(**kwargs)


class ScreenManagement(ScreenManager):
    # LoginScreen = ObjectProperty(None)
    # MainScreen = ObjectProperty(None)
    # addFileScreen = ObjectProperty(None)
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
