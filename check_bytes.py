p = r"D:\dsh\kzsg3_port\ios_port\Game\ios\Info.plist"
d = open(p, "rb").read()
i = d.find(b"CFBundleDisplayName")
print(d[i:i+90])
print("utf8 ok:", "狂斩三国3".encode("utf-8") in d)
