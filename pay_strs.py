import re, struct
# While the download runs: analyze Pay flow. Extract all utf16+ascii strings from Pay-related jsc
import os
files = [
 r"src\Pay.jsc",
 r"src\ChannelExport.jsc",
 r"src\ios\define\Pay_Define.jsc",
 r"src\android\define\Pay_Define.jsc",
 r"src\kuaiyong\define\Pay_Define.jsc",
 r"src\KTPLAY.jsc",
]
root = r"D:\dsh\kzsg3_port\apk_extracted\assets"
for f in files:
    p = os.path.join(root, f)
    if not os.path.exists(p):
        print("MISSING:", f); continue
    d = open(p,"rb").read()
    a = [m.group(0).decode() for m in re.finditer(rb"[\x20-\x7e]{5,}", d)]
    w = [m.group(0).decode("utf-16le") for m in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", d)]
    seen = []
    for s in a+w:
        if s not in seen: seen.append(s)
    print("="*15, f, len(d))
    for s in seen[:45]: print("   ", repr(s))
    print()
