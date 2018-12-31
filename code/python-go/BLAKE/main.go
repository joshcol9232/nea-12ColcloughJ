package main

import (
  "fmt"
  "os"
  "io/ioutil"
  "BLAKE"
)

func main() {
	bytes, err := ioutil.ReadAll(os.Stdin)  // Read file to hash from stdin
  if err != nil { panic(err) }
  f := string(bytes)

	fmt.Printf("%x", BLAKE.GetChecksum(f, 64))
}
