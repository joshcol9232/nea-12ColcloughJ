from os import listdir
from os.path import isdir as osIsDir
from subprocess import Popen, PIPE

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.clock import Clock
from threading import Thread

import SHA

# Try importing the BT module, if it isn't available then they just can't use BT. Imported in case the user wants to switch from normal login to Bluetooth login.
try:
    from bluetooth import *
except:
    pass

class LoginScreen(Screen):

    def __init__(self, fileSep, path, startDir, **kwargs):
        self.fileSep, self.path, self.startDir = fileSep, path, startDir  # Start dir is location of running program, path is path of vault
        super(Screen, self).__init__(**kwargs)  # Run kivy's Screen.__init__ function with the key word arguments (such as size or position)
        self.key = ""

    def cancel(self):
        self.manager.get_screen("Main").useBT = True                      # Am now using BT
        Builder.load_file(self.startDir+"kivyStuff/kvFiles/loginScBT.kv") # Load the styling file for BT login screen
        self.manager.add_widget(LoginScreenBT(self.fileSep, self.path, self.startDir, name="Login")) # Create the new screen
        self.name = "Dead"  # To prevent clash with new login screen.
        self.manager.current = "Login"   # Change to Login
        self.manager.remove_widget(self) # Remove self from the app
        self = None                      # Kill self

    def findFile(self, dir):    # For finding a file to decrypt first block and compare it with key given.
        fs = listdir(dir)
        for item in fs:
            if osIsDir(dir+item+"/"):
                if self.count == 0:
                    self.findFile(dir+item+"/")
                else:
                    return
            else:
                self.decryptTestFile = dir+item
                self.count += 1
                return

    def passToTerm(self, key, d):           # Makes a pipe to communicate with AES
        if self.fileSep == "\\":
            progname = "AESWin"
        else:
            progname = "AES/AES"
        goproc = Popen(self.startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate(("test, "+d+", 0, ").encode()+key.encode())
        return out

    def getIfValidKey(self, inputKey):              # Gets the output of the AES key checker.
        if len(listdir(self.path)) > 1:
            self.decryptTestFile = ""
            self.count = 0
            self.findFile(self.path)
            diditwork = self.passToTerm(inputKey, self.decryptTestFile)
            if diditwork == b"-Valid-": #The go program prints "-Valid-" or "-Invalid-" once it is done checking the key.
                return True
            else:
                return False
        else:
            return True

    def checkKey(self, inputKey):   # Handles the GUI while the key is checked, and passes key to functions to check it.
        if len(inputKey) < 1:
            Popup(title="Invalid", content=Label(text="Invalid key, valid key\ncontains at least 1 digit."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4)).open()
            return "Login"
        try:
            int(inputKey)
        except:
            Popup(title="Invalid", content=Label(text="Invalid key, valid key\ncontains no letters."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4)).open()
            return "Login"
        else:
            if len(str(inputKey)) > 16:
                Popup(title="Invalid", content=Label(text="Invalid key, longer than\n 16 characters."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4)).open()
                return "Login"
            else:
                inputKeyTemp = []
                for i in range(len(inputKey)):
                    inputKeyTemp.append(int(inputKey[i]))
                inputKey = inputKeyTemp
                inputKey = SHA.getSHA128of16(inputKey)
                key = " ".join(str(i) for i in inputKey)
                valid = self.getIfValidKey(key)
                if valid:
                    self.ids.keyInput.text = "" #reset key input if valid
                    self.key = key
                    return "Main"
                else:
                    Popup(title="Invalid", content=Label(text="Invalid key."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4)).open()
                    return "Login"

    def needToSetKey(self):      # Gets text to tell the user if they need to set a key.
        if len(listdir(self.path)) == 0:   # If there are no files in the vault, then the key hasn't been set yet.
            return "Input New Key (Write this down if you have to)"
        else:
            return "Input Key"


class LoginScreenBT(LoginScreen, Screen):      #Has the same methods as LoginScreen, but some overwritten with bluetooth.

    def __init__(self, fileSep, path, startDir, **kwargs):
        self.fileSep, self.path, self.startDir = fileSep, path, startDir
        super(Screen, self).__init__(**kwargs)
        self.key = ""

    def on_enter(self):
        self.serv = None
        self.startServ = Clock.schedule_once(self.startSrv, 0.5) # Use the clock to allow the screen to be rendered. (Waits 0.5 seconds for screen to be loaded.)

    def checkKey(self, inputKey):
        inputKey = inputKey.split(",")
        inputKey = inputKey[:-1]
        key = " ".join(str(i) for i in inputKey)    #Formatting for AES
        valid = self.getIfValidKey(key)
        if valid:
            self.key = key
            self.manager.get_screen("Main").key = key
            return True
        else:
            return False

    def cancel(self):
        if self.serv != None:
            self.manager.get_screen("Main").serverSock.close()  # Close the BT server
            self.serv.join()  # Close the thread that runs the server (in LoginScreenBT)
            try:
                self.manager.get_screen("Main").clientSock.close()
            except AttributeError:  # clientSock will not be initilized if there are no clients.
                pass
        else:
            self.startServ.cancel()   # Cancels scheduled task to start server, as we are switching screens anyway.

        print("Server closed.")
        self.manager.get_screen("Main").useBT = False
        Builder.load_file(self.startDir+"kivyStuff/kvFiles/loginSc.kv")
        self.manager.add_widget(LoginScreen(self.fileSep, self.path, self.startDir, name="Login"))
        self.name = "Dead"      # To prevent name clash with other login screen.
        self.manager.current = "Login"
        self.manager.remove_widget(self)
        self = None

    def startSrv(self, dt=None):
        self.serv = Thread(target=self.manager.get_screen("Main").startBT, daemon=True)  # Runs the function in MainScreen, which prevents segmentation, so I don't have to shutdown server when screen is switched
        self.serv.start()
