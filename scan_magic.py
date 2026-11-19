data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
for off in [5308196, 5308400, 5308952, 5309184]:
    print("=== offset", hex(off))
    chunk = data[off-64:off+96]
    # print hex + ascii
    for row in range(0, len(chunk), 16):
        line = chunk[row:row+16]
        hexs = " ".join(f"{b:02X}" for b in line)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in line)
        print(f"{off-64+row:08X}  {hexs}  {asc}")
