#!/bin/bash
export GOPATH="/home/josh/nea-12ColcloughJ/code/python-go/BLAKE/"
cd src/BLAKE && go test -v -bench=. -benchmem
