package sorts

import (
  "os"
  "strconv"
)

// For keeping the decrypted name with their encrypted name
type Tuple struct {
  A os.FileInfo
  B string
}

type SearchTuple struct {
  pos int
  name string
}

func UseQuickSortSize(inp []string) []string {  // Converts inputs so that QuickSortSize can be used.
  var nums []int64
  var out []string
  for i := 0; i < len(inp); i++ {
    int, err := strconv.ParseInt(inp[i], 10, 64)
    if err != nil { panic(err) }
    nums = append(nums, int)
  }
  nums = quickSort(nums)
  for i := 0; i < len(nums); i++ {
    out = append(out, strconv.FormatInt(nums[i], 10))
  }
  return out
}

func UseQuickSortAlph(inp []string) []string { // For sorting a list that has no encrypted name
  var inpToAlph []Tuple
  var out []string
  for i := 0; i < len(inp); i++ {
    inpToAlph = append(inpToAlph, Tuple{A: nil, B: inp[i]})
  }

  inpToAlph = QuickSortAlph(inpToAlph)
  for i := 0; i < len(inpToAlph); i++ {
    out = append(out, inpToAlph[i].B)
  }
  return out
}

func UseQuickSortSearch(posList, nameList []string) []string { // Returns names in order.
  var inpToSort []SearchTuple
  var out []string
  if len(posList) != len(nameList) {
    panic("Search result lists are different sizes.")
  }
  for i := 0; i < len(posList); i++ {
    intPos, err := strconv.Atoi(posList[i])
    if err != nil { panic(err) }
    inpToSort = append(inpToSort, SearchTuple{pos: intPos, name: nameList[i]})
  }
  inpToSort = quickSortSearch(inpToSort)
  for i := 0; i < len(inpToSort); i++ {
    out = append(out, inpToSort[i].name)
  }
  return out
}

func quickSort(inp []int64) []int64 {
  if len(inp) < 2 {
    return inp
  }
  var pivot int64 = inp[int(len(inp)/2)]
  var left []int64
  var middle []int64
  var right []int64
  for i := 0; i < len(inp); i++ {
    if inp[i] < pivot {
      left = append(left, inp[i])
    } else if inp[i] > pivot {
      right = append(right, inp[i])
    } else {
      middle = append(middle, inp[i])
    }
  }
  left = quickSort(left)
  right = quickSort(right)
  return append(append(left, middle...), right...)
}

func getLower(inp []byte) []byte { // .lower() in python
  var out []byte
  for i := range inp {
    out = append(out, inp[i])
    if out[i] >= 65 && out[i] <= 90 {
      out[i] += 32 // Using ASCII table
    }
  }
  return out
}

func QuickSortAlph(inp []Tuple) []Tuple {  // Only used internally by AES
  if len(inp) < 2 {
    return inp
  }
  var pivot Tuple = inp[int(len(inp)/2)]
  var left []Tuple
  var middle []Tuple
  var right []Tuple
  for i := 0; i < len(inp); i++ {
    result := compareStrings(pivot.B, inp[i].B)
    if result == 0 {
      right = append(right, inp[i])
    } else if result == 1 {
      left = append(left, inp[i])
    } else if result == 2 {
      middle = append(middle, inp[i])
    }
  }
  left = QuickSortAlph(left)
  right = QuickSortAlph(right)
  return append(append(left, middle...), right...)
}

func quickSortSearch(inp []SearchTuple) []SearchTuple { // Sorts search results
  if len(inp) < 2 {
    return inp
  }
  var pivot int = inp[int(len(inp)/2)].pos
  var left []SearchTuple
  var middle []SearchTuple
  var right []SearchTuple
  for i := 0; i < len(inp); i++ {
    if inp[i].pos < pivot {
      left = append(left, inp[i])
    } else if inp[i].pos > pivot {
      right = append(right, inp[i])
    } else {
      middle = append(middle, inp[i])
    }
  }
  left = quickSortSearch(left)
  right = quickSortSearch(right)
  return append(append(left, middle...), right...)
}

func compareStrings(string1, string2 string) int {
  if string1 == string2 {
    return 2
  }
  string1b, string2b := []byte(string1), []byte(string2) // Get the ascii values in bytes
  string1bLower, string2bLower := getLower(string1b), getLower(string2b) // Get each string as lower case

  for i := 0; i < len(string1) && i < len(string2); i++ {
    if string2bLower[i] < string1bLower[i] {
      return 1
    } else if string2bLower[i] > string1bLower[i] {
      return 0
    } else {                                      // If the characters are both the same, then compare if they are lower case or upper case.
      if string2b[i] < string1b[i] {
        return 1
      } else if string2b[i] > string1b[i] {
        return 0
      }
    }
  }
  if len(string1) > len(string2) {      // If they are the exact same to a certain point, then compare their lengths
    return 1
  } else if len(string1) < len(string2) {
    return 0
  } else {
    panic("Strings are the exact same!")
  }
}