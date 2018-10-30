global k

k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,    #Round constants
     0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
     0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
     0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
     0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
     0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
     0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
     0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
     0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
     0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
     0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

def makeBitArray(inp):
    bitArray = []
    #print(inp, "INP")
    for element in inp:
        tempByte = intToBits(element)
        for bit in tempByte:
            bitArray.append(bit)
    return bitArray

def intToBits(inp, bitLength=8):
    tempByte = []
    for x in range(bitLength):
        tempByte.append(0)  #Initialize
    for i in range(bitLength):
        tempByte[(bitLength-1)-i] = (inp >> i) & 1 #Goes through bits backwards so append backwards.
    return tempByte

def bitsToInt(inp):
    byteString = "".join(str(i) for i in inp)
    return int(byteString, 2)


def pad(inpBits):   #https://csrc.nist.gov/csrc/media/publications/fips/180/4/archive/2012-03-06/documents/fips180-4.pdf section 5.1
    l = len(inpBits)
    if (l % 512 == 0) and l != 0:
        return inpBits
    else:
        inpBits.append(1) #Add one to the end of the message
        # 448%512 = k + l + 1
        #k = 448-(l+1)
        k = 0
        while ((l+1+k)-448)%512 != 0:   #Smallest value of k that makes that work
            k += 1
        for i in range(k):
            inpBits.append(0)
        #Pad with message length expessed as 64 bit binary number
        lengthBits = intToBits(l, 64)
        for x in lengthBits:
            inpBits.append(x)
        return inpBits


def checkLessThan32(num):
    if num < 32:
        return num
    else:
        return num - 32

def checkShiftInBounds(word, num):
    if (num < 0) or (num >= 32):
        return 0
    else:
        return word[num]


def notArray(array, l=32):
    temp = []
    for x in range(l):
        temp.append(0)
    for i in range(l):
        if array[i] == 1:
            temp[i] = 0
        else:
            temp[i] = 1
    return temp

def xorArrays(array1, array2):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(32):
        temp[i] = array1[i] ^ array2[i]
    return temp

def andBitArrays(array1, array2):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(32):
        temp[i] = array1[i] & array2[i]
    return temp

def orBitArrays(array1, array2):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(array1)-1):
        temp[i] = array1[i] | array2[i]
    return temp

def RotL(word, amount):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #32Bits
    for i in range(32):
        temp[i] = word[checkLessThan32(i+amount)]
    return temp

def RotR(word, amount):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #32Bits

    for i in range(32):
        temp[i] = word[checkLessThan32(i-amount)]
    return temp

def addMod2W(array1, array2, W=32):
    if len(array1) != len(array2):
        raise IndexError("Arrays not same size - ", array1, array2)
    result = (bitsToInt(array1) + bitsToInt(array2)) % 2**W
    return intToBits(result, 32)

def ShR(x, n):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(32):
        temp[i] = checkShiftInBounds(x, i-n)
    return temp

def ShL(x, n):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(32):
        temp[i] = checkShiftInBounds(x, i+n)
    return temp

def SigExpansion0(x):
    return xorArrays(xorArrays(RotR(x, 7), RotR(x, 18)), ShR(x, 3))

def SigExpansion1(x):
    return xorArrays(xorArrays(RotR(x, 17), RotR(x, 19)), ShR(x, 10))

def Sig0(x):
    return xorArrays(xorArrays(RotR(x, 2), RotR(x, 13)), RotR(x, 22))

def Sig1(x):
    return xorArrays(xorArrays(RotR(x, 6), RotR(x, 11)), RotR(x, 25))

def Ch(x, y, z):
    return xorArrays(andBitArrays(x, y), andBitArrays(notArray(x), z))

def Maj(x, y, z):
    return xorArrays(xorArrays(andBitArrays(x, y), andBitArrays(x, z)), andBitArrays(y, z))

def sha256(inp):
    #Initial hash values - https://csrc.nist.gov/csrc/media/publications/fips/180/4/archive/2012-03-06/documents/fips180-4.pdf section 5.3.3
    hList = [0x6a09e667,    # H0
             0xbb67ae85,    # H1
             0x3c6ef372,    # H2
             0xa54ff53a,    # H3
             0x510e527f,    # H4
             0x9b05688c,    # H5
             0x1f83d9ab,    # H6
             0x5be0cd19]    # H7

    #https://en.wikipedia.org/wiki/SHA-2

    bits = makeBitArray(inp)
    bits = pad(bits)
    bits = [bits[x:x+32] for x in range(0, len(bits), 32)]  #Split padded message into 32 bit words
    bits = bits+[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for y in range(48)]
    #Main part

    for x in range(16, 64): #Expand current bits to be 64 words
        s0 = SigExpansion0(bits[x-15])
        s1 = SigExpansion1(bits[x-2])
        bits[x] = addMod2W(addMod2W(addMod2W(bits[x-16], s0), bits[x-7]), s1)


    a = intToBits(hList[0], 32)
    b = intToBits(hList[1], 32)
    c = intToBits(hList[2], 32)
    d = intToBits(hList[3], 32)
    e = intToBits(hList[4], 32)
    f = intToBits(hList[5], 32)
    g = intToBits(hList[6], 32)
    h = intToBits(hList[7], 32)

    for i in range(64):
        S1 = Sig1(e)
        ch = Ch(e, f, g)
        temp1 = addMod2W(addMod2W(addMod2W(addMod2W(h, S1), ch), intToBits(k[i], 32)), bits[i])
        S0 = Sig0(a)
        maj = Maj(a, b, c)
        temp2 = addMod2W(S0, maj)

        h = g
        g = f
        f = e
        e = addMod2W(d, temp1)
        d = c
        c = b
        b = a
        a = addMod2W(temp1, temp2)

    h0 = addMod2W(intToBits(hList[0], 32), a)
    h1 = addMod2W(intToBits(hList[1], 32), b)
    h2 = addMod2W(intToBits(hList[2], 32), c)
    h3 = addMod2W(intToBits(hList[3], 32), d)
    h4 = addMod2W(intToBits(hList[4], 32), e)
    h5 = addMod2W(intToBits(hList[5], 32), f)
    h6 = addMod2W(intToBits(hList[6], 32), g)
    h7 = addMod2W(intToBits(hList[7], 32), h)

    resultBits = h0+h1+h2+h3+h4+h5+h6+h7
    resultBytes = [resultBits[x:x+8] for x in range(0, len(resultBits), 8)]
    result = []
    for byte in resultBytes:
        result.append(bitsToInt(byte))
    return result

def getSHA128of16(data):
    #print("getShakey", inpKey)
    out = sha256(data)
    half1, half2 = out[:16], out[16:]
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(16):
        temp[i] = half1[i] ^ half2[i]   #XOR both halves to get a 128 bit output for 128 bit AES

    # result = ""
    # for x in temp:
    #     result += hex(x)

    return temp

def roundUpOnly(fl):    #for rounding up numbers only. Accepts float
    fl = str(fl)
    temp = fl.split(".")
    if temp[1] != 0:
        return int(temp[0])+1
    else:
        return int(temp[0])

def xorBlocks(inp):
    while len(inp) != 1:
        inp[0] = xorArrays(inp[0], inp[1])
        del inp[1]
    return inp

def feed(data):         #accepts string
    if len(data) > 16:
        arrayOfOut = []
        for i in range(roundUpOnly(len(data)/16)):
            arrayOfOut.append(sha256(data[(i*16):((i+1)*16)]))
        #xor each 32 bytes with each other to produce a 32 byte output
        return xorBlocks(arrayOfOut)

    else:
        return sha256(data)


if __name__ == "__main__":
    print(len("123456789012345678901234567890121234567890123456789012345689012 "))
    geg = feed("123456789012345678901234567890121234567890123456789012345689012")
    for i in geg:
        print(i, len(i))
