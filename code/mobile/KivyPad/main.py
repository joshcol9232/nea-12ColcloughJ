from __future__ import absolute_import
from jnius import autoclass

import time

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
from kivy.lang import Builder
from kivy.config import Config


####Bluetooth stuff####
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
            self.view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
            self.setupDevButtons(self.getDeviceList())

        def setupDevButtons(self, listOfDevs):
            self.layout = GridLayout(cols=1, spacing=20, size_hint_y=None, height=Window.height * 1.5)
            self.layout.bind(minimum_height=self.layout.setter("height"))
            self.layout.add_widget(Label(text="Select device:", font_size=80))
            for devName in listOfDevs:
                btn = self.DeviceButton(self, text=devName, size_hint_y=None, halign="left", valign="middle")
                self.layout.add_widget(btn)


            self.view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
            self.view.add_widget(self.layout)
            self.content = self.view

        def getDeviceList(self):
            result = []
            pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
            for dev in pairedDevs:
                result.append(dev.getName())
            return result

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
                    found = True
                    break   #Stop when device found
            if found:
                socket.connect()
                return rStream, sStream
            else:
                raise ConnectionAbortedError(u"Couldn't find + connect to device.")

        def setupBT(self, devName):
            try:
                self.outerScreen.rStream, self.outerScreen.sStream = self.createSocketStream(devName)
            except Exception, e:
                print e, u"Can't connect."
            else:
                print u"Connected to:", devName


    def __init__(self, **kwargs):
        super(PadScreen, self).__init__(**kwargs)
        self.nums = []
        self.numsString = u""
        self.rStream = None
        self.sStream = None
        self.deviceSelection = self.DeviceSelectionPopup(self, title="Select your device.", size_hint=(1, 1), pos_hint={"x_center": .5, "y_center": .5}, auto_dismiss=False)
        self.deviceSelection.open()

    def addNum(self, num):
        if len(self.nums) < 16:
            self.nums.append(int(num))
            self.numsString += num
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
            for num in self.nums:
                self.sStream.write("{}".format(num))
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
            elif data == 48:
                print u"Invalid."
                pop.dismiss()
                invPop = Popup(title="Invalid.", content=Label(text="Invalid passcode, please try again."), size_hint=(.8, .5), pos_hint={"x_center": .5, "y_center": .5})
                invPop.open()
            else:
                print type(data), "AAA data"
        else:
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
