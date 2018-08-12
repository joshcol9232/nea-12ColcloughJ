from subprocess import Popen, PIPE

geg = "/run/media/josh/Storage/nea-12ColcloughJ-master/code/python-go/AES"

goproc = Popen(geg, stdin=PIPE, stdout=PIPE)
key = SHA.getSHAkey()
out, err = goproc.communicate(inp.encode("test, "+d+", 0"), key)
