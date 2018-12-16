// Package blake
package main

import (
  "fmt"
  "math"
  "os"
  "io"
  "io/ioutil"
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


func blakeCompress(h [8]uint64, block []uint64, t int, lastBlock bool) [8]uint64 {  // Compressing function
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
    // Mix
    v = mix(v, 0, 4,  8, 12, m[sigma[i][0]], m[sigma[i][1]])
    v = mix(v, 1, 5,  9, 13, m[sigma[i][2]], m[sigma[i][3]])
    v = mix(v, 2, 6, 10, 14, m[sigma[i][4]], m[sigma[i][5]])
    v = mix(v, 3, 7, 11, 15, m[sigma[i][6]], m[sigma[i][7]])

    v = mix(v, 0, 5, 10, 15, m[sigma[i][ 8]], m[sigma[i][ 9]])   // Rows have been shifted
    v = mix(v, 1, 6, 11, 12, m[sigma[i][10]], m[sigma[i][11]])
    v = mix(v, 2, 7,  8, 13, m[sigma[i][12]], m[sigma[i][13]])
    v = mix(v, 3, 4,  9, 14, m[sigma[i][14]], m[sigma[i][15]])
  }

  for i := 0; i < 8; i++ {
    h[i] ^= v[i]
    h[i] ^= v[i+8]
  }

  return h
}

func getNiceOutput(h [8]uint64) [64]byte {
  var out [64]byte
  for i := 0; i < 8; i++ {
    for j := 8; j != 0; j-- {
      out[i*8+(j-1)] = byte(((h[i] << uint64(64 - uint64((j)*8))) & 0xFFFFFFFFFFFFFFFF) >> 56)
    }
  }
  return out
}

func BLAKEchecksum(f string, hashL int) [64]byte {
  h := k  // Initialize h0-7 with initial values.
  h[0] = h[0] ^ (0x01010000 ^ uint64(hashL)) // Not using a key

  a, err := os.Open(f)    // Open file
  check(err)
  aInfo, err := a.Stat()  // Get statistics of file
  check(err)

  fileSize := int(aInfo.Size()) // Get size of original file

  var bufferSize int = 65536

  if fileSize < bufferSize {    // If the buffer size is larger than the file size, just read the whole file.
    bufferSize = fileSize
  }

  var buffCount int = 0   // Keeps track of how far through the file we are
  var bytesFed int = 0
  var bytesLeft int = fileSize

  for buffCount < fileSize {
    if bufferSize > (fileSize - buffCount) {
      bufferSize = fileSize - buffCount
    }
    buff := make([]uint64, bufferSize)
    tempBuff := make([]byte, bufferSize)  // Make a slice the size of the buffer
    _, err := io.ReadFull(a, tempBuff) // Read the contents of the original file, but only enough to fill the buff array.
                                   // The "_" tells go to ignore the value returned by io.ReadFull, which in this case is the number of bytes read.
    check(err)
    for i := range tempBuff {
      buff[i] = uint64(tempBuff[i])
    }
    tempBuff = nil // Delete array

    for len(buff) % 128 != 0 {
      buff = append(buff, 0)  // Append 0s when buffer is not long enough
    }

    for i := 0; i < bufferSize; i += 128 {
      if bytesLeft <= 128 {
        h = blakeCompress(h, buff[i:i+128], bytesFed+bytesLeft, true)
      } else {
        bytesFed += 128
        h = blakeCompress(h, buff[i:i+128], bytesFed, false)
      }
      bytesLeft -= 128
    }

    buffCount += bufferSize
  }
  a.Close()

  return getNiceOutput(h)
}

func main() {
  bytes, err := ioutil.ReadAll(os.Stdin)  // Read file to hash from stdin
  check(err)
  f := string(bytes)

  fmt.Printf("%x", BLAKEchecksum(f, 64))
}
