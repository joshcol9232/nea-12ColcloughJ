from os import path as osPath
from os import listdir
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


def readConfigFile(configLocation):
    configFile = open(configLocation, "r")
    for line in configFile:
        lineSplit = line.split("--")
        lineSplit[1] = lineSplit[1].replace("\n", "")
        if lineSplit[0] == "vaultDir":
            path = lineSplit[1]
        elif lineSplit[0] == "searchRecursively":
            if lineSplit[1] == "True":
                recurse = True
            elif lineSplit[1] == "False":
                recurse = False
            else:
                raise ValueError("Recursive search settings not set correctly in config file: Not True or False.")
        elif lineSplit[0] == "bluetooth":
            if lineSplit[1] == "True":
                bt = True
            elif lineSplit[1] == "False":
                bt = False
            else:
                raise ValueError("Bluetooth not configured correctly in config file: Not True or False.")

    configFile.close()

    return path, recurse, bt


def runConfigOperations():
    if platform.startswith("win32"): # Find out what operating system is running.
        fileSep = "\\"
    else:          #windows bad
        fileSep = "/"
    osTemp = gettempdir()+fileSep #From tempfile module

    # Get config settings.
    startDir = osPath.dirname(osPath.realpath(__file__))+fileSep
    tempDir = startDir.split(fileSep)
    del tempDir[len(tempDir)-2]
    startDir = fileSep.join(tempDir)
    for i in range(2):
        del tempDir[len(tempDir)-2]
    sharedAssets = fileSep.join(tempDir)
    sharedAssets += "assets"+fileSep+"exports"+fileSep

    path, recurse, bt = readConfigFile(findConfigFile(startDir, fileSep))
    return fileSep, osTemp, startDir, tempDir, path, recurse, bt  # 7 Outputs in total.