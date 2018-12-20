from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from btShared import recieveFileList, recieveFile

class FileSelectionScreen(Screen, FloatLayout):

    class listButton(Button):

        def __init__(self, mainScreen, fileName, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileName = fileName


    def __init__(self, **kwargs):
        super(FileSelectionScreen, self).__init__(**kwargs)
        self.sStream = None
        self.rStream = None
        self.fileList = []

        # List of possible responses
        self.endOfTreeResponse = [33, 69, 78, 68, 79, 70, 84, 82, 69, 69, 33] # !ENDOFTREE!
        self.startList         = [33, 70, 73, 76, 69, 76, 73, 83, 84, 33] # !FILELIST!
        self.endList           = [126, 33, 33, 69, 78, 68, 76, 73, 83, 84, 33]          # ~!!ENDLIST!
        self.nameInstruction   = [33, 78, 65, 77, 69, 33]                       # !NAME!  --Start of a file
        self.fileNotFound      = [33, 78, 79, 84, 70, 79, 85, 78, 68, 33]          # !NOTFOUND!  --Response to file selection


    def on_enter(self):
        self.createButtons(self.fileList)

    def exit(self):
        self.manager.current = "Main"

    def removeButtons(self):
        self.grid.clear_widgets()
        self.scroll.clear_widgets()
        self.grid = 0
        try:
            self.remove_widget(self.scroll)
        except Exception as e:
            print e, u"Already removed?"
        self.scroll = 0

    def createButtons(self, array):
        self.grid = GridLayout(cols=1, size_hint_y=None) # Added in case I need to add more columns in the future (file size etc)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        for item in array:
            btn = self.listButton(self, item, text=("    "+str(item)), height=Window.height/10, halign="left", valign="middle")
            btn.bind(size=btn.setter("text_size"))
            self.grid.add_widget(btn)

        self.scroll = ScrollView(size_hint=(1, .86))
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)
        print u"done creating buttons"

    def recreateButtons(self, array):
        self.removeButtons()
        self.createButtons(array)

    def selectFile(self, fileName):
        print fileName, "Selected."
        # File request looks like: !FILESELECT!<name here>~!ENDSELECT!
        msg = [33, 70, 73, 76, 69, 83, 69, 76, 69, 67, 84, 33] # !FILESELECT!


        for letter in fileName:
            msg.append(ord(letter))

        msg += [126, 33, 69, 78, 68, 83, 69, 76, 69, 67, 84, 33] # End header: ~!ENDSELECT!

        self.sStream.flush() # Clear write buffer on data stream.
        print msg, "full msg to be sent."

        for i in msg:
            self.sStream.write(i)

        # Get response
        buff = []
        data = ""
        responseFound = False
        print u"Waiting for response"
        while not responseFound:
            try:
                data = self.rStream.read()
            except Exception as e:
                print e, "Failed recieving response to select file."
                return False
            else:
                buff.append(data)

            if (buff[:6] == self.nameInstruction) and (len(buff) >= 6):
                print u"Is name instruction"
                recieveFile(self.rStream, buff)
                responseFound = True
                buff = []

            elif (buff[:10] == self.fileNotFound) and (len(buff) >= 10):
                print u"Response is fileNotFound."
                raise ValueError("File was not found by host.")
                responseFound = True
                buff = []

            elif (buff[:10] == self.startList) and (len(buff) >= 10):
                print u"Response is a file list."
                self.fileList = recieveFileList(self.rStream, buff)
                responseFound = True
                self.recreateButtons(self.fileList)

            elif len(buff) >= 13:
                print u"Didn't get response :(", buff
                buff = []

    def getBackDir(self):
        # Back dir request looks like: !BACK!
        backCommand = [33, 66, 65, 67, 75, 33]
        self.sStream.flush() # Clear the buffer for sending
        for i in backCommand:
            self.sStream.write(i)

        data = ""
        buff = []
        responseFound = False
        while not responseFound:
            try:
                data = self.rStream.read()
            except Exception as e:
                print e, "Failed recieving server response to BACK request."
                return False
            else:
                buff.append(data)

            if (buff[:11] == self.endOfTreeResponse) and (len(buff) >= 11):
                print "END OF TREE"
                buff = []
                responseFound = True

            elif (buff[:10] == self.startList) and (len(buff) >= 10):
                print "START OF LIST"
                responseFound = True
                self.fileList = recieveFileList(self.rStream, buff)
                print self.fileList, "file list?"
                self.recreateButtons(self.fileList)

            elif len(buff) >= 11:
                print "start header not found yet :(", buff
                buff = []

