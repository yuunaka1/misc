

FLAG_Copied = 0x80
FLAG_Compress = 0x40

def get_match(src, X, src_len, hash, size, pos):
    hash_val = (40543*((((ord(src[X]) << 4) ^ ord(src[X+1])) << 4) ^ ord(src[X+2])) >> 4) & 0xfff
    pos = hash[hash_val]
    hash[hash_val] = X
    #print(repr(hash))
    if ((pos != -1) and ((X - pos) < 4096)):
        size = 0
        while 1:
            if ((size < 18) and ((X+size) < src_len) and (src[X+size] == src[pos+size])):
                size += 1
                #print("X: %d, size: %d, pos: %d" % (X, size, pos))
            else:
                break
        return((size >= 3, size, pos))
    return((False, size, pos))

def compression(src, dest, src_len):
    bit = 0
    key = 0
    size = 0
    pos = 0
    command = 0
    X = 0
    Y = 3
    Z = 1
    hash = range(4096)
    for i in range(4096):
        hash[i] = -1
    dest[0] = chr(FLAG_Compress)
    while (X < src_len) and (Y <= src_len):
        #print("X: %d Y: %d" % (X,Y))
        if bit > 15:
            dest[Z] = chr((command >> 8) & 0x00ff)
            Z+=1
            dest[Z] = chr(command & 0x00ff)
            Z = Y
            bit = 0
            Y += 2
        size = 1
        while (src[X] == src[X+size]) and (size < 0x0fff) and (X+size < src_len):
            size+=1
        if size >= 16:
            dest[Y] = chr(0)
            Y+=1
            dest[Y] = chr(((size - 16) >> 8) & 0x00ff)
            Y+=1
            dest[Y] = chr((size -16) & 0x00ff)
            Y+=1
            dest[Y] = src[X]
            Y+=1
            X+=size
            command = (command << 1) + 1
        (match, size, pos) = get_match(src, X, src_len, hash, size, pos)
        if match: 
            key = ((X-pos) << 4) + (size - 3)
            dest[Y] = chr((key >> 8) & 0x00ff)
            Y+=1
            dest[Y] = chr(key & 0x00ff)
            Y+=1
            X+=size
            command = (command << 1) + 1
        else:
            dest[Y] = src[X]
            Y+=1
            X+=1
            command = (command << 1)
        bit+=1
    command <<= (16-bit)
    dest[Z] = chr((command >> 8) & 0x00ff)
    Z+=1
    dest[Z] = chr(command & 0x00ff)
    if (Y > src_len):
        for Y in range(src_len):
            dest[Y+1] = src[Y]
            Y+=1
        dest[0] = chr(FLAG_Copied)
        return(src_len+1)
    return(Y)
    
def decompression(src, dest, src_len):
    X = 3
    Y = 0
    pos = 0
    size = 0
    command = (ord(src[1]) << 8) + ord(src[2])
    bit = 16
    if ord(src[0]) == FLAG_Copied:
        dest = src[1:]
        return(len(src) - 1)
    while (X < src_len):
        if bit == 0:
            command = (ord(src[X]) << 8)
            X+=1
            command += ord(src[X])
            X+=1
            bit = 16
        if (command & 0x8000):
            pos = ord(src[X]) << 4
            X+=1
            pos += ord(src[X]) >> 4
            if pos:
                size = (ord(src[X]) & 0x0f) + 3
                X+=1
                for K in range(size):
                    #print("Y:%d K:%d pos:%d" % (Y, K, pos))
                    dest[Y+K] = dest[Y-pos+K]
                Y+=size
            else:
                size = ord(src[X]) << 8
                X+=1
                size += ord(src[X]) + 16
                X+=1
                for K in range(size):
                    dest[Y+K] = src[X]
                X+=1
                Y+=size
        else:
            dest[Y] = src[X]
            Y+=1
            X+=1
        command <<= 1
        bit-=1 
    return Y

data = "hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world"
compressed = range(1000) 
print(len(data))
compressed_len = compression(data, compressed, len(data))
decompressed = range(1000)
decompressed_len = decompression("".join(compressed[:compressed_len]), decompressed, compressed_len)
print(repr("".join(decompressed[:decompressed_len])))
