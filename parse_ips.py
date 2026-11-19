import json
p = r"D:\WeChat\decuments\xwechat_files\wxid_w02eqbj914b622_662c\msg\file\2026-11\KZSG3-2026-11-18-133847.ips"
raw = open(p, encoding="utf-8", errors="replace").read()
# first line = metadata json; rest = crash report json
nl = raw.index("\n")
body = json.loads(raw[nl:])
print("exception:", json.dumps(body.get("exception", {}), indent=1))
print("termination:", json.dumps(body.get("termination", {}), indent=1))
print("faultingThread:", body.get("faultingThread"))
# images table
imgs = body.get("usedImages", [])
print("images:")
for i, im in enumerate(imgs):
    print("  %d: %s base=%s size=%s arch=%s" % (i, im.get("name"), im.get("base"), im.get("size"), im.get("arch")))
# faulting thread frames
ft = body.get("faultingThread", 0)
th = body["threads"][ft]
print("== thread", ft, "frames:")
for fr in th.get("frames", []):
    img = imgs[fr.get("imageIndex", 0)] if fr.get("imageIndex") is not None and fr.get("imageIndex") < len(imgs) else {}
    print("   %+s %s + %s" % (fr.get("imageOffset"), img.get("name"), fr.get("imageOffset")))
