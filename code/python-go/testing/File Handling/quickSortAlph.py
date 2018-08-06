import os

def List(dir):
    fs = os.listdir(dir)
    count = 0
    listOfFiles = []
    for item in fs:
        if os.path.isdir(dir+item):
            listOfFiles.append(item)
    for item in fs:
        if not os.path.isdir(dir+item):
            listOfFiles.append(item)
    return listOfFiles

def quickSortAlphabetical(myList):
    if len(myList) > 1:
        left = []
        right = []  #Make seperate l+r lists, and add on at the end.
        middle = []
        pivot = myList[int(len(myList)/2)]
        for item in myList:
            compared = False
            count = 0
            while not compared:
                print(item, count)
                if count == len(item):
                    compared = True
                else:
                    if ord(item[count].lower()) < ord(pivot[count].lower()):
                        left.append(item)
                        compared = True
                    elif ord(item[count].lower()) > ord(pivot[count].lower()):
                        right.append(item)
                        compared = True
                    else:
                        if item == pivot:
                            middle.append(item)
                            compared = True
                        else:
                            count += 1

        return quickSortAlphabetical(left)+middle+quickSortAlphabetical(right)
    else:
        return myList

files = ["kaine", "never", "goes", "to", "school", "kayak", "bean", "goal", "kalinka", "bob", "spoop"]
print(quickSortAlphabetical(files))
print(files)
