package main

import (
  "github.com/fogleman/gg"
  "os"
  "io/ioutil"
  "image"
  "math"
  _ "image/jpeg" // add these so that image can be read
  _ "image/png"
  "strings"
  "strconv"
)

func check(e error) {     //Used for checking errors when reading/writing to files.
  if e != nil {
    panic(e)
  }
}

// Returns thumbnail of image that is of desired height (y).
func getThumb(f, w string, y int) {
  a, err := os.Open(f)
  check(err)

  img, _, err := image.Decode(a)  // _ is where the function returns the format name, which I don't really need for this
  check(err)
  a.Close()
  bounds := img.Bounds() // Get Rectangle object that has size of the image.

  oldX, oldY := bounds.Dx(), bounds.Dy()
  factor := int(math.Ceil(float64(oldY/y))) // Get the shrink factor
  if factor == 0 {
    data, err := ioutil.ReadFile(f)
    check(err)
    e, err := os.OpenFile(w, os.O_RDWR|os.O_CREATE, 0755)
    check(err)
    e.Write(data)
    e.Close()
  } else {
    newX, newY := oldX/factor, oldY/factor
    genThumb(oldX, oldY, newX, newY, factor, img, w)
  }
}

func genThumb(oldX, oldY, newX, newY, scanLen int, img image.Image, destination string) {
  scanArea := uint32(scanLen*scanLen)
  dc := gg.NewContext(newX, newY) // Make new image object

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
      avR = avR/scanArea  // Get average
      avG = avG/scanArea
      avB = avB/scanArea
      avA = avA/scanArea

      R := float64(float64(avR)/65535)  // Divided by 65535 because the Image module does colour between 0 and 65535 (same as a 32 bit binary word).
      G := float64(float64(avG)/65535)
      B := float64(float64(avB)/65535)
      A := float64(float64(avA)/65535)
      dc.SetRGBA(R, G, B, A)
      dc.SetPixel(x/scanLen, y/scanLen)
    }
  }
  dc.SavePNG(destination)
}

func strToInt(str string) (int, error) {    //Used for converting string to integer, as go doesn't have that built in for some reason
    n := strings.Split(str, ".")    //Splits by decimal point
    return strconv.Atoi(n[0])       //Returns integer of whole number
}

func main() {
  f := "/home/josh/mandelbrot.png"
  w := "/home/josh/test.png"
  getThumb(f, w, 480)

}
