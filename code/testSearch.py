def compareStringsSearch(fileObj, string2, fileObjects=True):



def quickSortSearch(myList, searchItem, fileObjects=True):  #Quick sorts alphabetically
    left = []
    right = []  #Make seperate l+r lists, and add on at the end.
    middle = []
    if len(myList) > 1:
        pivot = searchItem
        for item in myList:
            if fileObjects:
                leftSide = compareStrings(pivot, item.name)
            else:
                leftSide = compareStrings(pivot, item, False)
            if leftSide == 2:
                middle.append(item)
            elif leftSide == 1:
                left.append(item)
            elif leftSide == 0:
                right.append(item)

        return quickSortSearch(left, item, fileObjects)+middle+quickSortSearch(right, item, fileObjects)
    else:
       return myList


def binarySearch(myList, item, fileObjects=True):
    mid = int(len(myList)/2)
    if fileObjects:
        name = myList[mid].name
    else:
        name = myList[mid]
    print(name)

    if len(myList) == 1 and name != item:
        return "Not found."
    else:
        if name == item:
            return item, "Found"
        elif name > item:
            return binarySearch(myList[:mid], item, fileObjects) # If middle bigger than item, look through left side.
        elif name < item:
            return binarySearch(myList[mid:], item, fileObjects) # If middle less than item, look through right side.


import os
L = os.listdir("/home/josh/Important images/bil/")
searchItem = "images (69).jpg"
L = quickSortSearch(L, searchItem, False)
print(L)
#print(binarySearch(L, "1_Bill-Bailey.jpg", fileObjects=False))
