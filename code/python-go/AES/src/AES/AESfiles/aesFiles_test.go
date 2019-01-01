package AESfiles

import (
  "fmt"
  "testing"
  "os/exec"
  "strings"
  "AES"
)

const (
  largeFile = "/home/josh/GentooMin.iso"
  largeFileTemp = "/home/josh/temp"
  largeFileDec = "/home/josh/decTemp.iso"

  mediumFile = "/home/josh/8k.png"
  mediumFileTemp = "/home/josh/8kTemp"
  mediumFileDec = "/home/josh/8kDec.png"

  smallFile = "/home/josh/a.txt"
  smallFileTemp = "/home/josh/temp2"
  smallFileDec = "/home/josh/smallDec.txt"
)

var (
  expandedKey = AES.ExpandKey([]byte{0x00, 0x0b, 0x16, 0x1d, 0x2c, 0x27, 0x3a, 0x31, 0x58, 0x53, 0x4e, 0x45, 0x74, 0x7f, 0x62, 0x69})
)

func BenchmarkEncryptFileLarge(b *testing.B) {
  for n := 0; n < b.N; n++ {
    EncryptFile(&expandedKey, largeFile, largeFileTemp)
  }
}

func BenchmarkDecryptFileLarge(b *testing.B) {
  for n := 0; n < b.N; n++ {
    DecryptFile(&expandedKey, largeFileTemp, largeFileDec)
  }
}

func BenchmarkEncryptFileMedium(b *testing.B) {
  for n := 0; n < b.N; n++ {
    EncryptFile(&expandedKey, mediumFile, mediumFileTemp)
  }
}

func BenchmarkDecryptFileMedium(b *testing.B) {
  for n := 0; n < b.N; n++ {
    DecryptFile(&expandedKey, mediumFileTemp, mediumFileDec)
  }
}

func TestEncDecMediumFile(t *testing.T) {
  out, err := exec.Command("/bin/bash", "-c", "b2sum '"+mediumFile+"'").Output() // Gets hash of original file using the b2sum utility in the GNU core utils
  if err != nil { panic(err) }

  initialHash := strings.Replace(fmt.Sprintf("%s", out), mediumFile, "", -1) // b2sum outputs the dir after the checksum is output, so remove the dir.

  EncryptFile(&expandedKey, mediumFile, mediumFileTemp)
  DecryptFile(&expandedKey, mediumFileTemp, mediumFileDec)

  out, err = exec.Command("/bin/bash", "-c", "b2sum '"+mediumFileDec+"'").Output()

  finalHash := strings.Replace(fmt.Sprintf("%s", out), mediumFileDec, "", -1)

  if finalHash != initialHash {
    t.Fatalf("Expected %s but got %s", initialHash, finalHash)
  }
}

func TestEncDecSmallFile(t *testing.T) {
  out, err := exec.Command("/bin/bash", "-c", "b2sum '"+smallFile+"'").Output() // Gets hash of original file using the b2sum utility in the GNU core utils
  if err != nil { panic(err) }

  initialHash := strings.Replace(fmt.Sprintf("%s", out), smallFile, "", -1) // b2sum outputs the dir after the checksum is output, so remove the dir.

  EncryptFile(&expandedKey, smallFile, smallFileTemp)
  DecryptFile(&expandedKey, smallFileTemp, smallFileDec)

  out, err = exec.Command("/bin/bash", "-c", "b2sum '"+smallFileDec+"'").Output()

  finalHash := strings.Replace(fmt.Sprintf("%s", out), smallFileDec, "", -1)

  if finalHash != initialHash {
    t.Fatalf("Expected %s but got %s", initialHash, finalHash)
  }
}
