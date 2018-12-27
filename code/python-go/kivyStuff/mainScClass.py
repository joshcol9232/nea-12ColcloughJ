import os
from shutil import move, disk_usage, rmtree
from threading import Thread
from functools import partial   # For parsing in functions with multiple arguments to widgets/threads
from subprocess import Popen, PIPE

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from fileClass import File
import aesFName
import sortsCy
# Own kivy classes
import mainBtns
from settingsScreen import SettingsScreen
import mainSmallPops as mainSPops

try:
    from bluetooth import *
except:
    pass

class MainScreen(Screen):

    class infoLabel(Label):   # Not a popup so only suitable place.
        pass

    def __init__(self, fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc, **kwargs):
        self.fileSep, self.osTemp, self.startDir, self.assetsPath, self.path, self.searchRecursively, self.useBT, self.configLoc = fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc
        super(Screen, self).__init__(**kwargs)
        self.ascending = True       # Sort order
        self.key = ""
        self.encPop = None
        self.entered = False
        self.validBTKey = False
        self.useBTTemp = self.useBT
        self.previousDir = None
        self.lastPathSent = ""
        self.recycleFolder = ""
        self.recycleName = ""
        self.thumbsName = ""

        Window.bind(on_dropfile=self.onFileDrop)    #Binding the function to execute when a file is dropped into the window.
        self.currentDir = self.path


    def on_enter(self): # When the screen is started.
        self.key = self.manager.get_screen("Login").key  # Fetch the key from the Login Screen.
        if not self.entered:
            self.setupSortButtons() #Put sort buttons in place.
            self.recycleName = aesFName.encryptFileName(self.key, ".$recycling")    # Prepare recycling and thumbnail folder names for use in the program.
            self.thumbsName = aesFName.encryptFileName(self.key, ".$thumbs")
            self.recycleFolder = self.path+self.recycleName+self.fileSep

            if not os.path.exists(self.recycleFolder):
                print("Recycling folder not found in directory, making one now.")
                os.makedirs(self.recycleFolder)

            self.entered = True

        if self.recycleFolder in self.currentDir:
            self.createButtons(self.List(self.path))     # Don't want to log into the recycling bin, as the user might get confused.
        else:
            self.createButtons(self.List(self.currentDir)) # Loads previous directory.

    def on_leave(self):     # Kept separate from lock because i may want to add more screens that need the key, and do not log the user out.
        if self.useBT:      # Popups that are open block the lock button, but if BT is lost, the popups stay open.
            try:                            # Try to close any popups that may be open.
                self.largePop.dismiss()
                self.remove_widget(self.largePop)
            except Exception as e:
                print(e, "Already closed?")
            try:
                self.smallPop.dismiss()
                self.remove_widget(self.smallPop)
            except Exception as e:
                print(e, "Already closed?")
            try:
                self.encPop.dismiss()
                self.remove_widget(self.encPop)
            except Exception as e:
                print(e, "Already closed?")

        self.removeButtons()

    def lock(self, fromRunServ=False):  # Procedure for when the program is locked. If it has been called from runServMain, then we might still be on login screen, so don't change screen to login, and restart the server.
        self.clearUpTempFiles() # Delete all temporary files (decrypted files ready for use).
        if self.useBT:
            self.manager.get_screen("Login").ids.clientLabel.text = ""

        if fromRunServ and self.validBTKey == False:
            self.runServMain()
        else:
            self.validBTKey = False
            return mainthread(self.changeToLogin())      #Change screen to the login screen. Ran on mainthread in case it was called in

    def runServMain(self):
        self.serverSock = BluetoothSocket( RFCOMM )
        self.serverSock.bind(("",PORT_ANY))
        self.serverSock.listen(1)

        uuid = "80677070-a2f5-11e8-b568-0800200c9a66"

        try:
            advertise_service(self.serverSock, "FileMateServer",
                              service_id = uuid,
                              service_classes = [ uuid, SERIAL_PORT_CLASS ],
                              profiles = [ SERIAL_PORT_PROFILE ],)
        except BluetoothError as e:
            Popup(title="Error", content=Label(text="Bluetooth not available.\nPlease make sure your bluetooth is on,\nor change to normal login.\n\nReason: "+str(e)), size_hint=(.4, .4), auto_dismiss=True).open()
            return

        print("[BT]: Waiting for connection on RFCOMM channel", self.serverSock.getsockname()[1])

        self.clientSock, self.clientInfo = self.serverSock.accept()  # Wait for a connection
        print("[BT]: Accepted connection from ", self.clientInfo)
        self.manager.get_screen("Login").ids.clientLabel.text = "Connected to: "+str(self.clientInfo[0])

        numbers = []
        data = ""
        buff = []
        backCommand = [33, 66, 65, 67, 75, 33]                                # !BACK!
        fileSelectCommand = [33, 70, 73, 76, 69, 83, 69, 76, 69, 67, 84, 33]  # !FILESELECT!
        endHeader =  [126, 33, 69, 78, 68, 83, 69, 76, 69, 67, 84, 33]        # ~!ENDSELECT!

        try:
            while len(data) > -1:
                data = self.clientSock.recv(1024) # Recieve 1kb of data
                print("[BT]: Received data.")
                if not self.validBTKey:                 # If the key is not valid yet, BT server has to wait for key
                    numbers.append(str(data, "utf-8"))
                    if b"~" in data:    # End of key message
                        append = False
                        tempNums = "".join(numbers)
                        tempNums = tempNums.replace("#", "")
                        tempNums = tempNums.replace("~", "")
                        if self.manager.get_screen("Login").checkKey(tempNums):   # Check the key in login.
                            numbers = []
                            self.clientSock.send("1")
                            print("[BT]: Send true.")
                            self.validBTKey = True
                            self.recycleName = aesFName.encryptFileName(self.key, ".$recycling") # Set so that file list can be sent
                            self.thumbsName = aesFName.encryptFileName(self.key, ".$thumbs")   
                            self.sendFileList(self.getListForSend(self.path))
                            mainthread(self.changeToMain())   # Exit thread and change screen to main.
                        else:
                            numbers = []
                            self.clientSock.send("0")
                            print("[BT]: Send false.")
                            self.validBTKey = False

                else:
                    for i in data:
                        buff.append(i)

                    if buff[:6] == backCommand:   # Buffer is reset every time a header is found
                        pathBack = self.getPathBack(self.lastPathSent)
                        if (not pathBack) or (pathBack.replace(self.path, "") == pathBack):    # If you can't go further back (if pathBack has less than path, then remove returns the original string).
                            print("[BT]: Can't go further back.")
                            self.clientSock.send("!ENDOFTREE!")
                        else:
                            self.sendFileList(self.getListForSend(pathBack))
                        buff = []

                    elif buff[:12] == fileSelectCommand:  # If the command is fileSelect
                        commandParams = buff[12:]         # Get parameters (buffer will not be reset)
                        if commandParams[-12:] == endHeader:  # If end of the buffer is the endHeader, then proceed.
                            fileWantedList = commandParams[:-12]
                            fileWanted = ""
                            for letter in fileWantedList:
                                fileWanted += chr(letter)

                            print("[BT]:", fileWanted, "fileWanted")
                            buff = []
                            filesInPath = self.List(self.lastPathSent)  # Get list of files at directory requested.

                            f = 0
                            fileObj = None
                            while (f < len(filesInPath)) and (fileObj == None): # Searches for the file in the path
                                if filesInPath[f].name == fileWanted:
                                    fileObj = filesInPath[f]
                                f += 1

                            if fileObj != None:    # If the file was found, then send it
                                if fileObj.isDir:  # If it was a directory then send the list of files in that directory.
                                    self.sendFileList(self.getListForSend(fileObj.hexPath))
                                else:
                                    self.makeSendFile(fileObj) # Otherwise send the file.

                            else:
                                print("[BT]: Couldn't find that file :/")
                                self.clientSock.send("!NOTFOUND!")


                    elif len(buff) > 12: # Clear buffer and wait for next command.
                        buff = []


        except IOError as e:
            print(e)        # Will be caused when app on mobile closes.

        print("[BT]: Closed.")

        self.clientSock.close()
        self.serverSock.close()
        self.lock(fromRunServ=True)

    def sendFileList(self, fileList):
        # File list sent like: !FILELIST!--fileName1--filename2~!!ENDLIST!
        self.clientSock.send("!FILELIST!")
        print("[BT]: Sent !FILELIST!")

        for i in fileList:
            self.clientSock.send("--{}".format(i))

        print("[BT]: Sent full list, now sent end.")
        self.clientSock.send("~!!ENDLIST!")


    def getListForSend(self, path):
        if not path:
            return False
        else:
            fs = os.listdir(path)
            listOfFolders = []
            listOfFiles = []
            for item in fs:
                if (item != self.thumbsName) and (item != self.recycleName):
                    if os.path.isdir(path+item):
                        listOfFolders.append(aesFName.decryptFileName(self.key, item))
                    else:
                        listOfFiles.append(aesFName.decryptFileName(self.key, item))

            self.lastPathSent = path

            return sortsCy.quickSortAlph(listOfFolders, fileObjects=False)+sortsCy.quickSortAlph(listOfFiles, fileObjects=False)  # Sort the list and return it



##Functions for changing screen within threads (used to prevent segmentation faults)
    @mainthread
    def changeToMain(self):
        self.manager.current = "Main"

    @mainthread
    def changeToLogin(self):    #Only used for checkServerStatus because you can only return a function or variable, and if i execute this within the thread then it causes a segmentation fault.
        self.manager.current = "Login"
##############################################

    def startBT(self):
        self.serverThread = Thread(target=self.runServMain, daemon=True)      #Start BT server as thread so the screen still renders.
        self.serverThread.start()

    def setupSortButtons(self):
        self.sortsGrid = GridLayout(cols=2, size_hint=(.99, .04), pos_hint={"x": .005, "y": .79})    #Make a grid of 1 row (colums=2 and i am only adding 2 widgets) to hold sort buttons.
        self.nameSort = mainBtns.nameSortButton(self, text="^")  # Default starts with Alphabetical sort ascending.
        self.sizeSort = mainBtns.sizeSortButton(self)
        self.sortsGrid.add_widget(self.nameSort)
        self.sortsGrid.add_widget(self.sizeSort)
        self.add_widget(self.sortsGrid) #Add the sort buttons grid to the float layout of MainScreen.

    def getGoodUnit(self, bytes):       #Get a good unit for displaying the sizes of files.
        if bytes == " -":
            return " -"
        else:
            divCount = 0
            divisions = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB", 5: "PB"}
            while bytes > 1000:
                bytes = bytes/1000
                divCount += 1

            return ("%.2f" % bytes) + divisions[divCount]

    def getSortedFoldersAndFiles(self, fileObjects, inverse=False): # Get a sorted list of files for display. Displays all folders before files.
        folders = []
        files = []
        for i in range(len(fileObjects)):   #Separate into folders and files
            if fileObjects[i].isDir:
                folders.append(fileObjects[i])
            else:
                files.append(fileObjects[i])

        foldersSort = sortsCy.quickSortAlph(folders)   #Quick sort the list of folders and the list of files.
        filesSort = sortsCy.quickSortAlph(files)

        if inverse: #If inverse
            foldersSort = foldersSort[::-1] #Invert the array
            filesSort = filesSort[::-1]

        return foldersSort+filesSort

    def openRecycling(self):  # Open the recycling folder.
        if not os.path.exists(self.recycleFolder):
            print("Recycling folder doesn't exist, making one now.")
            makedirs(self.recycleFolder)

        Popup(title="Changed Mode",
              content=Label(text="You are now in the\nrecycling folder.\nClick files to restore, and \nenter the INFO menu\nto see more information,\nor delete the file permanently."),
              pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4)).open()
        self.currentDir = self.recycleFolder
        self.removeButtons()
        print(self.currentDir, "current dir")
        self.createButtons(self.List(self.currentDir))


#######Button Creation and button functions#######
    def createButtonsCore(self, array): # Makes each file button with it's information and adds it to the scroll view.
        self.currentList = array
        for item in array:
            if item.name != ".$recycling" and item.name != ".$thumbs": # If the folder is the recycling folder or thumbnail temporary folder, don't draw it.
                back = (1, 1, 1, 1)
                if item.isDir:   # Colour folders darker than files
                    back = (0.3, 0.3, 0.3, 1)   # Works as a tint rather than a colour.

                btn = mainBtns.listButton(self, item, text=("    "+item.name), background_color=back)
                info = mainBtns.infoButton(self, item, background_color=back)

                btn.bind(size=btn.setter("text_size"))  # Set the text to wrap within the button
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(item.size), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))  # Wrap text in label
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)

    def createButtons(self, fileObjects, sort=True):
        self.currentList = []
        if sort:
            fileObjects = self.getSortedFoldersAndFiles(fileObjects)    #Sort the list of files.

        self.grid = GridLayout(cols=3, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll = ScrollView(size_hint=(.99, .79), pos_hint={"x": .005, "y": 0}) #Grid is added to the scroll view.
        self.scroll.add_widget(self.grid)

        self.createButtonsCore(fileObjects)
        self.add_widget(self.scroll)    #Scroll view is added to the float layout of MainScreen.


    def traverseButton(self, fileObj):  # Function when file is clicked.
        if self.recycleFolder not in self.currentDir:
            if fileObj.isDir:   #If is a folder, then display files within that folder.
                self.previousDir = self.currentDir
                self.currentDir = fileObj.hexPath
                self.resetButtons()
            else:   # If is a file, decrypt the file and open it.
                self.decrypt(fileObj)
        else:
            print("Recovering this file to path:", fileObj.name)
            move(fileObj.hexPath, self.path) # Imported from shutil
            self.refreshFiles()

    def openAddFilePop(self):     # Needs to be asigned to self.smallPop because if the screen is closed with the popup open (only possible when using Bluetooth), all crucial popups need to be closed.
        self.smallPop = mainSPops.addFilePop(self)
        self.smallPop.open()

    def openAddFolderPop(self):
        self.smallPop = mainSPops.addNewFolderPop(self)
        self.smallPop.open()

    def onFileInfoClose(self, fileObj, _):  # _ is me discarding the popup object.
        if os.path.exists(fileObj.thumbDir):  # Remove temporary thumnail directory once done with thumbnail
            os.remove(fileObj.thumbDir)

    def getFileInfo(self, fileObj):     #Get information about a file/folder.
        size = (.7, .4)  # Size of popup
        if fileObj.extension == "png" or fileObj.extension == "jpg":
            thumb = self.getThumbnail(fileObj)
            size = (.8, .5)  # Increase size of popup to display image preview.

        # Works as: internalLayout -> scrolView + (Image?)
        # scrollView contains infoGrid with all of the file's information.
        internalLayout = BoxLayout(orientation="horizontal", size_hint=(1, 1))
        scrolView = ScrollView()
        self.infoPopup = Popup(title="File Information", content=internalLayout, pos_hint={"center_x": .5, "center_y": .5}, size_hint=size)
        self.infoPopup.bind(on_dismiss=partial(self.onFileInfoClose, fileObj, ))

        infoGrid = GridLayout(cols=2, size_hint_y=None, row_default_height=40)
        scrolView.add_widget(infoGrid)
        internalLayout.add_widget(scrolView)

        if fileObj.extension == "png" or fileObj.extension == "jpg":
            internalLayout.add_widget(thumb)

        infoGrid.add_widget(self.infoLabel(text="File Name:", halign="left", valign="middle"))
        infoGrid.add_widget(self.infoLabel(text=fileObj.name, halign="left", valign="middle"))

        infoGrid.add_widget(self.infoLabel(text="Current Location:", halign="left", valign="middle"))
        infoGrid.add_widget(self.infoLabel(text="/Vault/"+fileObj.decryptRelPath(), halign="left", valign="middle"))

        infoGrid.add_widget(self.infoLabel(text="Size:", halign="left", valign="middle"))
        infoGrid.add_widget(self.infoLabel(text=str(fileObj.size), halign="left", valign="middle"))

        delText = "Delete"
        if self.recycleFolder in self.currentDir:    # If in the recycling folder, then delete the item permanently.
           delText = "Delete Permanently"

        infoGrid.add_widget(mainBtns.deleteButton(self, fileObj,text=delText))

        decBtnText = "Decrypt File"
        if fileObj.isDir:
            decBtnText = "Decrypt Folder"

        if fileObj.rawSize > 0:
            decBtn = Button(text=decBtnText, halign="left", valign="middle")
            decBtn.bind(on_release=partial(self.decryptFileToLoc, fileObj))
            infoGrid.add_widget(decBtn)

        self.infoPopup.open()

    def makeSendFile(self, fileObj, buttonInstance=None):
        self.sendFile = mainSPops.btTransferPop(self, fileObj)
        self.sendFile.open()

    def moveFileToRecycling(self, fileObj):
        print("Moving", fileObj.hexPath)
        if os.path.exists(fileObj.hexPath):
            move(fileObj.hexPath, self.recycleFolder) # Imported from shutil
        else:
            raise FileNotFoundError(fileObj.hexPath, "Not a file, can't move to recycling.") # Doesn't exist, so issue with code somewhere.

    def deleteFile(self, fileObj):
        if os.path.exists(fileObj.hexPath): #Checks file actually exists before trying to delete it.
            if self.recycleFolder not in self.currentDir:   # If outside of recycling bin.
                print("Moving", fileObj.hexPath)
                if os.path.exists(self.recycleFolder+fileObj.hexName):
                    if os.path.isdir(self.recycleFolder+fileObj.hexName):
                        rmtree(self.recycleFolder+fileObj.hexName)
                    else:
                        os.remove(self.recycleFolder+fileObj.hexName)
                move(fileObj.hexPath, self.recycleFolder) # Imported from shutil
            else:
                print("Deleting:", fileObj.hexPath, "and checking temp.")
                if os.path.exists(self.osTemp+"FileMate"+self.fileSep+fileObj.name):  # If removing permanently, check that the file is not decrypted in <system_temp>.
                    os.remove(self.osTemp+"FileMate"+self.fileSep+fileObj.name)
                if fileObj.isDir:    # Delete the file/folder
                    rmtree(fileObj.hexPath) # Imported from shutil
                else:
                    os.remove(fileObj.hexPath)
            self.refreshFiles()
            self.infoPopup.dismiss()

        else:
            raise FileNotFoundError(fileObj.hexPath, "Not a file, can't delete.")

    def goBackFolder(self):     #Go up a folder.
        if self.currentDir != self.path:    #Can't go further past the vault dir.
            self.previousDir = self.currentDir
            if self.recycleFolder in self.currentDir:
                self.goHome()
            else:
                self.currentDir = self.getPathBack(self.currentDir)
            self.resetButtons()
        else:
            print("Can't go further up.")
            return False

    def getPathForButton(self, item):   # Get the path to the asset for each button.
        return self.assetsPath+item

    def removeButtons(self):    # Remove the list of files.
        self.grid.clear_widgets()
        self.scroll.clear_widgets()
        self.remove_widget(self.scroll)

    def resetButtons(self): # Goes back to self.currentDir, different to refresh.
        self.removeButtons()
        self.nameSort.text = "^"
        self.sizeSort.text = ""
        self.createButtons(self.List(self.currentDir))

    def refreshFiles(self):   # Refreshes the files in the current directory
        self.removeButtons()
        self.createButtons(self.List(self.currentDir))

    def refreshButtons(self): # Refreshes file list buttons currently displayed.
        self.removeButtons()
        self.createButtons(self.currentList, False)

    def goHome(self):   #Takes the user back to the vault dir.
        self.currentDir = self.path
        self.refreshFiles()


    def List(self, dir):    # Lists a directory, returning File objects.
        fs = os.listdir(dir)
        listOfFolders = []
        listOfFiles = []
        for item in fs:
            if os.path.isdir(dir+item):
                listOfFolders.append(File(self, dir+item, item, self.fileSep, isDir=True))
            else:
                if os.path.exists(self.currentDir+self.thumbsName+self.fileSep+item):
                    listOfFiles.append(File(self, dir+item, item, self.fileSep, dir+self.thumbsName+self.fileSep+item))
                else:
                    listOfFiles.append(File(self, dir+item, item, self.fileSep))

        return listOfFolders+listOfFiles

    def getPathBack(self, origPath):  # Gets the path above the current folder.
        tempDir = origPath.split(self.fileSep)
        del tempDir[-2]
        tempDir = self.fileSep.join(tempDir)
        return tempDir

###########Searches############
    def findAndSortCore(self, dirName, item):
        files = self.List(dirName)
        for fileObj in files:
            loc = fileObj.name.find(item) # Find where in the word the item is found, if it is a substring of the word

            if fileObj.name == item:
                self.searchResults = [fileObj] + self.searchResults
            elif loc != -1: # If the search term is a substring of the current word
                self.unsorted.append((loc, fileObj))   #Adds loc found in word, so that it can be sorted by where it is found

            if (fileObj.isDir and self.searchRecursively) and (fileObj.hexPath != self.recycleFolder) and (fileObj.hexName != self.thumbsName):
                self.findAndSortCore(fileObj.hexPath, item)  # Search folder if recursive and not recycle folder or thumbnail folder.


    def findAndSort(self, item):    #Main search function.
        self.unsorted = []
        self.findAndSortCore(self.currentDir, item)

        if len(self.unsorted) > 0:
            sorted = sortsCy.quickSortTuples(self.unsorted)
            for i in sorted:
                self.searchResults.append(i[1])
            mainthread(self.removeButtons())
            return mainthread(self.createButtons(self.searchResults, False))

        elif len(self.searchResults) == 0:
            pop = Popup(title="No Results", content=Label(text="No results found for:\n"+item, halign="center"), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
            pop.open()


    def searchForItem(self, item):
        self.resetButtons()
        self.searchResults = []
        Thread(target=self.findAndSort, args=(item,), daemon=True).start()


####Progress Bar Information####
    def values(self, st):   #Information for space left on device.
        values = disk_usage(self.path) # Imported from shutil
        if st:
            return self.getGoodUnit(int(values[1]))+" / " + self.getGoodUnit(int(values[0])) + " used."
        else:
            return [values[0], values[1]]


######Encryption Stuff + opening decrypted files######
    def passToPipe(self, type, d, targetLoc, newName=None, endOfFolderList=False, op=True):     #Passes parameters to AES written in go.
        if self.fileSep == "\\":
            progname = "AESWin.exe"
        else:
            progname = "AES"

        goproc = Popen(self.startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate((type+", "+d+", "+targetLoc+", "+self.key).encode()) # Send parameters to AES
        if err != None:  # AES throws error when key is invalid.
            raise ValueError("Key not valid.")

        if endOfFolderList:
            if self.encPop != None:
                self.encPop.dismiss()
                self.encPop = None
            if type == "y":
                self.refreshFiles()
                print("Refreshing files.")

        if type == "n" and op and endOfFolderList:
            mainthread(self.openFileTh(targetLoc, d))

        if self.encPop != None:
            self.encPop.done = True
            print("Done")

        return out

    def getCheckSum(self, location):  # Communicates to BLAKE to get checksum.
        if self.fileSep == "\\":  # If on windows
            goproc = Popen(self.startDir+"BLAKEWin.exe", stdin=PIPE, stdout=PIPE)
        elif self.fileSep == "/":
            goproc = Popen(self.startDir+"BLAKE", stdin=PIPE, stdout=PIPE)

        out, err = goproc.communicate((location).encode())
        if err != None:
            raise ValueError(err)

        return out.decode()

    def getFileExtension(self, fileName):
        return fileName.split(".")[-1].lower()

    def isImage(self, fileName):  # Used to get a file extension from a given file name.
        extension = self.getFileExtension(fileName).lower()
        return bool(extension == "png" or extension == "jpg")

    def getThumbnail(self, fileObj):
        if self.thumbsName not in self.currentDir:    # Only check this when not in the thumbnail folder
            if self.thumbsName not in os.listdir(self.currentDir): # Checks that there is a thumbnail folder in this directory.
                os.makedirs(self.currentDir+self.thumbsName)
                print("Made thumbnail directory since it wasn't there")

        fileObj.thumbDir = self.currentDir+self.thumbsName+self.fileSep+fileObj.hexName
        self.passToPipe("n", fileObj.hexPath, fileObj.thumbDir) # Decrypts thumnail temporarily. Is deleted once program is finished displaying it.
        thumb = Image(source=fileObj.thumbDir)
        return thumb


    # Handles GUI while encrypting a single file, and parses parameters to passToPipe
    def encDecTerminal(self, type, d, targetLoc, isPartOfFolder=False, endOfFolderList=False, newName=None, op=True): # Handels passToPipe and UI while encryption/decryption happens.
        fileName = ""
        if type == "y":     #The file name also needs to be encrypted
            tempDir = d.split(self.fileSep)
            fileName = tempDir[-1]
            targetLoc = targetLoc.split(self.fileSep)
            #replace file name with new hex
            targetLoc[-1] = aesFName.encryptFileName(self.key, fileName)
            thumbTarget = self.fileSep.join(targetLoc[:-1])+self.fileSep+self.thumbsName+self.fileSep+targetLoc[-1]

            popText = "Encrypting..."
            targetLoc = self.fileSep.join(targetLoc)
            if os.path.exists(targetLoc):
                if os.path.isdir(targetLoc):
                    rmtree(targetLoc) # Imported from shutil
                else:
                    os.remove(targetLoc)

        elif type == "n":   #Need to decrypt file name if decrypting
            tempDir = d.split(self.fileSep)
            fileName = tempDir[-1]
            if newName == None:
                targetLoc = targetLoc.split(self.fileSep)
                newName = targetLoc[-1] #Stops you from doing it twice in decrypt()
                targetLoc = self.fileSep.join(targetLoc)
                fileName = newName
            popText = "Decrypting..."

        if not isPartOfFolder:   # If it is a single file, then open a popup. If it isn't, then a popup already exists.
            self.encPop = mainSPops.encDecPop(self, type, popText, [d], [targetLoc], op=op) #self, labText, d, newLoc, **kwargs
            return mainthread(Clock.schedule_once(self.encPop.open, -1)) # Open the popup as soon as possible

        if len(fileName) <= 112: #Any bigger than this and the file name is too long (os throws the error).
            self.encryptProcess = Thread(target=self.passToPipe, args=(type, d, targetLoc, newName, endOfFolderList, op,), daemon=True)
            return self.encryptProcess.start()
        else:
            print("File name too long: ", fileName)
            print("Dismissed?")
            lab = Label(text="File name too long, skipping:\n"+fileName)
            lab.bind(size=info.setter("text_size")) # Wrap to label.
            pop = Popup(title="Invalid file name", content=lab, size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
            pop.open()

    def openFileTh(self, fileLoc, startLoc):   # Creates a thread to open a file (stops program locking up)
        Thread(target=self.openFile, args=(fileLoc, startLoc,), daemon=True).start()

    def openFile(self, location, startLoc):
        locationFolder = location.split(self.fileSep)
        nameOfOriginal = locationFolder[-1]
        locationFolder = self.fileSep.join(locationFolder[:-1])
        startList = os.listdir(locationFolder)
        if self.fileSep == "\\":
            location = location.split("\\")
            location = "/".join(location) # Windows actually accepts forward slashes in terminal
            command = "cmd /k start "+'"" '+'"'+location+'"'+" /D"
        else:
            command = "xdg-open "+'"'+location+'"'      # Quotation marks for if the dir has spaces in it

        startCheckSum = self.getCheckSum(location) # Gets checksum of file before opening.
        os.system(command)# Using the same for both instead of os.startfile because os.startfile doesn't wait for file to close
        # After this line, the file has been closed.
        if os.path.exists(locationFolder):            # If the vault is locked while the file is being edited, then the temporary files get deleted, so check it still exists.
            endList = set(os.listdir(locationFolder)) # Get list of temp files afterwards, and encrypt any new ones (like doing save-as)
            endCheckSum = self.getCheckSum(location)
            print(startCheckSum, "START CHECK SUM")   # For debugging
            print(endCheckSum, "END CHECK SUM")
        else:
            endList = []
            endCheckSum = startCheckSum # Don't try and encrypt files that have been removed.

        diffAdded = [d for d in endList if d not in startList] # Creates an array of differences between the list of files currently in the temp folder, and the original contents of the temp folder.
        tempLoc = startLoc.split(self.fileSep)
        for i in diffAdded:   # Encrypt any extra files in the temp folder that were not there before
            print("Difference found:", i)
            tempLoc = self.fileSep.join(tempLoc[:-1]) # Remove last file name
            tempLoc += self.fileSep+i
            self.encDecTerminal("y", locationFolder+self.fileSep+i, tempLoc)   #Is encrypted when program closes anyway

        if nameOfOriginal in endList:
            print("Original still here")
            if endCheckSum != startCheckSum:
                print("Original file has changed.")
                self.encDecTerminal("y", location, startLoc)

    def onFileDrop(self, window, filePath):  # For draging + dropping files into the window.
        self.checkCanEncrypt(filePath.decode())
        return "Done"

    def decrypt(self, fileObj, op=True):
        if not os.path.isdir(self.osTemp+"FileMate"+self.fileSep):
            os.makedirs(self.osTemp+"FileMate"+self.fileSep)
        fileLoc = self.osTemp+"FileMate"+self.fileSep+fileObj.name  #Place in temporary files where it is going to be stored.
        if os.path.exists(fileLoc) and op:         #Checks file exits already in temp files, so it doesn't have to decrypt again.
            self.openFileTh(fileLoc, fileObj.hexPath)
        else:
            self.encDecTerminal("n", fileObj.hexPath, fileLoc, newName=fileObj.name, op=op)

    def checkDirExists(self, dir):  #Handles UI for checking directory exits when file added.
        if os.path.exists(dir):
            return True
        else:
            self.popup = Popup(title="Invalid", content=Label(text=dir+" - Not a valid directory."), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4))
            self.popup.open()
            return False

    def encDecDir(self, encType, d, targetLoc, op=True): # Encrypt and decrypt folders.
        if self.encPop != None:
            self.encPop.dismiss()
            self.encPop = None

        self.fileList = []
        self.locList = []
        self.encDecDirCore(encType, d, targetLoc)

        if len(self.fileList) < 1:
            return Popup(title="Empty", content=Label(text="This folder is empty..."), size_hint=(.4, .3)).open()

        labText = "Encrypting..."
        if encType == "n":
            labText = "Decrypting..."

        self.encPop = mainSPops.encDecPop(self, encType, labText, self.fileList, self.locList, op=op) #self, labText, fileList, locList, **kwargs
        mainthread(Clock.schedule_once(self.encPop.open, -1))

    def decryptFileToLoc(self, fileObj, button):   # Decrypt a file/folder to a location (just handles the input)
        mainSPops.decryptFileToLocPop(self, fileObj).open()

    def encDecDirCore(self, encType, d, targetLoc): # Enc/decrypts whole directory.
        fs = os.listdir(d)
        targetLoc = targetLoc.split(self.fileSep)
        if encType == "y": # Decrypt folder names
            targetLoc[-1] = aesFName.encryptFileName(self.key, targetLoc[-1])
        else:
            targetLoc[-1] = aesFName.decryptFileName(self.key, targetLoc[-1])
        targetLoc = self.fileSep.join(targetLoc)
        for item in fs:
            if os.path.isdir(d+item):
                self.encDecDirCore(encType, d+item+self.fileSep, targetLoc+self.fileSep+item) #Recursive
            else:
                if encType == "n":
                    name = aesFName.decryptFileName(self.key, item)
                elif encType == "y":
                    name = aesFName.encryptFileName(self.key, item)
                else:
                    name = item
                try:
                    self.createFolders(targetLoc+self.fileSep)
                except PermissionError:
                    pass
                else:
                    self.fileList.append(d+item)
                    self.locList.append(targetLoc+self.fileSep+name)

    def checkCanEncryptCore(self, inp): # Used for adding new files to the vault by the user.
        if self.checkDirExists(inp):
            if os.path.isdir(inp):
                if inp[-1] != self.fileSep:
                    inp += self.fileSep
                inpSplit = inp.split(self.fileSep)
                self.encDecDir("y", inp, self.currentDir+inpSplit[-2])
            else:
                inpSplit = inp.split(self.fileSep)
                self.encDecTerminal("y", inp, self.currentDir+inpSplit[-1])


    def checkCanEncrypt(self, inp):  # Used for adding new files to the vault by the user.
        if "--" in inp: # Multiple files/folders input.
            inp = inp.split("--")
            for d in inp:
                self.checkCanEncryptCore(d) # Actally encrypt/decrypt it.
        else:
            self.checkCanEncryptCore(inp)

        self.resetButtons()


    def createFolders(self, targetLoc):   # Create a folder safely.
        if not os.path.exists(targetLoc):
            os.makedirs(targetLoc)
            if self.thumbsName not in targetLoc: # If in the thumbnails folder, don't make a thumbnails folder.
                os.makedirs(targetLoc+self.thumbsName)


    def clearUpTempFiles(self):     # Deletes temp files when the program is locked.
        print("Deleting temp files.")
        try:
            rmtree(self.osTemp+"FileMate"+self.fileSep) # Imported from shutil
        except:
            print("No temp files.")
