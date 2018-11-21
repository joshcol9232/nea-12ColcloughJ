package main

import (
  "fmt"
  "math"
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


var sigma = [10][16]byte {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15},
                         {14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3},
                         {11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4},
                         {7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8},
                         {9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13},
                         {2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9},
                         {12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11},
                         {13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10},
                         {6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5},
                         {10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0}}


func pad128(inp []byte) [128]byte {
  var result = [128]byte {}
  for i := 0; i < len(inp); i++ {
    result[i] = inp[i]
  }
  return result
}


func rotRB(in byte, n int) byte {
  return (in >> uint(n)) ^ (in << (8 - uint(n)))
}

func rotR64(in uint64, n int) uint64 {
  return (in >> uint(n)) ^ (in << (64 - uint(n)))
}

func mix(vA, vB, vC, vD, x, y, []byte) {
  vA = vA + vB + x
  vD = (vD ^ vA) //rotateright 32
}

func compress(h [8]uint64, block []byte, t int, lastBlock bool) {  // Compressing function
  var v = [16]uint64{} // Current vector
  for i := 0; i < 8; i++ {
    v[i] = h[i]
  }
  for i := 8; i < 16; i++ {
    v[i] = k[i-8]
  }

  v[12] = v[12] ^ uint64(math.Mod(float64(t), math.Pow(2, 64)))
  v[13] = v[13] ^ (uint64(t) >> 64)

  if lastBlock {
    v[14] = v[14] ^ 0xFFFFFFFFFFFFFFFF
  }

  //for i := 0; i < 11; i++ { // Do 11 out of the 12 rounds
    //mix
  //}

  for i := 0; i < 11; i++ {
    sigRow := int(math.Mod(i, 10))

    //mix
  }

}

// w = 64
// r = 12 rounds
// 128 block bytes

func blake2b(m []byte, l int, hashL int) {// []byte {   // M is message, l is length of message, hashL is length of hash wanted.
  h := k

  var M [128]byte
  for i := 0; i < 128; i++ {
    M[i] = m[i]
  }

  h[0] = h[0] ^ 0x01010000 ^ (uint64(hashL) << 8) ^ uint64(l)

  var bytesCompressed int = 0
  var bytesRemaining int = l

  fmt.Println(bytesRemaining, "remaining")

  for (bytesRemaining > 128) {
    block := M[bytesCompressed:bytesCompressed+128]
    bytesRemaining += - 128
    bytesCompressed += 128
    fmt.Println(block)
  }
  block := M[bytesCompressed:bytesCompressed+128]
  bytesCompressed = bytesCompressed+bytesRemaining
  compress(h, block, bytesCompressed, true)

  //compress h
}


func main() {
  var g = []byte{}
  for i := 0; i < 128; i++ {
    g = append(g, byte(i))
  }
  blake2b(g, len(g), 128)
}
