package AESfiles

import (
  "os"        // For opening files
  "io"        // For reading files
  "runtime"   // For getting CPU core count
  "AES"
  "AES/AEScheckKey"
)

const DEFAULT_BUFFER_SIZE = 65536  // Define the default buffer size for enc/decrypt (is 2^16)

func check(e error) {  // Checks error given
  if e != nil { panic(e) }
}

func getNumOfCores() int {  // Gets the number of cores so the number of workers can be determined.
  maxProcs := runtime.GOMAXPROCS(0)
  numCPU := runtime.NumCPU()
  if maxProcs < numCPU {
    return maxProcs
  }
  return numCPU
}

// For holding the buffer to be worked on and the offset together, so it can be written to the file in the correct place at the end.
type work struct {
  buff []byte
  offset int64
}

func workerEnc(jobs <-chan work, results chan<- work, expandedKey *[176]byte) {    // Encrypts a chunk when given (a chunk of length bufferSize)
  for job := range jobs {
    for i := 0; i < len(job.buff); i += 16 {
      AES.Encrypt(job.buff[i:i+16], expandedKey)
    }
    results<- job // Return result with encrypted job
  }
}

func workerDec(jobs <-chan work, results chan<- work, expandedKey *[176]byte) {
  for job := range jobs {
    for i := 0; i < len(job.buff); i += 16 {
      AES.Decrypt(job.buff[i:i+16], expandedKey)
    }
    results<- job  // Return job with decrypted buffer
  }
}

func EncryptFile(expandedKey *[176]byte, f, w string) {
  a, err := os.Open(f)    // Open original file to get statistics and read data.
  check(err)
  aInfo, err := a.Stat()  // Get statistics
  check(err)

  fileSize := int(aInfo.Size()) // Get size of original file

  if _, err := os.Stat(w); err == nil { // If file already exists, delete it
    os.Remove(w)
  }

  var workingWorkers int = 0
  var workerNum int = getNumOfCores()*2

  jobs := make(chan work, workerNum)     // Make two channels for go routines to communicate over.
  results := make(chan work, workerNum)  // Each has a buffer of length workerNum

  for i := 0; i < workerNum; i++ {
    go workerEnc(jobs, results, expandedKey)   // Create the workers
  }
  /*
  Each go routine will be given access to the job channel, where each worker then waits to complete the job.
  Once the job is completed, the go routine pushes the result onto the result channel, where the result can be
  recieved by the main routine. The results are read once all of the go routines are busy, or if the file
  is completed, then the remaining workers still working are asked for their results.
  */
  var bufferSize int = DEFAULT_BUFFER_SIZE

  if fileSize < bufferSize {    // If the buffer size is larger than the file size, just read the whole file.
    bufferSize = fileSize
  }

  var buffCount int = 0   // Keeps track of how far through the file we are

  e, err := os.OpenFile(w, os.O_CREATE|os.O_WRONLY, 0644) // Open file for writing.
  check(err)  // Check it opened correctly

  // Append key so that when decrypting, the key can be checked before decrypting the whole file.
  originalKey := make([]byte, 16)
  for i := 0; i < 16; i++ {
    originalKey[i] = expandedKey[i]
  }
  AES.Encrypt(originalKey, expandedKey)
  e.Write(originalKey)
  offset := 16

  for buffCount < fileSize {    // Same as a while buffCount < fileSize: in python3
    if bufferSize > (fileSize - buffCount) {
      bufferSize = fileSize - buffCount    // If this is the last block, read the amount of data left in the file.
    }

    buff := make([]byte, bufferSize)  // Make a slice the size of the buffer
    _, err := io.ReadFull(a, buff) // Read the contents of the original file, but only enough to fill the buff array.
                                   // The "_" tells go to ignore the value returned by io.ReadFull, which in this case is the number of bytes read.
    check(err)

    if len(buff) % 16 != 0 {  // If the buffer is not divisable by 16 (usually the end of a file), then padding needs to be added.
      var extraNeeded int
      var l int = len(buff)
      for l % 16 != 0 {       // extraNeeded holds the value for how much padding the block needs.
        l++
        extraNeeded++
      }

      for i := 0; i < extraNeeded; i++ {                  // Add the number of extra bytes needed to the end of the block, if the block is not long enough.
        buff = append(buff, byte(extraNeeded))  // For example, the array [1, 1, 1, 1, 1, 1, 1, 1] would have the number 8 appended to then end 8 times to make the array 16 in length.
      } // This is so that when the block is decrypted, the pattern can be recognised, and the correct amount of padding can be removed.
    }

    jobs <- work{buff: buff, offset: int64(offset)} // Input new work into the jobs channel.
    workingWorkers++

    if workingWorkers == workerNum {  // Once all workers are working, wait for results.
      workingWorkers = 0
      for i := 0; i < workerNum; i++ {
        wk := <-results
        e.WriteAt(wk.buff, wk.offset)   // Write the buffer at the offset specified.
      }
    }

    offset += bufferSize
    buffCount += bufferSize
  }

  if workingWorkers != 0 { // If there are still workers working, then accept the results.
    for i := 0; i < workingWorkers; i++ {
      wk := <-results
      e.WriteAt(wk.buff, wk.offset)
    }
  }

  close(jobs)   // Close the channels since the file has been finished.
  close(results)

  a.Close()  // Close the files used.
  e.Close()
}


func DecryptFile(expandedKey *[176]byte, f, w string) {
  a, err := os.Open(f)
  check(err)
  aInfo, err := a.Stat()
  check(err)

  fileSize := int(aInfo.Size())-16 // Take away length of added key for checksum

  if _, err := os.Stat(w); err == nil { // If file exists, delete it
    os.Remove(w)
  }

  var bufferSize int = DEFAULT_BUFFER_SIZE

  var workingWorkers int = 0
  var workerNum int = getNumOfCores()*2

  jobs := make(chan work, workerNum)     // Make two channels for go routines to communicate over.
  results := make(chan work, workerNum)  // Each has a buffer of length workerNum

  for i := 0; i < workerNum; i++ {
    go workerDec(jobs, results, expandedKey)
  }

  if fileSize < bufferSize {
    bufferSize = fileSize
  }

  var buffCount int = 0

  e, err := os.OpenFile(w, os.O_CREATE|os.O_WRONLY, 0644) // Open file
  check(err)

  // Check first block is key
  firstBlock := make([]byte, 16)
  _, er := io.ReadFull(a, firstBlock)
  check(er)

  if AEScheckKey.CheckKey(expandedKey, firstBlock) { // If key is valid
    offset := 0
    a.Seek(16, 0) // Move past key in encrypted file
    for buffCount < fileSize{   // While the data done is less than the fileSize
      if bufferSize > (fileSize - buffCount) {
        bufferSize = fileSize - buffCount
      }

      buff := make([]byte, bufferSize)
      _, err := io.ReadFull(a, buff)  // Ignore the number of bytes read (_)
      check(err)

      jobs<- work{buff: buff, offset: int64(offset)}
      workingWorkers++

      if workingWorkers == workerNum {
        workingWorkers = 0
        for i := 0; i < workerNum; i++ {
          wk := <-results
          e.WriteAt(wk.buff, wk.offset)
        }
      }

      offset += bufferSize
      buffCount += bufferSize
    }

    if workingWorkers != 0 {
      for i := 0; i < workingWorkers; i++ {  // Collect all but last block
        wk := <-results
        if int(wk.offset)+bufferSize >= fileSize {    // If the offset is the last block in file
          wk.buff = checkForPadding(wk.buff)
        }
        e.WriteAt(wk.buff, wk.offset)
      }
    }
    close(jobs)
    close(results)

  } else {
    panic("Invalid Key")  // If first block is not equal to the key, then do not bother trying to decrypt the file.
  }
  a.Close()
  e.Close()
}

func checkForPadding(buffer []byte) []byte {  // Checks a block for padding
  var focus byte = buffer[len(buffer)-1]
  var focusCount byte = 0
  if focus < 16 {
    for j := 1; (buffer[len(buffer)-j] == focus) && (j <= 16); j++ {
      if buffer[len(buffer)-j] == focus { focusCount++ }
    }
    if focus == focusCount {
      buffer = buffer[:len(buffer)-int(focusCount)]  // If the number of bytes at the end is equal to the value of each byte, then remove them, as it is padding.
    }
  }
  return buffer
}

// For dealing with directories
func EncryptList(expandedKey *[176]byte, fileList []string, targetList []string) {  // Encrypts list of files given to the corresponding targets.
  if len(fileList) != len(targetList) { panic("fileList and targList are different in length") }
  for i := range fileList {
    EncryptFile(expandedKey, fileList[i], targetList[i])
  }
}

func DecryptList(expandedKey *[176]byte, fileList []string, targetList []string) {  // Decrypts list of files given to the corresponding targets.
  if len(fileList) != len(targetList) { panic("fileList and targList are different in length") }
  for i := range fileList {
    DecryptFile(expandedKey, fileList[i], targetList[i])
  }
}
