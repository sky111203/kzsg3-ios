import re
d = open(r"D:\dsh\kzsg3_port\apk_extracted\assets\main.jsc","rb").read()
# UTF-16LE ASCII strings
pat = rb"(?:[\x20-\x7e]\x00){4,}"
strs = [m.group(0).decode("utf-16le") for m in re.finditer(pat, d)]
seen = []
for s in strs:
    if s not in seen: seen.append(s)
print("utf16le strings in main.jsc:", len(seen))
for s in seen: print("  ", repr(s))
