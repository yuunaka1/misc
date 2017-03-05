#!/usr/bin/python
import sys
import pefile
from Crypto.Cipher import ARC4

def get_resource(pe):
    if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
	for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
	    if resource_type.name is not None:
		name = "%s" % resource_type.name
	    else:
		name = "%s" % pefile.RESOURCE_TYPE.get(resource_type.struct.Id)
	    if name == None:
		name = "%d" % resource_type.struct.Id
            print(name)
            if name == "RT_RCDATA":
		data = pe.get_data(resource_type.directory.entries[0].directory.entries[0].data.struct.OffsetToData, resource_type.directory.entries[0].directory.entries[0].data.struct.Size)
                return data

pe = pefile.PE(sys.argv[1])            
data = get_resource(pe)
key_len = ord(data[0])
key = data[1:1+key_len]
rc4 = ARC4.new(key)
dec = rc4.decrypt(data[1+key_len:])
dec_list = dec.split("@@")
for i in range(len(dec_list)):
    print("%d: %s" % (i, repr(dec_list[i])))
