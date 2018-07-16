import os

def listDir(f):
    fs = os.listdir(f)
    count = 0
    listOfFiles = []
    for item in fs:
        if os.path.isdir(f+item):
            listOfFiles.append(item)
    for item in fs:
        if not os.path.isdir(f+item):
            listOfFiles.append(item)
    return listOfFiles

def getPathBack(currentDir):
    tempDir = currentDir.split("\\")
    del tempDir[len(tempDir)-2]
    tempDir = "\\".join(tempDir)
    return tempDir



location = "C:\\"

files = listDir(location)
print(files)
stop = False
while not stop:
    nextFile = 0
    nextFile = str(input("What file next: "))
    if nextFile != "":
        if os.path.isdir(location+nextFile):
            try:
                print(listDir(location+nextFile+"\\"))
                location = location+nextFile+"\\"
            except PermissionError:
                print("hmm")
        else:
            try:
                os.startfile(location+nextFile)
            except FileNotFoundError:
                print("File does not exist.")
    else:
        location = getPathBack(location)
        try:
            print(listDir(location))
        except FileNotFoundError:
            print("hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
        
