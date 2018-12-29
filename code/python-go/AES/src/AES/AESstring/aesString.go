package AESstring

import (
  "os"
  "io/ioutil"
  "log"
  "encoding/hex" // For enc/decoding encrypted string
  "AES"
)

func EncryptFileName(expandedKeys [176]byte, name string) string {
  var byteName = []byte(name)

  for len(byteName) % 16 != 0 {   // Pad with 0's
    byteName = append(byteName, 0)
  }

  for i := 0; i < len(byteName); i += 16 {
    AES.Encrypt(byteName[i:i+16], expandedKeys)  // Done by reference so does not need to be assigned
  }

  return hex.EncodeToString(byteName)
}

func DecryptFileName(expandedKeys [176]byte, hexName string) string {
  byteName, err := hex.DecodeString(hexName)
  if err != nil { panic(err) }

  for i := 0; i < len(byteName); i += 16 {
    AES.Decrypt(byteName[i:i+16], expandedKeys)
  }
  checkForPadding(byteName)
  return string(byteName[:])
}

func checkForPadding(input []byte) {    // Checks for 0s in decrypted string (since 0 isn't on the ascii table as a letter/number)
  for i := 0; i < len(input); i++ {
    if input[i] == 0 {
      input = append(input[:i], input[i+1:]...)
    }
  }
}

func EncryptListOfString(expandedKeys [176]byte, l []string) []string {
  for i := range l {
    l[i] = EncryptFileName(expandedKeys, l[i])
  }
  return l
}

func DecryptListOfString(expandedKeys [176]byte, l []string) []string {
  for i := range l {
    l[i] = DecryptFileName(expandedKeys, l[i])
  }
  return l
}

func GetLists(expandedKeys [176]byte, fileList, targetList []string, folder, target string) ([]string, []string) { // Also makes the folders required
  os.Mkdir(target, os.ModePerm)
  list, err := ioutil.ReadDir(folder)
  if err != nil { panic(err) }
  for i := range list {
    if len(list[i].Name()) < 127 { // Max is 255 for file names, but this will double due to hex.
      if list[i].IsDir() {
        fileList, targetList = GetLists(expandedKeys, fileList, targetList, folder+list[i].Name()+"/", target+EncryptFileName(expandedKeys, list[i].Name())+"/")
      } else {
        fileList   = append(fileList, folder+list[i].Name())
        targetList = append(targetList, target+EncryptFileName(expandedKeys, list[i].Name()))
      }
    } else {
      log.Output(0, "Name too long: "+list[i].Name())
    }
  }
  return fileList, targetList
}
