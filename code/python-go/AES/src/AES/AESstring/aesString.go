package AESstring

import (
  "log"
  "os"
  "io/ioutil"
  "encoding/hex" // For enc/decoding encrypted string
  "AES"
  "sorts" // QuickSortAlph made in sorts.go
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

func EncryptListOfString(expandedKeys [176]byte, l []string) []string {
  for i := range l {
    l[i] = EncryptFileName(expandedKeys, l[i])
  }
  return l
}

func DecryptListOfString(expandedKeys [176]byte, l []string) []string {
  var out []string
  for i := range l {
    out = append(out, DecryptFileName(expandedKeys, l[i]))
  }
  return out
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

func GetListOfFiles(expandedKeys [176]byte, dir string) ([]string, []string) {  // Decrypts a list of files at the directory specified, also returning original list
  list, err := ioutil.ReadDir(dir)
  if err != nil { panic(err) }
  l := make([]sorts.Tuple, 0)
  var listOfNames []string
  for x := range list {
    listOfNames = append(listOfNames, list[x].Name())
  }
  dec := DecryptListOfString(expandedKeys, listOfNames)

  for i := range list {
    l = append(l, sorts.Tuple{A: list[i], B: dec[i]})
  }
  return getSortedFoldersAndFiles(l)
}
