package main

import (
  "bufio"
  "os"
)

func check(e error) {
  if e != nil {
    panic(e)
  }
}

func main() {
  reader := bufio.NewReader(os.Stdin)
  data := make([]byte, 256)
  _, err := reader.Read(data)
  check(err)
  print("\n", data, " DATA")

}
