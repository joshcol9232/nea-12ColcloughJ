cpdef list quickSortSize(list fileObjects):
    cdef list left = []
    cdef list right = []  #Make seperate l+r lists, and add on at the end.
    cdef list middle = []
    cdef float pivotSize
    if len(fileObjects) > 1:
        pivot = fileObjects[int(len(fileObjects)/2)]
        if pivot.rawSize == " -":
            pivotSize = 0
        else:
            pivotSize = pivot.rawSize

        for i in fileObjects:
            if i.rawSize == " -":
                left.append(i)
            elif i.rawSize < pivotSize:
                left.append(i)
            elif i.rawSize > pivotSize:
                right.append(i)
            else:
                middle.append(i)
        return quickSortSize(left)+middle+quickSortSize(right)
    else:
        return fileObjects

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
