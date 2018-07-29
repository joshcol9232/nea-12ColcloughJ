import time, psutil, sys

def getOrdOfInp(keyInput):
    ords = []
    for i in list(keyInput):
       ords.append(ord(i))
    return ords

def getBufferSize(percentage):
    mem = psutil.virtual_memory()
    return int(mem.free * percentage)

def splitBuffer(data):
    chunks = []

    divisions = int(len(data)/16)
    count = 0
    for i in range(divisions):
        segment = data[count:count+16]
        chunk = []
        for i in segment:
            chunk.append(i)
        chunks.append(chunk)
        #print(chunks, "chung")
        count += 1

    for item in chunks:
        while len(item) < 16:
            print("chunk not big enough - adding filler")
            item.append(bin(0))

    return chunks

def addRoundKey(state, roundKey):
    #print(state, roundKey, len(state), len(roundKey))
    for i in range(16):
        state[i] ^= roundKey[i]
    return state

def subBytes(state):
    #       0     1     2     3     4     5     6     7     8     9     a     b     c     d     e     f         - first digit of input
    sBox = [0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76, #00
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0, #10
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15, #20
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75, #30
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84, #40
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF, #50
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8, #60
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2, #70
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73, #80
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB, #90
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79, #a0
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08, #b0
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A, #c0
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E, #d0
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF, #e0
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16] #f0

    for i in range(len(state)-1):
        state[i] = sBox[state[i]]

    return state


def shiftRows(state):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #row1
    temp[0] = state[0] #Mixes it like this:
    temp[1] = state[5] #
    temp[2] = state[10]# 0  4  8 12         0  4  8 12  shifted left by 0
    temp[3] = state[15]# 1  5  9 13  ---->  5  9 13  1  shifted left by 1
    #row2              # 2  6 10 14  ----> 10 14  2  6  shifted left by 2
    temp[4] = state[4] # 3  7 11 15        15  3  7 11  shifted left by 3
    temp[5] = state[9]
    temp[6] = state[14]
    temp[7] = state[3]
    #row3
    temp[8] = state[8]
    temp[9] = state[13]
    temp[10] = state[2]
    temp[11] = state[7]
    #row4
    temp[12] = state[12]
    temp[13] = state[1]
    temp[14] = state[6]
    temp[15] = state[11]

    for i in range(16):
        state[i] = temp[i]

    return state


def mixColumns():
    pass


# def checkBytesNotInteger(chunk):
#     tempChunk = []
#     for item in chunk:
#         if type(item) == type(0):
#             tempItem = bytes(item)
#
#         else:
#             print("AAAA")


def encrypt(state, key, regularRounds):
    state = addRoundKey(state, key)
    for i in range(regularRounds):
        state = subBytes(state)
        state = shiftRows(state)
        #state = mixColumns() ##
        state = addRoundKey(state, key)
    #Last round
    state = subBytes(state)
    state = shiftRows(state)
    state = addRoundKey(state, key)

    return state


def main():
    key = getOrdOfInp("mynamejeffeleven")
    #f = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/smile.bmp"
    #w = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/hmmm.txt"
    #f = "/run/media/josh/Storage/kali-linux-2018.1-amd64.iso"
    f= "/run/media/josh/USB/IMPORTANT IMAGES/Pics/Important images/bil/bil/Bill Bailey © William Shaw_0.jpg"

    perc = 0.1
    bufferSize = getBufferSize(perc)
    print("Using "+str(int(perc*100))+"% of free memory:", bufferSize)
    key = getOrdOfInp("mynamejeffeleven")
    fo = open(f, "rb")
    buff = fo.read(bufferSize)
    #fw = open(w, "wb")
    while buff:
        print(sys.getsizeof(buff))
        buff = splitBuffer(buff)
        print(sys.getsizeof(buff))
        for i in range(len(buff)-1):
            buff[i] = encrypt(buff[i], key, 9)

        print("done chunk")
        print(buff)
        #buff = 0
        buff = fo.read(bufferSize)


    fo.close()
    # fw.close()




if __name__ == "__main__":
    main()
