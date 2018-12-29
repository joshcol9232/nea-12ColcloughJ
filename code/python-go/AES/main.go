package main

import (
  "fmt"       // For sending output on stout
  "os"        // Gets stdin
  "io/ioutil" // For reading from stdin
  "strings"   // For converting string key to an array of bytes
  "strconv"   // ^
  "AES"
  "AES/AESfiles"
  "AES/AESstring"
  "AES/AEScheckKey"
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
    AESfiles.EncryptFile(AES.ExpandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "n" {
    AESfiles.DecryptFile(AES.ExpandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "yDir" {
    AESfiles.EncryptList(AES.ExpandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "nDir" {
    AESfiles.DecryptList(AES.ExpandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "dirList" {
    fileList, targList := AESstring.GetLists(AES.ExpandKey(key), []string{}, []string{}, string(fields[1]), string(fields[2]))
    fmt.Print(strings.Join(fileList, ",,")+"--!--")
    fmt.Print(strings.Join(targList, ",,"))
  } else if request == "test" {
    valid := AEScheckKey.CheckKeyOfFile(key, string(fields[1]))
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
