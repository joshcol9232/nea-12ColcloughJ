package main

import (
  "io/ioutil"
)

func main() {
	bytes, err := ioutil.ReadAll(os.Stdin)  // Read file to hash from stdin
  check(err)
  f := string(bytes)

	fmt.Printf("%x", BLAKEchecksum(f, 64))
}
