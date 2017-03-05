#!/usr/bin/python
import re
import pefile
import sys

data = open(sys.argv[1],"rb").read()
for m in re.finditer(r"MZ", data):
    try:
        pe = pefile.PE(data=data[m.start():])
    except:
        continue
    ls_size = pe.sections[-1].SizeOfRawData
    ls_pos = pe.sections[-1].PointerToRawData
    open(sys.argv[1] + "_" + str(m.start()), "wb").write(data[m.start():m.start()+ls_pos+ls_size])
