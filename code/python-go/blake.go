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

func rotRB(in byte, n int) byte {
  return (in >> uint(n)) ^ (in << (8 - uint(n)))
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


func get64(in []uint64) uint64 {
  return uint64(in[0] ^ (in[1] << 8) ^ (in[2] << 16) ^ (in[3] << 24) ^ (in[4] << 32) ^ (in[5] << 40) ^ (in[6] << 48) ^ (in[7] << 56))
}


func compress(h [8]uint64, block [128]uint64, t int, lastBlock bool) [8]uint64 {  // Compressing function
  var v = [16]uint64{} // Current vector
  for i := 0; i < 8; i++ {
    v[i] = h[i]
    v[i+8] = k[i]
  }

  fmt.Printf("%x V12 before", v[12])
  v[12] = v[12] ^ uint64(math.Mod(float64(t), 18446744073709552000)) //  2 ^ 64 = 18446744073709552000 //ISSUE
  v[13] = v[13] ^ (uint64(t) >> 64)

  if lastBlock {
    v[14] = ^v[14] // NOT
  }


  fmt.Printf("%x V IN COMPRESS!!!!\n", v)

  var m [16] uint64
  for i := 0; i < 16; i++ {
    m[i] = get64(block[i*8:(i*8)+8])
  }
  fmt.Printf("%x M\n", m)
  for i := 0; i < 12; i++ {
    sigRow := sigma[i]
    fmt.Printf("%xSIGMA ROW\n", sigRow)
    fmt.Println(i, "i")
    // Mix
    v = mix(v, 0, 4,  8, 12, m[sigRow[0]], m[sigRow[1]])
    v = mix(v, 1, 5,  9, 13, m[sigRow[2]], m[sigRow[3]])
    v = mix(v, 2, 6, 10, 14, m[sigRow[4]], m[sigRow[5]])
    v = mix(v, 3, 7, 11, 15, m[sigRow[6]], m[sigRow[7]])

    v = mix(v, 0, 5, 10, 15, m[sigRow[ 8]], m[sigRow[ 9]])   // Rows have been shifted
    v = mix(v, 1, 6, 11, 12, m[sigRow[10]], m[sigRow[11]])
    v = mix(v, 2, 7,  8, 13, m[sigRow[12]], m[sigRow[13]])
    v = mix(v, 3, 4,  9, 14, m[sigRow[14]], m[sigRow[15]])

    fmt.Printf("%x\nV\n", v)
  }

  for i := 0; i < 8; i++ {
    h[i] ^= v[i]
    h[i] ^= v[i+8]
  }

  return h
}

// w = 64
// r = 12 rounds
// 16 64-bit words per block.
// 512 bit
func blake2b(data [][128]uint64, l, hashL int) [8]uint64 {  // data is split into 16 64-bit words.
  h := k

  h[0] = h[0] ^ (0x01010000 ^ uint64(hashL)) // Not using a key

  fmt.Printf("%x H!!!!!!\n", h)


  data[0] = [128]uint64{0x0000000000636261}

  if len(data) > 1 {
    for i := 0; i < len(data)-2; i++ {  // Do all blocks apart from last one.
      h = compress(h, data[i], (i+1)*128, false)  //128 block bytes = 16 64-bit words.
    }
  }

  h = compress(h, data[len(data)-1], l, true)

  return h
}


func main() {
  g := [][128]uint64{{0}} //{2, 3, 5, 1, 2, 66, 99}}

  h := blake2b(g, 3, 64)
  fmt.Printf("%x\nLAST", h)
}
