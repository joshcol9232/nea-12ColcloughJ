package main

import (
  "fmt"       // For sending output on stout
  "log"
  "os"        // Gets stdin
  "io/ioutil" // For reading from stdin
  "strings"   // For converting string key to an array of bytes
  "strconv"   // ^
  "AES"
  "AES/AESfiles"
  "AES/AESstring"
  "AES/AEScheckKey"
  "sorts"
)

func strToInt(str string) (int, error) {    // Used for converting string to integer, as go doesn't have that built in for some reason
    n := strings.Split(str, ".")    // Splits by decimal point
    return strconv.Atoi(n[0])       // Returns integer of whole number
}

func main() {
  bytes, err := ioutil.ReadAll(os.Stdin)
  if err != nil { panic(err) }
  fields := strings.Split(string(bytes), ", ")
  request := string(fields[0])
  var expandedKey [176]byte
  var key []byte

  if string(fields[3]) != "" {    // If the key has been passed.
    keyString := strings.Split(string(fields[3]), " ")
    for i := 0; i < len(keyString); i++ {
      a, err := strToInt(keyString[i])
      if err != nil { panic(err) }
      key = append(key, byte(a))
    }
    expandedKey = AES.ExpandKey(key)

  } else {
    log.Output(0, "EGG")
  }


  if request == "y" {
    AESfiles.EncryptFile(&expandedKey, string(fields[1]), string(fields[2]))
  } else if request == "n" {
    AESfiles.DecryptFile(&expandedKey, string(fields[1]), string(fields[2]))
  } else if request == "yDir" {
    AESfiles.EncryptList(&expandedKey, strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "nDir" {
    AESfiles.DecryptList(&expandedKey, strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "encString" {
    fmt.Print(AESstring.EncryptFileName(&expandedKey, string(fields[1])))
  } else if request == "decString" {
    fmt.Print(AESstring.DecryptFileName(&expandedKey, string(fields[1])))
  } else if request == "encList" {
    fmt.Print(strings.Join(AESstring.EncryptListOfString(&expandedKey, strings.Split(string(fields[1]), "\n")), ",,"))
  } else if request == "decList" {
    fmt.Print(strings.Join(AESstring.DecryptListOfString(&expandedKey, strings.Split(string(fields[1]), "\n")), ",,"))
  } else if request == "getListsy" {
    fileList, targList := AESstring.GetListsEnc(&expandedKey, []string{}, []string{}, string(fields[1]), string(fields[2]))
    fmt.Print(strings.Join(fileList, ",,")+"--!--")
    fmt.Print(strings.Join(targList, ",,"))
  } else if request == "getListsn" {
    fileList, targList := AESstring.GetListsDec(&expandedKey, []string{}, []string{}, string(fields[1]), string(fields[2]))
    fmt.Print(strings.Join(fileList, ",,")+"--!--")
    fmt.Print(strings.Join(targList, ",,"))
  } else if request == "listDir" {
    log.Output(0, "Getting List")
    fs, fsDec := AESstring.GetListOfFiles(&expandedKey, string(fields[1]))
    fmt.Print(strings.Join(fs, ",,")+"--!--")
    fmt.Print(strings.Join(fsDec, ",,"))
  } else if request == "sortSize" {
    fmt.Print(strings.Join(sorts.UseQuickSortSize(strings.Split(string(fields[1]), "\n")), ",,"))
  } else if request == "test" {
    valid := AEScheckKey.CheckKeyOfFile(key, string(fields[1]))
    if valid {
      fmt.Print("-Valid-")
    } else {
      fmt.Print("-NotValid-")
    }
  } else {
    panic("Invalid options.")
  }

   // out := encryptFileName(expandKey([]byte{49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 49, 50, 51, 52, 53, 54}), "12345678901234567")
   // fmt.Println(out, len(out))
   // fmt.Println(decryptFileName(expandKey([]byte{49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 49, 50, 51, 52, 53, 54}), out))
}
