import time

def getChunk(Dir):
    fo = open(Dir, "rb")
    chunk = []
    return fo.seek(16)
    
    return chunk
    

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

def xorWithKey(chunks, key):
    xor = []
    for chunk in chunks:
        newChunk = []
        for i in range(len(chunk)-1):
            newChunk.append(chunk[i] ^ key[i])
        xor.append(newChunk)

    return xor


f = "E:\\nea-12ColcloughJ-master\\code\\python\\testing\\Aes\\pictures\\smile.png"
print(getChunk(f))

##start = time.time()
##data = getFileData("/home/josh/VirtualBox VMs/bob/bob.vdi")
##chunks = splitIntoChunks(data)
##print("Took:", str(time.time()-start), "seconds to split.")
##
##keyInput = "mynamejeffeleven"
##key = []
##for i in list(keyInput):
##    key.append(ord(i))
##
##print(key)

# xorChunks = xorWithKey(chunks, key)
# print(xorChunks)
