import time
import io


##def splitIntoChunks(data):
##    chunks = []
##    divisions = int(len(data)/16)
##    count = 0
##    for i in range(divisions):
##        chunks.append(data[count:count+16])
##        count += 1
##
##    for item in chunks:
##        while len(item) < 16:
##            print("chunk not big enough - adding filler")
##            item.append(0)
##
##    return chunks

def xorWithKey(chunk, key):
    xor = []
    for i in range(len(chunk)-1):
        xor.append(chunk[i] ^ key[i])

    return xor


f = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/smile.bmp"
w = "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/pictures/hmmm.txt"
#f = "/run/media/josh/Storage/kali-linux-2018.1-amd64.iso"

def makeKey(keyInput):
    key = []
    for i in list(keyInput):
       key.append(ord(i))
    return key

def main():
    key = makeKey("mynamejeffeleven")
    fo = open(f, "rb")
    data = fo.read(16)
    fw = open(w, "wb")
    while data:
        chunk = []
        for byte in data:
            chunk.append(byte)
        tempData = xorWithKey(chunk, key)
        for i in tempData:
            fw.write(bytes(i))
        data = fo.read(16)


    fo.close()
    fw.close()



if __name__ == "__main__":
    main()


##start = time.time()
##data = getFileData("/home/josh/VirtualBox VMs/bob/bob.vdi")
##chunks = splitIntoChunks(data)
##print("Took:", str(time.time()-start), "seconds to split.")
##

##
##print(key)

# xorChunks = xorWithKey(chunks, key)
# print(xorChunks)
