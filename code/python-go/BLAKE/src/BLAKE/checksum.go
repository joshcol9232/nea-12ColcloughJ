package BLAKE

import (
  "os"
  "io"
)

func GetChecksum(f string, hashL int) [64]byte {
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
        h = BlakeCompress(h, buff[i:i+128], bytesFed+bytesLeft, true)
      } else {
        bytesFed += 128
        h = BlakeCompress(h, buff[i:i+128], bytesFed, false)
      }
      bytesLeft -= 128
    }

    buffCount += bufferSize
  }
  a.Close()

  return getLittleEndian(h)
}

func getLittleEndian(h [8]uint64) [64]byte {
  var out [64]byte
  for i := 0; i < 8; i++ {
    for j := 8; j != 0; j-- {
      out[i*8+(j-1)] = byte(((h[i] << uint64(64 - uint64((j)*8))) & 0xFFFFFFFFFFFFFFFF) >> 56)
    }
  }
  return out
}
