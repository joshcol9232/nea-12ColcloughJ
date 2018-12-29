package main

import (
  "fmt"       // For sending output on stout
  "os"
  "io/ioutil" // For reading from stdin
  "strings"   // For converting string key to an array of bytes
  "strconv"   // ^
  "AES"
)

func strToInt(str string) (int, error) {    // Used for converting string to integer, as go doesn't have that built in for some reason
    n := strings.Split(str, ".")    // Splits by decimal point
    return strconv.Atoi(n[0])       // Returns integer of whole number
}

func main() {
  bytes, err := ioutil.ReadAll(os.Stdin)
  if err != nil { panic(err) }
  fields := strings.Split(string(bytes), ", ")
  keyString := strings.Split(string(fields[3]), " ")

  var key []byte
  for i := 0; i < len(keyString); i++ {
    a, err := strToInt(keyString[i])
    if err != nil { panic(err) }
    key = append(key, byte(a))
  }
  request := string(fields[0])

  if request == "y" {
    AES.EncryptFile(AES.ExpandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "n" {
    AES.DecryptFile(AES.ExpandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "yDir" {
    AES.EncryptList(AES.ExpandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "nDir" {
    AES.DecryptList(AES.ExpandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "dirList" {
    fileList, targList := AES.GetLists(AES.ExpandKey(key), []string{}, []string{}, string(fields[1]), string(fields[2]))
    fmt.Print(strings.Join(fileList, ",,")+"--!--")
    fmt.Print(strings.Join(targList, ",,"))
  } else if request == "test" {
    valid := AES.CheckKey(key, string(fields[1]))
    if valid {
      fmt.Println("-Valid-")
    } else {
      fmt.Println("-NotValid-")
    }
  } else {
    panic("Invalid options.")
  }

   // out := encryptFileName(expandKey([]byte{49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 49, 50, 51, 52, 53, 54}), "12345678901234567")
   // fmt.Println(out, len(out))
   // fmt.Println(decryptFileName(expandKey([]byte{49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 49, 50, 51, 52, 53, 54}), out))
}
