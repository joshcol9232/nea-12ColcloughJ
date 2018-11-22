package main

import (
  "fmt"
  "math"
  "os"
  "io"
  "runtime"
)

// Inital constants.
var k = [8]uint64 {0x6A09E667F3BCC908,
                   0xBB67AE8584CAA73B,
                   0x3C6EF372FE94F82B,
                   0xA54FF53A5F1D36F1,
                   0x510E527FADE682D1,
                   0x9B05688C2B3E6C1F,
                   0x1F83D9ABFB41BD6B,
                   0x5BE0CD19137E2179}

var sigma = [12][16]uint64 {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15},
                            {14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3},
                            {11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4},
                            {7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8},
                            {9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13},
                            {2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9},
                            {12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11},
                            {13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10},
                            {6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5},
                            {10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0},
                            {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15},
                            {14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3}}

// Research: https://tools.ietf.org/pdf/rfc7693.pdf

func check(e error) {     //Used for checking errors when reading/writing to files.
  if e != nil {
    panic(e)
  }
}



func rotR64(in uint64, n int) uint64 {  // For 64 bit words
  return (in >> uint(n)) ^ (in << (64 - uint(n)))
}

func mix(v [16]uint64, a, b, c, d int, x, y uint64) [16]uint64 {
  v[a] = v[a] + v[b] + x
  v[d] = rotR64((v[d] ^ v[a]), 32)

  v[c] = v[c] + v[d]
  v[b] = rotR64((v[b] ^ v[c]), 24)

  v[a] = v[a] + v[b] + y
  v[d] = rotR64((v[d] ^ v[a]), 16)

  v[c] = v[c] + v[d]
  v[b] = rotR64((v[b] ^ v[c]), 63)

  return v
}


func get64(in []uint64) uint64 {  // Gets a full 64-bit word from a list of 8 64-bit bytes.
  return uint64(in[0] ^ (in[1] << 8) ^ (in[2] << 16) ^ (in[3] << 24) ^ (in[4] << 32) ^ (in[5] << 40) ^ (in[6] << 48) ^ (in[7] << 56))
}


func compress(h [8]uint64, block [128]uint64, t int, lastBlock bool) [8]uint64 {  // Compressing function
  var v = [16]uint64{} // Current vector
  for i := 0; i < 8; i++ {
    v[i] = h[i]
    v[i+8] = k[i]
  }
  v[12] = v[12] ^ uint64(math.Mod(float64(t), 18446744073709552000)) //  2 ^ 64 = 18446744073709552000
  v[13] = v[13] ^ (uint64(t) >> 64)

  if lastBlock {
    v[14] = ^v[14] // NOT
  }

  var m [16] uint64
  for i := 0; i < 16; i++ {
    m[i] = get64(block[i*8:(i*8)+8])
  }
  for i := 0; i < 12; i++ {
    sigRow := sigma[i]
    // Mix
    v = mix(v, 0, 4,  8, 12, m[sigRow[0]], m[sigRow[1]])
    v = mix(v, 1, 5,  9, 13, m[sigRow[2]], m[sigRow[3]])
    v = mix(v, 2, 6, 10, 14, m[sigRow[4]], m[sigRow[5]])
    v = mix(v, 3, 7, 11, 15, m[sigRow[6]], m[sigRow[7]])

    v = mix(v, 0, 5, 10, 15, m[sigRow[ 8]], m[sigRow[ 9]])   // Rows have been shifted
    v = mix(v, 1, 6, 11, 12, m[sigRow[10]], m[sigRow[11]])
    v = mix(v, 2, 7,  8, 13, m[sigRow[12]], m[sigRow[13]])
    v = mix(v, 3, 4,  9, 14, m[sigRow[14]], m[sigRow[15]])
  }

  for i := 0; i < 8; i++ {
    h[i] ^= v[i]
    h[i] ^= v[i+8]
  }

  return h
}

func getNiceOutput(h [8]uint64) [8][8]byte {
  var out [8][8]byte
  for i := 0; i < 8; i++ {
    for j := 8; j != 0; j-- {
      out[i][j-1] = byte(((h[i] << uint64(64 - uint64((j)*8))) & 0xFFFFFFFFFFFFFFFF) >> 56)
    }
  }
  return out
}

// w = 64
// r = 12 rounds
// 16 64-bit words per block.
// 512 bit
func BLAKE2b(dataIn []byte, hashL int) [8][8]byte {  // data is split into 16 64-bit words.
  var data [][128]uint64
  data, l := splitData(dataIn)

  h := k  // Initialize h0-7 with initial values.
  h[0] = h[0] ^ (0x01010000 ^ uint64(hashL)) // Not using a key

  if len(data) > 1 {
    for i := 0; i < len(data)-2; i++ {  // Do all blocks apart from last one.
      h = compress(h, data[i], (i+1)*128, false)  //128 block bytes = 16 64-bit words.
    }
  }

  h = compress(h, data[len(data)-1], l, true)
  // Get the output as hashL bytes of the little endian of h
  out := getNiceOutput(h)
  return out
}

// Functions to manage input to blake2b
func splitData(data []byte) ([][128]uint64, int) {  // Data will be given to the program in bytes.
  var l int = len(data)
  var out = [][128]uint64{{}}
  count2 := 0
  for i := range data {
    count1 := 0
    if (math.Mod(float64(i), 128) == 0) && (i != 0) {
      count1++
      count2 = 0
      out = append(out, [128]uint64{0})
    }
    fmt.Println(out, "out")
    out[count1][count2] = uint64(data[i])

    count2++
  }
  if len(out) == 0 {
    out = [][128]uint64{{0}}
  }
  return out, l
}

func getNumOfCores() int {  //Gets the number of cores so it determines buffer size.
  maxProcs := runtime.GOMAXPROCS(0)
  numCPU := runtime.NumCPU()
  if maxProcs < numCPU {
    return maxProcs
  }
  return numCPU
}

func byte128To64(data []byte) [128]uint64 {
  var out = [128]uint64{}
  for i := range data {
    out[i] = uint64(data[i])
  }
  return out
}

func BLAKEchecksum(f string, hashL int) [8][8]byte {
  // Going to feed in the chunks very similar to AES.
  h := k  // Initialize h0-7 with initial values.
  h[0] = h[0] ^ (0x01010000 ^ uint64(hashL)) // Not using a key

  a, err := os.Open(f)    // Open original file to get statistics
  check(err)
  aInfo, err := a.Stat()  // Get statistics
  check(err)

  fileSize := int(aInfo.Size()) // Get size of original file

  var bufferSize int = 65536*getNumOfCores()  //Get the buffer size

  if fileSize < bufferSize {    // If the buffer size is larger than the file size, just read the whole file.
    bufferSize = fileSize
    fmt.Println("READING WHOLE FILE")
  }

  var buffCount int = 0   // Keeps track of how far through the file we are
  var bytesFed int = 0

  for buffCount < fileSize {
    if bufferSize > (fileSize - buffCount) {
      bufferSize = fileSize - buffCount
      fmt.Println("BUFFER SIZE CHANGED")
    }
    fmt.Printf("%x H\n", h)
    buff := make([]byte, bufferSize)  // Make a slice the size of the buffer
    _, err := io.ReadFull(a, buff) // Read the contents of the original file, but only enough to fill the buff array.
                                   // The "_" tells go to ignore the value returned by io.ReadFull, which in this case is the number of bytes read.
    check(err)

    //fmt.Println(buff, "buff")
    currBuff, _ := splitData(buff)
    //fmt.Println(currBuff, len(currBuff))
    if len(currBuff) > 1 {
      for i := 0; i < len(currBuff)-1; i++ {
        bytesFed += 128
        h = compress(h, currBuff[i], bytesFed, false)
      }
    }
    if fileSize - bytesFed <= 128 {
      fmt.Println("LAST EXECUTED", fileSize, bytesFed)
      bytesFed += 128
      //fmt.Println(currBuff[len(currBuff)-1])
      h = compress(h, currBuff[len(currBuff)-1], fileSize, true)
    } else {
//      fmt.Println("Bytes fed in:", 128+(lastI*128)+buffCount)
      bytesFed += 128
      h = compress(h, currBuff[len(currBuff)-1], bytesFed, false)
    }

    buffCount += bufferSize
  }
  fmt.Println(buffCount, fileSize)
  a.Close()

  return getNiceOutput(h)
}


func main() {
//  data := []byte("")
//  h := BLAKE2b(data, 64)
//  fmt.Println(h)
//  for i := range h {
//    fmt.Printf("%x\n", h[i])
//  }

  f := "/home/josh/e.txt"
  //f := "/home/josh/geg.txt"
  //f := "/home/josh/mandelbrot high.png"
  fmt.Printf("%x", BLAKEchecksum(f, 64))
}
