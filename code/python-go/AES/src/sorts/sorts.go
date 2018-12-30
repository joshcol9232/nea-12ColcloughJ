package sorts

import (
  "fmt"
  "os"
)

type Tuple struct {
  A os.FileInfo
  B string
}

func getLower(inp []byte) []byte {
  var out []byte
  for i := range inp {
    out = append(out, inp[i])
    if out[i] >= 65 && out[i] <= 90 {
      out[i] += 32 // Using ASCII table
    }
  }
  return out
}

func QuickSortAlph(inp []Tuple) []Tuple {
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

func compareStrings(string1, string2 string) int {
  if string1 == string2 {
    return 2
  }
  string1b, string2b := []byte(string1), []byte(string2)
  string1bLower, string2bLower := getLower(string1b), getLower(string2b)

  for i := 0; i < len(string1) && i < len(string2); i++ {
    if string2bLower[i] < string1bLower[i] {
      return 1
    } else if string2bLower[i] > string1bLower[i] {
      return 0
    } else {
      if string2b[i] < string1b[i] {
        return 1
      } else if string2b[i] > string1b[i] {
        return 0
      }
    }
  }
  if len(string1) > len(string2) {
    return 1
  } else if len(string1) < len(string2) {
    return 0
  } else {
    panic("Strings are the exact same!")
  }
}

func main() {
  fmt.Println("a")
}
