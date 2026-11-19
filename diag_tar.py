import tarfile
tf = tarfile.open(r"D:\dsh\kzsg3_port\iPhoneOS16.5.sdk.tar.xz", "r:xz")
hits = [m.name for m in tf.getmembers() if ("pthread.h" in m.name or "stdlib.h" in m.name or "UIKit.h" in m.name or m.name.endswith("libobjc.tbd") or m.name.endswith("libc++.tbd"))]
for h in hits[:20]:
    mm = tf.getmember(h)
    print(mm.name, "| type:", "dir" if mm.isdir() else "file" if mm.isfile() else ("sym" if mm.issym() else ("hard" if mm.islnk() else "?")), "| link:", mm.linkname)
print("total probed:", len(hits))
