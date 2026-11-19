import tarfile, os
tf = tarfile.open(r"D:\dsh\kzsg3_port\iPhoneOS15.6.sdk.tar.xz", "r:xz")
DEST = r"D:\dsh\kzsg3_port\sdk156"
os.makedirs(DEST, exist_ok=True)
members = tf.getmembers()
# we only need usr/lib tbds + framework tbds
for m in members:
    n = m.name
    if not n.endswith(".tbd"): continue
    tf.extract(m, DEST, set_attrs=False)
print("tbd files extracted:", sum(1 for m in members if m.name.endswith(".tbd")))
