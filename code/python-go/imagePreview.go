package main

import (
  "fmt"
  "github.com/fogleman/gg"
  "os"
  "image"
  _ "image/jpeg" // add these so that image can be read
  _ "image/png"
)


func check(e error) {     //Used for checking errors when reading/writing to files.
  if e != nil {
    panic(e)
  }
}


func getPreview(f string, scanLen int) { // Scan length is the size of square to scan the file with. e.g 2 would be a 2x2 square, so 4 pixels are averaged.
  a, err := os.Open(f)
  check(err)

  img, _, err := image.Decode(a)  // _ is where the function returns the format name, which I don't really need for this
  check(err)

  bounds := img.Bounds() // Get Rectangle object that has size of the image.

  scanArea := scanLen*scanLen
  scanAreaBits := uint32(scanArea)
  oldX, oldY := bounds.Dx(), bounds.Dy()
  newX, newY := oldX/scanLen, oldY/scanLen
  fmt.Println("Image size:", oldX, oldY)

  dc := gg.NewContext(newX, newY) // Make new image object
  fmt.Println(dc)

  var avR uint32
  var avG uint32
  var avB uint32
  var avA uint32

  for x := 0; x < oldX; x += scanLen {
    for y := 0; y < oldY; y += scanLen {
      avR = 0
      avG = 0
      avB = 0
      avA = 0
      for i := 0; (i < scanLen) && (x+i < oldX); i++ {
        for j := 0; (j < scanLen) && (j+y < oldY); j++ {
          r, g, b, a := img.At(x+i, y+j).RGBA()
          avR += r
          avG += g
          avB += b
          avA += a
        }
      }
      avR = avR/scanAreaBits
      avG = avG/scanAreaBits
      avB = avB/scanAreaBits
      avA = avA/scanAreaBits

      R := float64(float64(avR)/65535)
      G := float64(float64(avG)/65535)
      B := float64(float64(avB)/65535)
      A := float64(float64(avA)/65535)
      dc.SetRGBA(R, G, B, A)
      dc.SetPixel(x/scanLen, y/scanLen)
    }
  }
  dc.SavePNG("/home/josh/rescale.png")
}

func main() {
  f := "/home/josh/wp1848572.jpg"
  getPreview(f, 2)
}
