#!/bin/bash
export env GOPATH="/home/josh/nea-12ColcloughJ/code/python-go/AES/"
cd src/AES && go test -v -bench=. -benchmem
cd AESfiles && go test -v -bench=. -benchmem