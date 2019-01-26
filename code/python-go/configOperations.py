from os import path as osPath
from os import listdir, makedirs
from sys import platform
from tempfile import gettempdir

def findConfigFile(startDir, fileSep):
    config = None
    if fileSep == "/":
        try:
            home = listdir(osPath.expanduser("~/.config/FileMate/"))
        except:
            print("No config file in .config")
        else:
            if "config" in home:
                config = osPath.expanduser("~/.config/FileMate/config")

    if config == None:
        try:
            configFile = open(startDir+"config.cfg", "r")
        except Exception as e:
            raise FildNotFoundError("No config file found. Refer to the README if you need help.")
        else:
            configFile.close()
            config = startDir+"config.cfg"

    return config


def readConfigFile(configLocation=None, lineNumToRead=None, fSep=None, startDir=None):
    if fSep == None:
        fSep = getFileSep()
    if configLocation == None:
        fSep = getFileSep()
        configLocation = findConfigFile(getStartDir(fSep)[0], fSep)

    configFile = open(configLocation, "r")
    if lineNumToRead == None:
        for line in configFile:
            lineSplit = line.split("--")
            nl = "\n"
##            if fSep == "\\":
##                nl = "\r\n"
##            print("\\"+nl)
            lineSplit[1] = lineSplit[1].replace(nl, "")
            if lineSplit[0] == "vaultDir":
                path = lineSplit[1]
            elif lineSplit[0] == "searchRecursively":
                if lineSplit[1] == "True":
                    recurse = True
                elif lineSplit[1] == "False":
                    recurse = False
                else:
                    print(lineSplit[1])
                    raise ValueError("Recursive search settings not set correctly in config file: Not True or False.")
            elif lineSplit[0] == "bluetooth":
                if lineSplit[1] == "True":
                    bt = True
                elif lineSplit[1] == "False":
                    bt = False
                else:
                    raise ValueError("Bluetooth not configured correctly in config file: Not True or False.")

        configFile.close()

        if (path[0] != fSep and fSep == "/") or (path[1] != ":" and fSep == "\\"):  # If vaultDir done relatively, then get path relative to the folder the program is in, rather than searching the folder.
            if startDir == None:
                startDir = osPath.dirname(osPath.realpath(__file__))+fSep
            startDir = startDir.split(fSep)
            path = fSep.join(startDir[:-4])+fSep+path # Removes "" and nea-12ColcloughJ/code/python-go folder names from list, then adds the Vault folder name to the end.
            if path[-1] != fSep:
                path += fSep # End with file separator

        return path, recurse, bt

    else:
        lineSplit = configFile.readlines()[lineNumToRead].split("--")
        lineSplit[1] = lineSplit[1].replace("\n", "")
        return lineSplit[1]

def getFileSep():
    if platform.startswith("win32"): # Find out what operating system is running.
        return "\\"
    else:
        return "/"

def getStartDir(fileSep=None):
    if fileSep == None:
        fileSep = getFileSep()
    startDir = osPath.dirname(osPath.realpath(__file__))+fileSep
    tempDir = startDir.split(fileSep)
    for i in range(2):
        del tempDir[-2]
    return startDir, fileSep.join(tempDir)+fileSep+"assets"+fileSep+"exports"+fileSep


def editConfTerm(term, newContent, config):  # Edits a given term in the config.cfg file.
    with open(config, "r") as conf:
        confContent = conf.readlines()

    for i in range(len(confContent)):
        a = confContent[i].split("--")
        if term == a[0]:
            a[1] = newContent+"\n"
            confContent[i] = "--".join(a)

    with open(config, "w") as confW:
        confW.writelines(confContent)

def dirInputValid(inp, fileSep):
    valid = bool((inp[0] == fileSep) and ("\n" not in inp))       #If it starts with the file separator and doesn't contain any new lines, then it is valid for now.
    inp = inp.split(fileSep)
    focusIsSlash = False
    for item in inp:            #Checks for multiple file separators next to each other, as that would be an invalid folder name.
        if item == "":
            if focusIsSlash:
                valid = False
            focusIsSlash = True
        else:
            focusIsSlash = False
    return valid

def changeVaultLoc(inp, fileSep, config):      #Sorts out the UI while the vault location is changed.
    if inp != "":
        if dirInputValid(inp, fileSep):
            if osPath.exists(inp) and osPath.isdir(inp):
                editConfTerm("vaultDir", inp, config)
            else:
                makedirs(inp)
                if inp[-1] != fileSep:
                    inp += fileSep
                editConfTerm("vaultDir", inp, config)

            return True

    return False


def runConfigOperations():
    fileSep = getFileSep()
    osTemp = gettempdir()+fileSep #From tempfile module
    # Get config settings.
    startDir, sharedAssets = getStartDir(fileSep)

    configLoc = findConfigFile(startDir, fileSep)
    path, recurse, bt = readConfigFile(configLoc, fSep=fileSep, startDir=startDir)
    return fileSep, osTemp, startDir, sharedAssets, path, recurse, bt, configLoc  # 8 Outputs in total.
