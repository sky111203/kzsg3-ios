import re
# patch audit: only count n_value==0 as undefined
p = r"D:\dsh\kzsg3_port\audit_ios15.py"
t = open(p, encoding="utf-8").read()
t = t.replace("""    n_strx, n_type = struct.unpack_from("<IB", d, o)
    if (n_type & 0x0E) == 0:
        e = STR.index(b"\\x00", n_strx)""", """    n_strx, n_type, n_sect, n_desc, n_value = struct.unpack_from("<IBBII", d, o)
    if (n_type & 0x0E) == 0 and n_value == 0 and n_sect == 0:
        e = STR.index(b"\\x00", n_strx)""")
open(p, "w", encoding="utf-8").write(t)
print("patched")
