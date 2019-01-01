package BLAKE

import (
  "fmt"
  "testing"
)

const largeFile = "/home/josh/GentooMin.iso"
const smallFile = "/home/josh/a.txt"

func BenchmarkBLAKELarge(b *testing.B) {
  for n := 0; n < b.N; n++ {
    GetChecksum(largeFile, 64)
  }
}

func BenchmarkBLAKESmall(b *testing.B) {
  for n := 0; n < b.N; n++ {
    GetChecksum(smallFile, 64)
  }
}

func TestBLAKELarge(t *testing.T) {
  actualResult := fmt.Sprintf("%x", GetChecksum(largeFile, 64))
  expectedResult := "640ac216c91f85d69b450b070828b0f2f54db51af3ecf1daffeafdd657ae1a8d4e5732b4594f936c9d2d853ee12a1df58e6fa63535c1ed3e170e9578da740e5d"  // Obtained using b2sum tool in GNU core utilities

  if actualResult != expectedResult {
    t.Fatalf("Expected %s but got %s", expectedResult, actualResult)
  }
}

func TestBLAKESmall(t *testing.T) {
  actualResult := fmt.Sprintf("%x", GetChecksum(smallFile, 64))
  expectedResult := "f545377b0ab74d283ff65ec5518bc00633d46125ec28bbd11f417da16949e8937759d8f1aa97556845e24edc676d8f288d49aae1bb195a12e5595525713427c4"

  if actualResult != expectedResult {
    t.Fatalf("Expected %s but got %s", expectedResult, actualResult)
  }
}

func TestBlakeMix(t *testing.T) {
  arr := []uint64{0x70f3abeaaf82f2d2, 0x48221449c090c5cb, 0x1631bc17f31ed4ef, 0xdf4a6c4edfb6012e,
  								0x4011c31f6e4fbe98, 0xeca6fe4ecfbd235d,	 0xc732f6aacdfed23, 0x6c59d3af929a71a7,
  								0x726e4d94d076d220, 0xd55261f05e988e99, 0x47c5fed6073fff6f, 0xafdc6ec84b5122fd,
  								0x828789a16ddf8fcc, 0x9219a1cce5eaceb3, 0x81c389d523f73c81, 0xc518f0411804f255} // Randomly generated in python.

	expectedResult := []uint64{0x24f71c9177a10424, 0x48221449c090c5cb, 0x1631bc17f31ed4ef, 0xdf4a6c4edfb6012e,
      											 0x216426a085db4092, 0xeca6fe4ecfbd235d,  0xc732f6aacdfed23, 0x6c59d3af929a71a7,
      											 0xaa69fe02ab573a54, 0xd55261f05e988e99, 0x47c5fed6073fff6f, 0xafdc6ec84b5122fd,
      											 0x9771847d3761d4df, 0x9219a1cce5eaceb3, 0x81c389d523f73c81, 0xc518f0411804f255}

  blakeMix(arr, 0, 4, 8, 12, &arr[0], &arr[1]) // Simulates first mix of the compression function.

  if fmt.Sprintf("%x", arr) != fmt.Sprintf("%x", expectedResult) {
    t.Fatalf("Expected %x but got %x", expectedResult, arr)
  }
}
