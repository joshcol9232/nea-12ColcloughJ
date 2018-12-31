package main

import (
  "BLAKE"
  "fmt"
  "testing"
)

const largeFile = "/home/josh/GentooMin.iso"
const smallFile = "/home/josh/a.txt"

func BenchmarkBLAKELarge(b *testing.B) {
  for n := 0; n < b.N; n++ {
    BLAKE.GetChecksum(largeFile, 64)
  }
}

func BenchmarkBLAKESmall(b *testing.B) {
  for n := 0; n < b.N; n++ {
    BLAKE.GetChecksum(smallFile, 64)
  }
}

func TestBLAKELarge(t *testing.T) {
  actualResult := fmt.Sprintf("%x", BLAKE.GetChecksum(largeFile, 64))
  expectedResult := "640ac216c91f85d69b450b070828b0f2f54db51af3ecf1daffeafdd657ae1a8d4e5732b4594f936c9d2d853ee12a1df58e6fa63535c1ed3e170e9578da740e5d"  // Obtained using b2sum tool in GNU core utilities

  if actualResult != expectedResult {
    t.Fatalf("Expected %s but got %s", expectedResult, actualResult)
  }
}

func TestBLAKESmall(t *testing.T) {
  actualResult := fmt.Sprintf("%x", BLAKE.GetChecksum(smallFile, 64))
  expectedResult := "0401983e1a14dab1f48b29178cea53cf3931367207fcca32a29093fae953f557d28bb5c20733a875c3ad231027ead1552d3775f9f53a333101ff750ba3061440"

  if actualResult != expectedResult {
    t.Fatalf("Expected %s but got %s", expectedResult, actualResult)
  }
}
