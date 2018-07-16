import time

def getFileData(Dir):
    fo = open(Dir, "rb")
    eachByte = []
    for line in fo:
        for item in line:
            eachByte.append(item)

    fo.close()
    return eachByte

def splitIntoChunks(data):
    chunks = []
    divisions = int(len(data)/16)
    count = 0
    for i in range(divisions):
        chunks.append(data[count:count+16])
        count += 1

    for item in chunks:
        while len(item) < 16:
            print("chunk not big enough - adding filler")
            item.append(0)

    return chunks

def xorWithKey(chunks, key):
    xor = []
    for chunk in chunks:
        newChunk = []
        for i in range(len(chunk)-1):
            newChunk.append(chunk[i] ^ key[i])
        xor.append(newChunk)

    return xor


start = time.time()
data = getFileData("smile.bmp")
chunks = splitIntoChunks(data)
print(chunks)
print("Took:", str(time.time()-start), "seconds to split.")

keyInput = "mynamejeffeleven"
key = []
for i in list(keyInput):
    key.append(ord(i))

print(key)

# xorChunks = xorWithKey(chunks, key)
# print(xorChunks)
