package AESstring

import (
  "os"
  "log"
  "io/ioutil"
  b64 "encoding/base64" // For enc/decoding encrypted string
  "AES"
  "sorts" // QuickSortAlph made in sorts.go
)

func EncryptFileName(expandedKey *[176]byte, name string) string {
  var byteName = []byte(name)

  for len(byteName) % 16 != 0 {   // Pad with 0's
    byteName = append(byteName, 0)
  }

  for i := 0; i < len(byteName); i += 16 {
    AES.Encrypt(byteName[i:i+16], expandedKey)  // Done by reference so does not need to be assigned
  }
  return b64.URLEncoding.EncodeToString(byteName) // URL encoding used so it is safe for file systems ("/")
}

func DecryptFileName(expandedKey *[176]byte, hexName string) string {
  byteName, err := b64.URLEncoding.DecodeString(hexName)
  if err != nil { panic(err) }

  for i := 0; i < len(byteName); i += 16 {
    AES.Decrypt(byteName[i:i+16], expandedKey)
  }
  byteName = checkForPadding(byteName)
  return string(byteName[:])
}

func checkForPadding(input []byte) ([]byte) {
  var newBytes []byte
  for _, element := range input {
    if (element > 31) && (element < 127) {    //If a character
      newBytes = append(newBytes, element)
    }
  }
  return newBytes
}

func EncryptListOfString(expandedKey *[176]byte, l []string) []string {
  for i := range l {
    l[i] = EncryptFileName(expandedKey, l[i])
  }
  return l
}

func DecryptListOfString(expandedKey *[176]byte, l []string) []string {
  var out []string
  for i := range l {
    out = append(out, DecryptFileName(expandedKey, l[i]))
  }
  return out
}

func GetListsEnc(expandedKey *[176]byte, fileList, targetList []string, folder, target string) ([]string, []string) { // Also makes the folders required
  os.Mkdir(target, os.ModePerm)
  list, err := ioutil.ReadDir(folder)
  if err != nil { panic(err) }
  for i := range list {
    if len(list[i].Name()) <= 176 {
      if list[i].IsDir() {
        fileList, targetList = GetListsEnc(expandedKey, fileList, targetList, folder+list[i].Name()+"/", target+EncryptFileName(expandedKey, list[i].Name())+"/")
      } else {
        fileList   = append(fileList, folder+list[i].Name())
        targetList = append(targetList, target+EncryptFileName(expandedKey, list[i].Name()))
      }
    } else {
      log.Output(0, "File name too long: "+list[i].Name())
    }
  }
  return fileList, targetList
}

func GetListsDec(expandedKey *[176]byte, fileList, targetList []string, folder, target string) ([]string, []string) {
  os.Mkdir(target, os.ModePerm)
  list, err := ioutil.ReadDir(folder)
  if err != nil { panic(err) }
  for i := range list {
    if list[i].IsDir() {
      fileList, targetList = GetListsDec(expandedKey, fileList, targetList, folder+list[i].Name()+"/", target+DecryptFileName(expandedKey, list[i].Name())+"/")
    } else {
      fileList   = append(fileList, folder+list[i].Name())
      targetList = append(targetList, target+DecryptFileName(expandedKey, list[i].Name()))
    }
  }
  return fileList, targetList
}

func getSortedFoldersAndFiles(inp []sorts.Tuple) ([]string, []string) {
  var files []sorts.Tuple
  var folders []sorts.Tuple
  for i := 0; i < len(inp); i++ {
    if inp[i].A.IsDir() {
      folders = append(folders, inp[i])
    } else {
      files = append(files, inp[i])
    }
  }
  foldersSort, filesSort := sorts.QuickSortAlph(folders), sorts.QuickSortAlph(files)
  var (
    encOut []string
    decOut []string
  )
  for x := range foldersSort {
    encOut = append(encOut, foldersSort[x].A.Name())
    decOut = append(decOut, foldersSort[x].B)
  }
  for y := range filesSort {
    encOut = append(encOut, filesSort[y].A.Name())
    decOut = append(decOut, filesSort[y].B)
  }
  return encOut, decOut
}

func GetListOfFiles(expandedKey *[176]byte, dir string) ([]string, []string) {  // Decrypts a list of files at the directory specified, also returning original list
  list, err := ioutil.ReadDir(dir)
  if err != nil { panic(err) }
  l := make([]sorts.Tuple, 0)
  var listOfNames []string
  for x := range list {
    listOfNames = append(listOfNames, list[x].Name())
  }
  dec := DecryptListOfString(expandedKey, listOfNames)

  for i := range list {
    l = append(l, sorts.Tuple{A: list[i], B: dec[i]})
  }
  return getSortedFoldersAndFiles(l)
}
