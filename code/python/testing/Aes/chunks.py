import time
import psutil
import math

def xorWithKey(chunk, key):
    xor = []
    for i in range(len(chunk)-1):
        xor.append(chunk[i] ^ key[i])

    return xor

def makeKey(keyInput):
    key = []
    for i in list(keyInput):
       key.append(ord(i))
    return key

def getBufferSize(percentage):
     mem = psutil.virtual_memory()
     return int(mem.free * percentage)

def splitBuffer(data):
   chunks = []
   divisions = int(len(data)/16)
   count = 0
   for i in range(divisions):
       chunks.append(data[count:count+16])
       count += 1

   for item in chunks:
       while len(item) < 16:
           print("chunk not big enough - adding filler")
           item.append(bin(0))

   return chunks

def checkBytesNotInteger(chunk):
    tempChunk = []
    for item in chunk:
        if type(item) == type(0):
            tempItem = bytes(item)

        else:
            print("AAAA")



def main():
    f = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/smile.bmp"
    w = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/hmmm.txt"
    #f = "/run/media/josh/Storage/kali-linux-2018.1-amd64.iso"

    perc = 0.1
    bufferSize = getBufferSize(perc)
    print("Using "+str(int(perc*100))+"% of memory:", bufferSize)
    key = makeKey("mynamejeffeleven")
    fo = open(f, "rb")
    data = fo.read(bufferSize)
    fw = open(w, "wb")
    while data:
        #important bit
        buff = []
        for byte in data:
            buff.append(byte)

        print(data)
        chunks = splitBuffer(buff)
        print(chunks)


        for chunk in chunks:
            checkBytesNotInteger(chunk)
            tempData = xorWithKey(chunk, key)
            for i in tempData:
                fw.write(i)


        data = fo.read(bufferSize)


    fo.close()
    fw.close()



if __name__ == "__main__":
    main()
