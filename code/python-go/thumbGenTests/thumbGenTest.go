package main

import (
  "github.com/fogleman/gg"
  "os"
  "io/ioutil"
  "image"
  "math"
  _ "image/jpeg" // add these so that image can be read
  _ "image/png"
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
  dc := gg.NewContext(newX, newY) // Make new image object

  for x := 0; x < oldX; x += scanLen {
    for y := 0; y < oldY; y += scanLen {
      r, g, b, a := img.At(x, y).RGBA()
      R, G, B, A := float64(float64(r)/65535), float64(float64(g)/65535), float64(float64(b)/65535), float64(float64(a)/65535)
      dc.SetRGBA(R, G, B, A)
      dc.SetPixel(x/scanLen, y/scanLen)
    }
  }
  dc.SavePNG(destination)
}

func main() {
  f := "/home/josh/mandelbrot.png"
  w := "/home/josh/test.png"
  getThumb(f, w, 480)
}
