# Since compareStrings will be called a lot, i will define as cpdef for speeeed
cpdef int compareStrings(fileObj, string2):
    cdef int count = 0
    while not (count >= len(fileObj.name) or count >= len(string2)):
        if ord(string2[count].lower()) < ord(fileObj.name[count].lower()):
            return 1
        elif ord(string2[count].lower()) > ord(fileObj.name[count].lower()):
            return 0
        else:
            if ord(string2[count]) < ord(fileObj.name[count]):    #if the same name but with capitals - e.g (Usb Backup) and (usb backup)
                return 1
            elif ord(string2[count]) > ord(fileObj.name[count]):
                return 0
            else:
                if string2 == fileObj.name:
                    return 2
                else:
                    count += 1
    if len(fileObj.name) > len(string2):
        return 1
    elif len(fileObj.name) < len(string2):
        return 0
    else:
        raise ValueError("Two strings are the same in compareStrings.")

cpdef list quickSortAlph(list myList, int fileObjects=True):  #Quick sorts alphabetically
    cdef list left = []
    cdef list right = []  #Make seperate l+r lists, and add on at the end.
    cdef list middle = []
    if len(myList) > 1:
        pivot = myList[int(len(myList)/2)]
        for item in myList:
            if fileObjects:
                leftSide = compareStrings(pivot, item.name)
            else:
                leftSide = compareStrings(pivot, item)
            if leftSide == 2:
                middle.append(item)
            elif leftSide == 1:
                left.append(item)
            elif leftSide == 0:
                right.append(item)

        return quickSortAlph(left, fileObjects)+middle+quickSortAlph(right, fileObjects)
    else:
        return myList


cpdef list quickSortSize(list fileObjects):
    cdef list left = []
    cdef list right = []  #Make seperate l+r lists, and add on at the end.
    cdef list middle = []
    if len(fileObjects) > 1:
        pivotSize = fileObjects[int(len(fileObjects)/2)].rawSize
        for i in fileObjects:
            if i.rawSize < pivotSize:
                left.append(i)
            elif i.rawSize > pivotSize:
                right.append(i)
            else:
                middle.append(i)
        return quickSortSize(left)+middle+quickSortSize(right)
    else:
        return fileObjects