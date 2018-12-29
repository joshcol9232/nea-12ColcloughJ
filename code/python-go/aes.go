package main

import (
  "fmt"       // For sending output on stout
  "os"        // For opening files
  "log"
  "io"        // For reading files
  "io/ioutil" // For reading from stdin
  "encoding/hex" // For enc/decoding encrypted string
  "strings"   // For converting string key to an array of bytes
  "strconv"   // ^
  "runtime"   // For getting CPU core count
)

const DEFAULT_BUFFER_SIZE = 32768  // Define the default buffer size for enc/decrypt

// Global lookup tables.
var sBox = [256]byte {0x63,0x7C,0x77,0x7B,0xF2,0x6B,0x6F,0xC5,0x30,0x01,0x67,0x2B,0xFE,0xD7,0xAB,0x76,
                      0xCA,0x82,0xC9,0x7D,0xFA,0x59,0x47,0xF0,0xAD,0xD4,0xA2,0xAF,0x9C,0xA4,0x72,0xC0,
                      0xB7,0xFD,0x93,0x26,0x36,0x3F,0xF7,0xCC,0x34,0xA5,0xE5,0xF1,0x71,0xD8,0x31,0x15,
                      0x04,0xC7,0x23,0xC3,0x18,0x96,0x05,0x9A,0x07,0x12,0x80,0xE2,0xEB,0x27,0xB2,0x75,
                      0x09,0x83,0x2C,0x1A,0x1B,0x6E,0x5A,0xA0,0x52,0x3B,0xD6,0xB3,0x29,0xE3,0x2F,0x84,
                      0x53,0xD1,0x00,0xED,0x20,0xFC,0xB1,0x5B,0x6A,0xCB,0xBE,0x39,0x4A,0x4C,0x58,0xCF,
                      0xD0,0xEF,0xAA,0xFB,0x43,0x4D,0x33,0x85,0x45,0xF9,0x02,0x7F,0x50,0x3C,0x9F,0xA8,
                      0x51,0xA3,0x40,0x8F,0x92,0x9D,0x38,0xF5,0xBC,0xB6,0xDA,0x21,0x10,0xFF,0xF3,0xD2,
                      0xCD,0x0C,0x13,0xEC,0x5F,0x97,0x44,0x17,0xC4,0xA7,0x7E,0x3D,0x64,0x5D,0x19,0x73,
                      0x60,0x81,0x4F,0xDC,0x22,0x2A,0x90,0x88,0x46,0xEE,0xB8,0x14,0xDE,0x5E,0x0B,0xDB,
                      0xE0,0x32,0x3A,0x0A,0x49,0x06,0x24,0x5C,0xC2,0xD3,0xAC,0x62,0x91,0x95,0xE4,0x79,
                      0xE7,0xC8,0x37,0x6D,0x8D,0xD5,0x4E,0xA9,0x6C,0x56,0xF4,0xEA,0x65,0x7A,0xAE,0x08,
                      0xBA,0x78,0x25,0x2E,0x1C,0xA6,0xB4,0xC6,0xE8,0xDD,0x74,0x1F,0x4B,0xBD,0x8B,0x8A,
                      0x70,0x3E,0xB5,0x66,0x48,0x03,0xF6,0x0E,0x61,0x35,0x57,0xB9,0x86,0xC1,0x1D,0x9E,
                      0xE1,0xF8,0x98,0x11,0x69,0xD9,0x8E,0x94,0x9B,0x1E,0x87,0xE9,0xCE,0x55,0x28,0xDF,
                      0x8C,0xA1,0x89,0x0D,0xBF,0xE6,0x42,0x68,0x41,0x99,0x2D,0x0F,0xB0,0x54,0xBB,0x16}

var invSBox = [256]byte {0x52,0x09,0x6A,0xD5,0x30,0x36,0xA5,0x38,0xBF,0x40,0xA3,0x9E,0x81,0xF3,0xD7,0xFB,
                         0x7C,0xE3,0x39,0x82,0x9B,0x2F,0xFF,0x87,0x34,0x8E,0x43,0x44,0xC4,0xDE,0xE9,0xCB,
                         0x54,0x7B,0x94,0x32,0xA6,0xC2,0x23,0x3D,0xEE,0x4C,0x95,0x0B,0x42,0xFA,0xC3,0x4E,
                         0x08,0x2E,0xA1,0x66,0x28,0xD9,0x24,0xB2,0x76,0x5B,0xA2,0x49,0x6D,0x8B,0xD1,0x25,
                         0x72,0xF8,0xF6,0x64,0x86,0x68,0x98,0x16,0xD4,0xA4,0x5C,0xCC,0x5D,0x65,0xB6,0x92,
                         0x6C,0x70,0x48,0x50,0xFD,0xED,0xB9,0xDA,0x5E,0x15,0x46,0x57,0xA7,0x8D,0x9D,0x84,
                         0x90,0xD8,0xAB,0x00,0x8C,0xBC,0xD3,0x0A,0xF7,0xE4,0x58,0x05,0xB8,0xB3,0x45,0x06,
                         0xD0,0x2C,0x1E,0x8F,0xCA,0x3F,0x0F,0x02,0xC1,0xAF,0xBD,0x03,0x01,0x13,0x8A,0x6B,
                         0x3A,0x91,0x11,0x41,0x4F,0x67,0xDC,0xEA,0x97,0xF2,0xCF,0xCE,0xF0,0xB4,0xE6,0x73,
                         0x96,0xAC,0x74,0x22,0xE7,0xAD,0x35,0x85,0xE2,0xF9,0x37,0xE8,0x1C,0x75,0xDF,0x6E,
                         0x47,0xF1,0x1A,0x71,0x1D,0x29,0xC5,0x89,0x6F,0xB7,0x62,0x0E,0xAA,0x18,0xBE,0x1B,
                         0xFC,0x56,0x3E,0x4B,0xC6,0xD2,0x79,0x20,0x9A,0xDB,0xC0,0xFE,0x78,0xCD,0x5A,0xF4,
                         0x1F,0xDD,0xA8,0x33,0x88,0x07,0xC7,0x31,0xB1,0x12,0x10,0x59,0x27,0x80,0xEC,0x5F,
                         0x60,0x51,0x7F,0xA9,0x19,0xB5,0x4A,0x0D,0x2D,0xE5,0x7A,0x9F,0x93,0xC9,0x9C,0xEF,
                         0xA0,0xE0,0x3B,0x4D,0xAE,0x2A,0xF5,0xB0,0xC8,0xEB,0xBB,0x3C,0x83,0x53,0x99,0x61,
                         0x17,0x2B,0x04,0x7E,0xBA,0x77,0xD6,0x26,0xE1,0x69,0x14,0x63,0x55,0x21,0x0C,0x7D}

var rcon = [256]byte {0x8d,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d,0x9a,    // https:// en.wikipedia.org/wiki/Rijndael_key_schedule
                      0x2f,0x5e,0xbc,0x63,0xc6,0x97,0x35,0x6a,0xd4,0xb3,0x7d,0xfa,0xef,0xc5,0x91,0x39,
                      0x72,0xe4,0xd3,0xbd,0x61,0xc2,0x9f,0x25,0x4a,0x94,0x33,0x66,0xcc,0x83,0x1d,0x3a,
                      0x74,0xe8,0xcb,0x8d,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,
                      0xab,0x4d,0x9a,0x2f,0x5e,0xbc,0x63,0xc6,0x97,0x35,0x6a,0xd4,0xb3,0x7d,0xfa,0xef,
                      0xc5,0x91,0x39,0x72,0xe4,0xd3,0xbd,0x61,0xc2,0x9f,0x25,0x4a,0x94,0x33,0x66,0xcc,
                      0x83,0x1d,0x3a,0x74,0xe8,0xcb,0x8d,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,
                      0x36,0x6c,0xd8,0xab,0x4d,0x9a,0x2f,0x5e,0xbc,0x63,0xc6,0x97,0x35,0x6a,0xd4,0xb3,
                      0x7d,0xfa,0xef,0xc5,0x91,0x39,0x72,0xe4,0xd3,0xbd,0x61,0xc2,0x9f,0x25,0x4a,0x94,
                      0x33,0x66,0xcc,0x83,0x1d,0x3a,0x74,0xe8,0xcb,0x8d,0x01,0x02,0x04,0x08,0x10,0x20,
                      0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d,0x9a,0x2f,0x5e,0xbc,0x63,0xc6,0x97,0x35,
                      0x6a,0xd4,0xb3,0x7d,0xfa,0xef,0xc5,0x91,0x39,0x72,0xe4,0xd3,0xbd,0x61,0xc2,0x9f,
                      0x25,0x4a,0x94,0x33,0x66,0xcc,0x83,0x1d,0x3a,0x74,0xe8,0xcb,0x8d,0x01,0x02,0x04,
                      0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d,0x9a,0x2f,0x5e,0xbc,0x63,
                      0xc6,0x97,0x35,0x6a,0xd4,0xb3,0x7d,0xfa,0xef,0xc5,0x91,0x39,0x72,0xe4,0xd3,0xbd,
                      0x61,0xc2,0x9f,0x25,0x4a,0x94,0x33,0x66,0xcc,0x83,0x1d,0x3a,0x74,0xe8,0xcb,0x8d}

var mul2 = [256]byte {0x00,0x02,0x04,0x06,0x08,0x0a,0x0c,0x0e,0x10,0x12,0x14,0x16,0x18,0x1a,0x1c,0x1e,
                      0x20,0x22,0x24,0x26,0x28,0x2a,0x2c,0x2e,0x30,0x32,0x34,0x36,0x38,0x3a,0x3c,0x3e,
                      0x40,0x42,0x44,0x46,0x48,0x4a,0x4c,0x4e,0x50,0x52,0x54,0x56,0x58,0x5a,0x5c,0x5e,
                      0x60,0x62,0x64,0x66,0x68,0x6a,0x6c,0x6e,0x70,0x72,0x74,0x76,0x78,0x7a,0x7c,0x7e,
                      0x80,0x82,0x84,0x86,0x88,0x8a,0x8c,0x8e,0x90,0x92,0x94,0x96,0x98,0x9a,0x9c,0x9e,
                      0xa0,0xa2,0xa4,0xa6,0xa8,0xaa,0xac,0xae,0xb0,0xb2,0xb4,0xb6,0xb8,0xba,0xbc,0xbe,
                      0xc0,0xc2,0xc4,0xc6,0xc8,0xca,0xcc,0xce,0xd0,0xd2,0xd4,0xd6,0xd8,0xda,0xdc,0xde,
                      0xe0,0xe2,0xe4,0xe6,0xe8,0xea,0xec,0xee,0xf0,0xf2,0xf4,0xf6,0xf8,0xfa,0xfc,0xfe,
                      0x1b,0x19,0x1f,0x1d,0x13,0x11,0x17,0x15,0x0b,0x09,0x0f,0x0d,0x03,0x01,0x07,0x05,
                      0x3b,0x39,0x3f,0x3d,0x33,0x31,0x37,0x35,0x2b,0x29,0x2f,0x2d,0x23,0x21,0x27,0x25,
                      0x5b,0x59,0x5f,0x5d,0x53,0x51,0x57,0x55,0x4b,0x49,0x4f,0x4d,0x43,0x41,0x47,0x45,
                      0x7b,0x79,0x7f,0x7d,0x73,0x71,0x77,0x75,0x6b,0x69,0x6f,0x6d,0x63,0x61,0x67,0x65,
                      0x9b,0x99,0x9f,0x9d,0x93,0x91,0x97,0x95,0x8b,0x89,0x8f,0x8d,0x83,0x81,0x87,0x85,
                      0xbb,0xb9,0xbf,0xbd,0xb3,0xb1,0xb7,0xb5,0xab,0xa9,0xaf,0xad,0xa3,0xa1,0xa7,0xa5,
                      0xdb,0xd9,0xdf,0xdd,0xd3,0xd1,0xd7,0xd5,0xcb,0xc9,0xcf,0xcd,0xc3,0xc1,0xc7,0xc5,
                      0xfb,0xf9,0xff,0xfd,0xf3,0xf1,0xf7,0xf5,0xeb,0xe9,0xef,0xed,0xe3,0xe1,0xe7,0xe5}

var mul3 = [256]byte {0x00,0x03,0x06,0x05,0x0c,0x0f,0x0a,0x09,0x18,0x1b,0x1e,0x1d,0x14,0x17,0x12,0x11,
                      0x30,0x33,0x36,0x35,0x3c,0x3f,0x3a,0x39,0x28,0x2b,0x2e,0x2d,0x24,0x27,0x22,0x21,
                      0x60,0x63,0x66,0x65,0x6c,0x6f,0x6a,0x69,0x78,0x7b,0x7e,0x7d,0x74,0x77,0x72,0x71,
                      0x50,0x53,0x56,0x55,0x5c,0x5f,0x5a,0x59,0x48,0x4b,0x4e,0x4d,0x44,0x47,0x42,0x41,
                      0xc0,0xc3,0xc6,0xc5,0xcc,0xcf,0xca,0xc9,0xd8,0xdb,0xde,0xdd,0xd4,0xd7,0xd2,0xd1,
                      0xf0,0xf3,0xf6,0xf5,0xfc,0xff,0xfa,0xf9,0xe8,0xeb,0xee,0xed,0xe4,0xe7,0xe2,0xe1,
                      0xa0,0xa3,0xa6,0xa5,0xac,0xaf,0xaa,0xa9,0xb8,0xbb,0xbe,0xbd,0xb4,0xb7,0xb2,0xb1,
                      0x90,0x93,0x96,0x95,0x9c,0x9f,0x9a,0x99,0x88,0x8b,0x8e,0x8d,0x84,0x87,0x82,0x81,
                      0x9b,0x98,0x9d,0x9e,0x97,0x94,0x91,0x92,0x83,0x80,0x85,0x86,0x8f,0x8c,0x89,0x8a,
                      0xab,0xa8,0xad,0xae,0xa7,0xa4,0xa1,0xa2,0xb3,0xb0,0xb5,0xb6,0xbf,0xbc,0xb9,0xba,
                      0xfb,0xf8,0xfd,0xfe,0xf7,0xf4,0xf1,0xf2,0xe3,0xe0,0xe5,0xe6,0xef,0xec,0xe9,0xea,
                      0xcb,0xc8,0xcd,0xce,0xc7,0xc4,0xc1,0xc2,0xd3,0xd0,0xd5,0xd6,0xdf,0xdc,0xd9,0xda,
                      0x5b,0x58,0x5d,0x5e,0x57,0x54,0x51,0x52,0x43,0x40,0x45,0x46,0x4f,0x4c,0x49,0x4a,
                      0x6b,0x68,0x6d,0x6e,0x67,0x64,0x61,0x62,0x73,0x70,0x75,0x76,0x7f,0x7c,0x79,0x7a,
                      0x3b,0x38,0x3d,0x3e,0x37,0x34,0x31,0x32,0x23,0x20,0x25,0x26,0x2f,0x2c,0x29,0x2a,
                      0x0b,0x08,0x0d,0x0e,0x07,0x04,0x01,0x02,0x13,0x10,0x15,0x16,0x1f,0x1c,0x19,0x1a}

var mul9 = [256]byte {0x00,0x09,0x12,0x1b,0x24,0x2d,0x36,0x3f,0x48,0x41,0x5a,0x53,0x6c,0x65,0x7e,0x77,
                      0x90,0x99,0x82,0x8b,0xb4,0xbd,0xa6,0xaf,0xd8,0xd1,0xca,0xc3,0xfc,0xf5,0xee,0xe7,
                      0x3b,0x32,0x29,0x20,0x1f,0x16,0x0d,0x04,0x73,0x7a,0x61,0x68,0x57,0x5e,0x45,0x4c,
                      0xab,0xa2,0xb9,0xb0,0x8f,0x86,0x9d,0x94,0xe3,0xea,0xf1,0xf8,0xc7,0xce,0xd5,0xdc,
                      0x76,0x7f,0x64,0x6d,0x52,0x5b,0x40,0x49,0x3e,0x37,0x2c,0x25,0x1a,0x13,0x08,0x01,
                      0xe6,0xef,0xf4,0xfd,0xc2,0xcb,0xd0,0xd9,0xae,0xa7,0xbc,0xb5,0x8a,0x83,0x98,0x91,
                      0x4d,0x44,0x5f,0x56,0x69,0x60,0x7b,0x72,0x05,0x0c,0x17,0x1e,0x21,0x28,0x33,0x3a,
                      0xdd,0xd4,0xcf,0xc6,0xf9,0xf0,0xeb,0xe2,0x95,0x9c,0x87,0x8e,0xb1,0xb8,0xa3,0xaa,
                      0xec,0xe5,0xfe,0xf7,0xc8,0xc1,0xda,0xd3,0xa4,0xad,0xb6,0xbf,0x80,0x89,0x92,0x9b,
                      0x7c,0x75,0x6e,0x67,0x58,0x51,0x4a,0x43,0x34,0x3d,0x26,0x2f,0x10,0x19,0x02,0x0b,
                      0xd7,0xde,0xc5,0xcc,0xf3,0xfa,0xe1,0xe8,0x9f,0x96,0x8d,0x84,0xbb,0xb2,0xa9,0xa0,
                      0x47,0x4e,0x55,0x5c,0x63,0x6a,0x71,0x78,0x0f,0x06,0x1d,0x14,0x2b,0x22,0x39,0x30,
                      0x9a,0x93,0x88,0x81,0xbe,0xb7,0xac,0xa5,0xd2,0xdb,0xc0,0xc9,0xf6,0xff,0xe4,0xed,
                      0x0a,0x03,0x18,0x11,0x2e,0x27,0x3c,0x35,0x42,0x4b,0x50,0x59,0x66,0x6f,0x74,0x7d,
                      0xa1,0xa8,0xb3,0xba,0x85,0x8c,0x97,0x9e,0xe9,0xe0,0xfb,0xf2,0xcd,0xc4,0xdf,0xd6,
                      0x31,0x38,0x23,0x2a,0x15,0x1c,0x07,0x0e,0x79,0x70,0x6b,0x62,0x5d,0x54,0x4f,0x46}

var mul11 = [256]byte {0x00,0x0b,0x16,0x1d,0x2c,0x27,0x3a,0x31,0x58,0x53,0x4e,0x45,0x74,0x7f,0x62,0x69,
                       0xb0,0xbb,0xa6,0xad,0x9c,0x97,0x8a,0x81,0xe8,0xe3,0xfe,0xf5,0xc4,0xcf,0xd2,0xd9,
                       0x7b,0x70,0x6d,0x66,0x57,0x5c,0x41,0x4a,0x23,0x28,0x35,0x3e,0x0f,0x04,0x19,0x12,
                       0xcb,0xc0,0xdd,0xd6,0xe7,0xec,0xf1,0xfa,0x93,0x98,0x85,0x8e,0xbf,0xb4,0xa9,0xa2,
                       0xf6,0xfd,0xe0,0xeb,0xda,0xd1,0xcc,0xc7,0xae,0xa5,0xb8,0xb3,0x82,0x89,0x94,0x9f,
                       0x46,0x4d,0x50,0x5b,0x6a,0x61,0x7c,0x77,0x1e,0x15,0x08,0x03,0x32,0x39,0x24,0x2f,
                       0x8d,0x86,0x9b,0x90,0xa1,0xaa,0xb7,0xbc,0xd5,0xde,0xc3,0xc8,0xf9,0xf2,0xef,0xe4,
                       0x3d,0x36,0x2b,0x20,0x11,0x1a,0x07,0x0c,0x65,0x6e,0x73,0x78,0x49,0x42,0x5f,0x54,
                       0xf7,0xfc,0xe1,0xea,0xdb,0xd0,0xcd,0xc6,0xaf,0xa4,0xb9,0xb2,0x83,0x88,0x95,0x9e,
                       0x47,0x4c,0x51,0x5a,0x6b,0x60,0x7d,0x76,0x1f,0x14,0x09,0x02,0x33,0x38,0x25,0x2e,
                       0x8c,0x87,0x9a,0x91,0xa0,0xab,0xb6,0xbd,0xd4,0xdf,0xc2,0xc9,0xf8,0xf3,0xee,0xe5,
                       0x3c,0x37,0x2a,0x21,0x10,0x1b,0x06,0x0d,0x64,0x6f,0x72,0x79,0x48,0x43,0x5e,0x55,
                       0x01,0x0a,0x17,0x1c,0x2d,0x26,0x3b,0x30,0x59,0x52,0x4f,0x44,0x75,0x7e,0x63,0x68,
                       0xb1,0xba,0xa7,0xac,0x9d,0x96,0x8b,0x80,0xe9,0xe2,0xff,0xf4,0xc5,0xce,0xd3,0xd8,
                       0x7a,0x71,0x6c,0x67,0x56,0x5d,0x40,0x4b,0x22,0x29,0x34,0x3f,0x0e,0x05,0x18,0x13,
                       0xca,0xc1,0xdc,0xd7,0xe6,0xed,0xf0,0xfb,0x92,0x99,0x84,0x8f,0xbe,0xb5,0xa8,0xa3}

var mul13 = [256]byte {0x00,0x0d,0x1a,0x17,0x34,0x39,0x2e,0x23,0x68,0x65,0x72,0x7f,0x5c,0x51,0x46,0x4b,
                       0xd0,0xdd,0xca,0xc7,0xe4,0xe9,0xfe,0xf3,0xb8,0xb5,0xa2,0xaf,0x8c,0x81,0x96,0x9b,
                       0xbb,0xb6,0xa1,0xac,0x8f,0x82,0x95,0x98,0xd3,0xde,0xc9,0xc4,0xe7,0xea,0xfd,0xf0,
                       0x6b,0x66,0x71,0x7c,0x5f,0x52,0x45,0x48,0x03,0x0e,0x19,0x14,0x37,0x3a,0x2d,0x20,
                       0x6d,0x60,0x77,0x7a,0x59,0x54,0x43,0x4e,0x05,0x08,0x1f,0x12,0x31,0x3c,0x2b,0x26,
                       0xbd,0xb0,0xa7,0xaa,0x89,0x84,0x93,0x9e,0xd5,0xd8,0xcf,0xc2,0xe1,0xec,0xfb,0xf6,
                       0xd6,0xdb,0xcc,0xc1,0xe2,0xef,0xf8,0xf5,0xbe,0xb3,0xa4,0xa9,0x8a,0x87,0x90,0x9d,
                       0x06,0x0b,0x1c,0x11,0x32,0x3f,0x28,0x25,0x6e,0x63,0x74,0x79,0x5a,0x57,0x40,0x4d,
                       0xda,0xd7,0xc0,0xcd,0xee,0xe3,0xf4,0xf9,0xb2,0xbf,0xa8,0xa5,0x86,0x8b,0x9c,0x91,
                       0x0a,0x07,0x10,0x1d,0x3e,0x33,0x24,0x29,0x62,0x6f,0x78,0x75,0x56,0x5b,0x4c,0x41,
                       0x61,0x6c,0x7b,0x76,0x55,0x58,0x4f,0x42,0x09,0x04,0x13,0x1e,0x3d,0x30,0x27,0x2a,
                       0xb1,0xbc,0xab,0xa6,0x85,0x88,0x9f,0x92,0xd9,0xd4,0xc3,0xce,0xed,0xe0,0xf7,0xfa,
                       0xb7,0xba,0xad,0xa0,0x83,0x8e,0x99,0x94,0xdf,0xd2,0xc5,0xc8,0xeb,0xe6,0xf1,0xfc,
                       0x67,0x6a,0x7d,0x70,0x53,0x5e,0x49,0x44,0x0f,0x02,0x15,0x18,0x3b,0x36,0x21,0x2c,
                       0x0c,0x01,0x16,0x1b,0x38,0x35,0x22,0x2f,0x64,0x69,0x7e,0x73,0x50,0x5d,0x4a,0x47,
                       0xdc,0xd1,0xc6,0xcb,0xe8,0xe5,0xf2,0xff,0xb4,0xb9,0xae,0xa3,0x80,0x8d,0x9a,0x97}

var mul14 = [256]byte {0x00,0x0e,0x1c,0x12,0x38,0x36,0x24,0x2a,0x70,0x7e,0x6c,0x62,0x48,0x46,0x54,0x5a,
                       0xe0,0xee,0xfc,0xf2,0xd8,0xd6,0xc4,0xca,0x90,0x9e,0x8c,0x82,0xa8,0xa6,0xb4,0xba,
                       0xdb,0xd5,0xc7,0xc9,0xe3,0xed,0xff,0xf1,0xab,0xa5,0xb7,0xb9,0x93,0x9d,0x8f,0x81,
                       0x3b,0x35,0x27,0x29,0x03,0x0d,0x1f,0x11,0x4b,0x45,0x57,0x59,0x73,0x7d,0x6f,0x61,
                       0xad,0xa3,0xb1,0xbf,0x95,0x9b,0x89,0x87,0xdd,0xd3,0xc1,0xcf,0xe5,0xeb,0xf9,0xf7,
                       0x4d,0x43,0x51,0x5f,0x75,0x7b,0x69,0x67,0x3d,0x33,0x21,0x2f,0x05,0x0b,0x19,0x17,
                       0x76,0x78,0x6a,0x64,0x4e,0x40,0x52,0x5c,0x06,0x08,0x1a,0x14,0x3e,0x30,0x22,0x2c,
                       0x96,0x98,0x8a,0x84,0xae,0xa0,0xb2,0xbc,0xe6,0xe8,0xfa,0xf4,0xde,0xd0,0xc2,0xcc,
                       0x41,0x4f,0x5d,0x53,0x79,0x77,0x65,0x6b,0x31,0x3f,0x2d,0x23,0x09,0x07,0x15,0x1b,
                       0xa1,0xaf,0xbd,0xb3,0x99,0x97,0x85,0x8b,0xd1,0xdf,0xcd,0xc3,0xe9,0xe7,0xf5,0xfb,
                       0x9a,0x94,0x86,0x88,0xa2,0xac,0xbe,0xb0,0xea,0xe4,0xf6,0xf8,0xd2,0xdc,0xce,0xc0,
                       0x7a,0x74,0x66,0x68,0x42,0x4c,0x5e,0x50,0x0a,0x04,0x16,0x18,0x32,0x3c,0x2e,0x20,
                       0xec,0xe2,0xf0,0xfe,0xd4,0xda,0xc8,0xc6,0x9c,0x92,0x80,0x8e,0xa4,0xaa,0xb8,0xb6,
                       0x0c,0x02,0x10,0x1e,0x34,0x3a,0x28,0x26,0x7c,0x72,0x60,0x6e,0x44,0x4a,0x58,0x56,
                       0x37,0x39,0x2b,0x25,0x0f,0x01,0x13,0x1d,0x47,0x49,0x5b,0x55,0x7f,0x71,0x63,0x6d,
                       0xd7,0xd9,0xcb,0xc5,0xef,0xe1,0xf3,0xfd,0xa7,0xa9,0xbb,0xb5,0x9f,0x91,0x83,0x8d}


func keyExpansionCore(inp [4]byte, i int) [4]byte {
  // Shift the inp left by moving the first byte to the end (rotate).
  inp[0], inp[1], inp[2], inp[3] = inp[1], inp[2], inp[3], inp[0]

  // S-Box the bytes
  inp[0], inp[1], inp[2], inp[3] = sBox[inp[0]], sBox[inp[1]], sBox[inp[2]], sBox[inp[3]]

  // rcon, the round constant
  inp[0] ^= rcon[i]

  return inp
}

func expandKey(inputKey []byte) [176]byte {
  var expandedKeys [176]byte
  // first 16 bytes of the expandedKeys should be the same 16 as the original key
  for i := 0; i < 16; i++ {
    expandedKeys[i] = inputKey[i]
  }
  var bytesGenerated int = 16 // needs to get to 176 to fill expandedKeys with 11 keys, one for every round.
  var rconIteration int = 1
  var temp [4]byte

  for bytesGenerated < 176{
    // Read 4 bytes for use in keyExpansionCore
    copy(temp[:], expandedKeys[bytesGenerated-4:bytesGenerated])

    if bytesGenerated % 16 == 0 {    // Keys are length 16 bytes so every 16 bytes generated, expand.
      temp = keyExpansionCore(temp, rconIteration)
      rconIteration += 1
    }

    for y := 0; y < 4; y++ {
      expandedKeys[bytesGenerated] = expandedKeys[bytesGenerated - 16] ^ temp[y]  // XOR first 4 bytes of previous key with the temporary list.
      bytesGenerated += 1
    }
  }

  return expandedKeys
}

func addRoundKey(state []byte, roundKey []byte) {       // Add round key is also it's own inverse
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  state[ 0]^roundKey[ 0], state[ 1]^roundKey[ 1], state[ 2]^roundKey[ 2], state[ 3]^roundKey[ 3],
  state[ 4]^roundKey[ 4], state[ 5]^roundKey[ 5], state[ 6]^roundKey[ 6], state[ 7]^roundKey[ 7],
  state[ 8]^roundKey[ 8], state[ 9]^roundKey[ 9], state[10]^roundKey[10], state[11]^roundKey[11],
  state[12]^roundKey[12], state[13]^roundKey[13], state[14]^roundKey[14], state[15]^roundKey[15]
}

func subBytes(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  sBox[state[ 0]], sBox[state[ 1]], sBox[state[ 2]], sBox[state[ 3]],
  sBox[state[ 4]], sBox[state[ 5]], sBox[state[ 6]], sBox[state[ 7]],
  sBox[state[ 8]], sBox[state[ 9]], sBox[state[10]], sBox[state[11]],
  sBox[state[12]], sBox[state[13]], sBox[state[14]], sBox[state[15]]
}

func invSubBytes(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  invSBox[state[ 0]], invSBox[state[ 1]], invSBox[state[ 2]], invSBox[state[ 3]],
  invSBox[state[ 4]], invSBox[state[ 5]], invSBox[state[ 6]], invSBox[state[ 7]],
  invSBox[state[ 8]], invSBox[state[ 9]], invSBox[state[10]], invSBox[state[11]],
  invSBox[state[12]], invSBox[state[13]], invSBox[state[14]], invSBox[state[15]]
}

func shiftRows(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  state[ 0], state[ 5], state[10], state[15],
  state[ 4], state[ 9], state[14], state[ 3],
  state[ 8], state[13], state[ 2], state[ 7],
  state[12], state[ 1], state[ 6], state[11]
}
  //  Shifts it like this:
  //
  //  0  4  8 12         0  4  8 12   Shifted left by 0
  //  1  5  9 13  ---->  5  9 13  1   Shifted left by 1
  //  2  6 10 14  ----> 10 14  2  6   Shifted left by 2
  //  3  7 11 15        15  3  7 11   Shifted left by 3


func invShiftRows(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  state[ 0], state[13], state[10], state[ 7],
  state[ 4], state[ 1], state[14], state[11],
  state[ 8], state[ 5], state[ 2], state[15],
  state[12], state[ 9], state[ 6], state[ 3]
}
  //   0  4  8 12         0  4  8 12   Shifted right by 0
  //   5  9 13  1  ---->  1  5  9 13   Shifted right by 1
  //  10 14  2  6  ---->  2  6 10 14   Shifted right by 2
  //  15  3  7 11         3  7 11 15   Shifted right by 3


func mixColumns(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  mul2[state[ 0]] ^ mul3[state[ 1]] ^ state[ 2] ^ state[ 3],
  state[ 0] ^ mul2[state[ 1]] ^ mul3[state[ 2]] ^ state[ 3],
  state[ 0] ^ state[ 1] ^ mul2[state[ 2]] ^ mul3[state[ 3]],
  mul3[state[ 0]] ^ state[ 1] ^ state[ 2] ^ mul2[state[ 3]],

  mul2[state[ 4]] ^ mul3[state[ 5]] ^ state[ 6] ^ state[ 7],
  state[ 4] ^ mul2[state [5]] ^ mul3[state[ 6]] ^ state[ 7],
  state[ 4] ^ state[ 5] ^ mul2[state[ 6]] ^ mul3[state[ 7]],
  mul3[state[ 4]] ^ state[ 5] ^ state[ 6] ^ mul2[state[ 7]],

  mul2[state[ 8]] ^ mul3[state[ 9]] ^ state[10] ^ state[11],
  state[ 8] ^ mul2[state[ 9]] ^ mul3[state[10]] ^ state[11],
  state[ 8] ^ state[ 9] ^ mul2[state[10]] ^ mul3[state[11]],
  mul3[state[ 8]] ^ state[ 9] ^ state[10] ^ mul2[state[11]],

  mul2[state[12]] ^ mul3[state[13]] ^ state[14] ^ state[15],
  state[12] ^ mul2[state[13]] ^ mul3[state[14]] ^ state[15],
  state[12] ^ state[13] ^ mul2[state[14]] ^ mul3[state[15]],
  mul3[state[12]] ^ state[13] ^ state[14] ^ mul2[state[15]]
}

func invMixColumns(state []byte) {
  state[ 0], state[ 1], state[ 2], state[ 3],
  state[ 4], state[ 5], state[ 6], state[ 7],
  state[ 8], state[ 9], state[10], state[11],
  state[12], state[13], state[14], state[15] =

  mul14[state[ 0]] ^ mul11[state[ 1]] ^ mul13[state[ 2]] ^ mul9[state[ 3]],
  mul9[state[ 0]] ^ mul14[state[ 1]] ^ mul11[state[ 2]] ^ mul13[state[ 3]],
  mul13[state[ 0]] ^ mul9[state[ 1]] ^ mul14[state[ 2]] ^ mul11[state[ 3]],
  mul11[state[ 0]] ^ mul13[state[ 1]] ^ mul9[state[ 2]] ^ mul14[state[ 3]],

  mul14[state[ 4]] ^ mul11[state[ 5]] ^ mul13[state[ 6]] ^ mul9[state[ 7]],
  mul9[state[ 4]] ^ mul14[state[ 5]] ^ mul11[state[ 6]] ^ mul13[state[ 7]],
  mul13[state[ 4]] ^ mul9[state[ 5]] ^ mul14[state[ 6]] ^ mul11[state[ 7]],
  mul11[state[ 4]] ^ mul13[state[ 5]] ^ mul9[state[ 6]] ^ mul14[state[ 7]],

  mul14[state[ 8]] ^ mul11[state[ 9]] ^ mul13[state[10]] ^ mul9[state[11]],
  mul9[state[ 8]] ^ mul14[state[ 9]] ^ mul11[state[10]] ^ mul13[state[11]],
  mul13[state[ 8]] ^ mul9[state[ 9]] ^ mul14[state[10]] ^ mul11[state[11]],
  mul11[state[ 8]] ^ mul13[state[ 9]] ^ mul9[state[10]] ^ mul14[state[11]],

  mul14[state[12]] ^ mul11[state[13]] ^ mul13[state[14]] ^ mul9[state[15]],
  mul9[state[12]] ^ mul14[state[13]] ^ mul11[state[14]] ^ mul13[state[15]],
  mul13[state[12]] ^ mul9[state[13]] ^ mul14[state[14]] ^ mul11[state[15]],
  mul11[state[12]] ^ mul13[state[13]] ^ mul9[state[14]] ^ mul14[state[15]]
}


func encrypt(state []byte, expandedKeys [176]byte) {
  addRoundKey(state, expandedKeys[:16])

  for i := 0; i < 144; i += 16 {    // 9 regular rounds * 16 = 144
    subBytes(state)
    shiftRows(state)
    mixColumns(state)
    addRoundKey(state, expandedKeys[i+16:i+32])
  }
  // Last round
  subBytes(state)
  shiftRows(state)
  addRoundKey(state, expandedKeys[160:])
}

func decrypt(state []byte, expandedKeys [176]byte) {
  addRoundKey(state, expandedKeys[160:])
  invShiftRows(state)
  invSubBytes(state)

  for i := 144; i != 0; i -= 16 {
    addRoundKey(state, expandedKeys[i:i+16])
    invMixColumns(state)
    invShiftRows(state)
    invSubBytes(state)
  }
  // Last round
  addRoundKey(state, expandedKeys[:16])
}


func check(e error) {     // Used for checking errors when reading/writing to files.
  if e != nil {
    panic(e)
  }
}

func getNumOfCores() int {  //Gets the number of cores so it determines buffer size.
  maxProcs := runtime.GOMAXPROCS(0)
  numCPU := runtime.NumCPU()
  if maxProcs < numCPU {
    return maxProcs
  }
  return numCPU
}

func compareSlices(slice1, slice2 []byte) bool {    // Function used for checking first block of a file with the key when decrypting.
  if len(slice1) != len(slice2) {
    return false
  } else {
    for i := 0; i < len(slice1); i++ {
      if slice1[i] != slice2[i] {
        return false
      }
    }
  }
  return true
}

// For holding the buffer to be worked on and the offset together, so it can be written to the file in the correct place at the end.
type work struct {
  buff []byte
  offset int64
}

func workerEnc(jobs <-chan work, results chan<- work, expandedKeys [176]byte) {    // Encrypts a chunk when given (a chunk of length bufferSize)
  for job := range jobs {
    for i := 0; i < len(job.buff); i += 16 {
      encrypt(job.buff[i:i+16], expandedKeys)
    }
    results<- work{buff: job.buff, offset: job.offset}
  }
}

func workerDec(jobs <-chan work, results chan<- work, expandedKeys [176]byte, fileSize int) {
  for job := range jobs {
    for i := 0; i < len(job.buff); i += 16 {
      if (fileSize - int(job.offset) - i) == 16 {     // If on the last block of whole file
        decrypt(job.buff[i:i+16], expandedKeys)   // Decrypt 128 bit chunk of buffer
        // Store in variable as we are going to change it.
        var focus int = int(job.buff[i+15])
        var focusCount int = 0

        if focus < 16 {     // If the last number is less than 16 (the maximum amount of padding to add is 15)
          for j := 15; (int(job.buff[i+j]) == focus) && (j > 0); j-- {
            if int(job.buff[i+j]) == focus { focusCount++ }
          }
          if focus == focusCount {
            job.buff = append(job.buff[:(i+16-focus)], job.buff[i+16:]...)  // If the number of bytes at the end is equal to the value of each byte, then remove them, as it is padding.
          }
        }
      } else {
        decrypt(job.buff[i:i+16], expandedKeys)
      }
    }
    results<- work{buff: job.buff, offset: job.offset}
  }
}

func encryptFile(expandedKeys [176]byte, f, w string) {
  a, err := os.Open(f)    // Open original file to get statistics and read data.
  check(err)
  aInfo, err := a.Stat()  // Get statistics
  check(err)

  fileSize := int(aInfo.Size()) // Get size of original file

  if _, err := os.Stat(w); err == nil { // If file already exists, delete it
    os.Remove(w)
  }

  var workingWorkers int = 0
  var workerNum int = getNumOfCores()*2  // 2 go routines per core got the most performance (didn't want usage above 90%)

  jobs := make(chan work, workerNum)     // Make two channels for go routines to communicate over.
  results := make(chan work, workerNum)  // Each has a buffer of length workerNum

  /*
  Each go routine will be given access to the job queue, where each worker then waits to complete the job.
  Once the job is completed, the go routine pushes the result onto the result queue, where the result can be
  recieved by the main routine. The results are read once all of the go routines are busy, or if the file
  is completed, then the remaining workers still working are asked for their results.
  */

  for i := 0; i < workerNum; i++ { // Use all cores bar one
    go workerEnc(jobs, results, expandedKeys)
  }

  var bufferSize int = DEFAULT_BUFFER_SIZE

  if fileSize < bufferSize {    // If the buffer size is larger than the file size, just read the whole file.
    bufferSize = fileSize
  }

  var buffCount int = 0   // Keeps track of how far through the file we are

  e, err := os.OpenFile(w, os.O_CREATE|os.O_WRONLY, 0644) // Open file for writing.
  check(err)  // Check it opened correctly

  // Append key so that when decrypting, the key can be checked before decrypting the whole file.
  var originalKey = expandedKeys[:16]
  encrypt(originalKey, expandedKeys)
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

    jobs <- work{buff: buff, offset: int64(offset)}
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
    for i := 0; i < workingWorkers; i++ {
      wk := <-results
      e.WriteAt(wk.buff, wk.offset)
    }
  }

  close(jobs)
  close(results)

  a.Close()  // Close the files used.
  e.Close()
}


func decryptFile(expandedKeys [176]byte, f, w string) {
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

  jobs := make(chan work, )
  results := make(chan work)

  for i := 0; i < workerNum; i++ { // Use all cores bar one
    go workerDec(jobs, results, expandedKeys, fileSize)
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
  decrypt(firstBlock, expandedKeys)

  if compareSlices(expandedKeys[:16], firstBlock) { // If key is valid
    offset := 0
    a.Seek(16, 0) // Move past key
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
      for i := 0; i < workingWorkers; i++ {
        wk := <-results
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

func encryptList(expandedKeys [176]byte, fileList []string, targetList []string) {  // Encrypts list of files given to the corresponding targets.
  if len(fileList) != len(targetList) { panic("fileList and targList are different in length") }
  for i := range fileList {
    log.Output(0, fileList[i]+" FILE")
    encryptFile(expandedKeys, fileList[i], targetList[i])
  }
}

func decryptList(expandedKeys [176]byte, fileList []string, targetList []string) {  // Decrypts list of files given to the corresponding targets.
  if len(fileList) != len(targetList) { panic("fileList and targList are different in length") }
  for i := range fileList {
    decryptFile(expandedKeys, fileList[i], targetList[i])
  }
}

func getLists(expandedKeys [176]byte, fileList, targetList []string, folder, target string) ([]string, []string) { // Also makes the folders required
  os.Mkdir(target, os.ModePerm)
  list, err := ioutil.ReadDir(folder)
  check(err)
  for i := range list {
    if len(list[i].Name()) < 127 { // Max is 255 for file names, but this will double due to hex.
      if list[i].IsDir() {
        fileList, targetList = getLists(expandedKeys, fileList, targetList, folder+list[i].Name()+"/", target+encryptFileName(expandedKeys, list[i].Name())+"/")
      } else {
        fileList   = append(fileList, folder+list[i].Name())
        targetList = append(targetList, target+encryptFileName(expandedKeys, list[i].Name()))
      }
    } else {
      log.Output(0, "Name too long: "+list[i].Name())
    }
  }
  return fileList, targetList
}

func encryptFileName(expandedKeys [176]byte, name string) string {
  var byteName = []byte(name)

  for len(byteName) % 16 != 0 {   // Pad with 0's
    byteName = append(byteName, 0)
  }

  for i := 0; i < len(byteName); i += 16 {
    encrypt(byteName[i:i+16], expandedKeys)  // Done by reference so does not need to be assigned
  }

  return hex.EncodeToString(byteName)
}

func decryptFileName(expandedKeys [176]byte, hexName string) string {
  byteName, err := hex.DecodeString(hexName)
  check(err)

  for i := 0; i < len(byteName); i += 16 {
    decrypt(byteName[i:i+16], expandedKeys)
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

func encryptListOfString(expandedKeys [176]byte, l []string) []string {
  for i := range l {
    l[i] = encryptFileName(expandedKeys, l[i])
  }
  return l
}

func decryptListOfString(expandedKeys [176]byte, l []string) []string {
  for i := range l {
    l[i] = decryptFileName(expandedKeys, l[i])
  }
  return l
}


func checkKey(key []byte, f string) bool {
  a, err := os.Open(f)    // Open an encrypted file to check first block against key
  check(err)

  var expandedKeys [176]byte

  expandedKeys = expandKey(key) // Expand the key

  // Check first block is key
  firstBlock := make([]byte, 16)
  _, er := io.ReadFull(a, firstBlock)   // Fill a slice of length 16 with the first block of 16 bytes in the file.
  check(er)
  decrypt(firstBlock, expandedKeys)    // Decrypt first block

  a.Close()
  return compareSlices(key, firstBlock) // Compare decrypted first block with the key.
}

func strToInt(str string) (int, error) {    // Used for converting string to integer, as go doesn't have that built in for some reason
    n := strings.Split(str, ".")    // Splits by decimal point
    return strconv.Atoi(n[0])       // Returns integer of whole number
}


func main() {
  bytes, err := ioutil.ReadAll(os.Stdin)
  check(err)
  fields := strings.Split(string(bytes), ", ")
  keyString := strings.Split(string(fields[3]), " ")

  var key []byte
  for i := 0; i < len(keyString); i++ {
    a, err := strToInt(keyString[i])
    check(err)
    key = append(key, byte(a))
  }
  request := string(fields[0])

  if request == "y" {
    encryptFile(expandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "n" {
    decryptFile(expandKey(key), string(fields[1]), string(fields[2]))
  } else if request == "yDir" {
    encryptList(expandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "nDir" {
    decryptList(expandKey(key), strings.Split(string(fields[1]), "\n"), strings.Split(string(fields[2]), "\n"))
  } else if request == "dirList" {
    fileList, targList := getLists(expandKey(key), []string{}, []string{}, string(fields[1]), string(fields[2]))
    fmt.Print(strings.Join(fileList, ",,")+"--!--")
    fmt.Print(strings.Join(targList, ",,"))
  } else if request == "test" {
    valid := checkKey(key, string(fields[1]))
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
