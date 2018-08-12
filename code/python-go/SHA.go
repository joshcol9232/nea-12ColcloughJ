package main

import (
  "fmt"
)

var k = [64]int {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,    //Round constants
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
                  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2}

func check(e error) {
  if e != nil {
    panic(e)
  }
}

func intToBits(inp int, bitLength int) ([]int) {
  tempByte := make([]int, bitLength)
  for i := 0; i < bitLength; i++ {
    tempByte[(bitLength-1)-i] = (inp >> uint(i)) & 1
  }
  return tempByte
}

func makeBitArray(inp string) ([]int){
  var bitArray []int
  var dat = []byte(inp)

  for i := 0; i < len(dat); i++ {
    tempByte := intToBits(int(dat[i]), 8)
    for x := 0; x < len(tempByte); x++ {
      bitArray = append(bitArray, tempByte[x])
    }
  }
  return bitArray
}

func bitsToInt(inp []int) (int) {
  fmt.Println(inp)
  var result int
  for i := 0; i < len(inp); i++ {
    if inp[i] == 1 {
      var temp int = 1
      for x := 0; x < (len(inp)-i)-1; x++ {
        temp = temp * 2
      }
      result += temp
    }
  }
  return result
}

func pad(inpBits []int) ([]int){  //https://csrc.nist.gov/csrc/media/publications/fips/180/4/archive/2012-03-06/documents/fips180-4.pdf section 5.1
  l := len(inpBits)
  if (l % 512 == 0) && (l != 0) {
        return inpBits
  } else {
    inpBits = append(inpBits, 1) //Add 1 to the end
    k := 0
    for {
      if ((l+1+k)-448)%512 == 0 {break}
      k++
    }
    for i := 0; i < k; i++ {
      inpBits = append(inpBits, 0)
    }
    lengthBits := intToBits(l, 64)
    for x := 0; x < 64; x++ {
      inpBits = append(inpBits, lengthBits[x])
    }

    return inpBits
  }
}


func main() {
  a := makeBitArray("abc")
  fmt.Println(pad(a))
}
