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

def fileNav(fileList, currentLoc):
    print(fileList)
    stop = False
    while not stop:
        nextFile = 0
        nextFile = input("What file next (or stop): ")
        try:
            nextFile = int(nextFile)
        except ValueError:
            if str(nextFile).lower() == "stop":
                stop = True
            elif 
        if not stop:
            if os.path.isdir(currentLoc+nextFile):
                currentLoc = currentLoc+nextFile+"\\"
                print(listDir(currentLoc))
            else:
                os.startfile(currentLoc+nextFile)
                print(listDir(currentLoc))

f = "D:\\blueboi\\"
if not os.path.exists(f):
    os.makedirs(f)

fileNav(listDir(f), f)
