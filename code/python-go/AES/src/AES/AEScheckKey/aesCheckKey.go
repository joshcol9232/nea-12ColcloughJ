package AEScheckKey

import (
  "os"
  "io"
  "AES"
)

func CompareSlices(slice1, slice2 []byte) bool {    // Function used for checking first block of a file with the key when decrypting.
  if len(slice1) != len(slice2) {
    return false
  } else {
    for i := 0; i < len(slice1); i++ {
      if slice1[i] != slice2[i] {
        return false
      }
    }
  }
  return true
}

func CheckKey(expandedKey *[176]byte, block []byte) bool {
  AES.Decrypt(block, expandedKey)    // Decrypt first block
  return CompareSlices(expandedKey[:16], block) // Compare decrypted first block with the key.
}

func CheckKeyOfFile(key []byte, f string) bool {
  a, err := os.Open(f)    // Open an encrypted file to check first block against key
  if err != nil { panic(err) }

  firstBlock := make([]byte, 16)
  _, er := io.ReadFull(a, firstBlock)   // Fill a slice of length 16 with the first block of 16 bytes in the file.
  if er != nil { panic(er) }
  a.Close()
  expKey := AES.ExpandKey(key)
  return CheckKey(&expKey, firstBlock)
}
