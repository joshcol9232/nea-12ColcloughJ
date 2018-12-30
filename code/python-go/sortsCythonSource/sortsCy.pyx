cpdef int compareStrings(fileObj, string2, fileObjects=True):
    cdef int count = 0

    if fileObjects:
        string1 = fileObj.name
    else:
        string1 = fileObj

    while not (count >= len(string1) or count >= len(string2)):
        if ord(string2[count].lower()) < ord(string1[count].lower()):
            return 1
        elif ord(string2[count].lower()) > ord(string1[count].lower()):
            return 0
        else:
            if ord(string2[count]) < ord(string1[count]):    #if the same name but with capitals - e.g (Usb Backup) and (usb backup)
                return 1
            elif ord(string2[count]) > ord(string1[count]):
                return 0
            else:
                if string2 == string1:
                    return 2
                else:
                    count += 1
    if len(string1) > len(string2):
        return 1
    elif len(string1) < len(string2):
        return 0
    else:
        raise ValueError("Two strings are the same in compareStrings.")

cpdef list quickSortAlph(list myList, fileObjects=True):  #Quick sorts alphabetically
    cdef list left = []
    cdef list right = []  #Make seperate l+r lists, and add on at the end.
    cdef list middle = []
    if len(myList) > 1:
        pivot = myList[int(len(myList)/2)]
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

        return quickSortAlph(left, fileObjects)+middle+quickSortAlph(right, fileObjects)
    else:
        return myList

cpdef list quickSortTuples(list tuples):  #Quick sorts tuples (for search results).
    cdef list left = []
    cdef list right = []  #Make seperate l+r lists, and add on at the end.
    cdef list middle = []
    cdef float pivot
    if len(tuples) > 1:
        pivot = tuples[int(len(tuples)/2)][0]
        for i in tuples:
            if i[0] < pivot:
                left.append(i)
            elif i[0] > pivot:
                right.append(i)
            else:
                middle.append(i)
        return quickSortTuples(left)+middle+quickSortTuples(right)
    else:
        return tuples
