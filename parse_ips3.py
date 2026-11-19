import json
p = r"D:\app\qq\lt\KZSG3-2026-11-18-150418.ips"
raw = open(p, encoding="utf-8", errors="replace").read()
nl = raw.index("\n")
body = json.loads(raw[nl:])
print("exception:", json.dumps(body.get("exception", {}), indent=1))
print("termination:", json.dumps(body.get("termination", {}), indent=1))
print("procStart:", body.get("procStartAbsTime"), "model:", body.get("modelCode"), "os:", body.get("osVersion", {}).get("train"))
imgs = body.get("usedImages", [])
print("images:", len(imgs))
for i, im in enumerate(imgs):
    print("  %d: %s base=%s size=%s path=%s" % (i, im.get("name"), im.get("base"), im.get("size"), str(im.get("path"))[:90]))
ft = body.get("faultingThread", 0)
th = body["threads"][ft]
print("== thread", ft, "frames:")
for fr in th.get("frames", [])[:25]:
    ii = fr.get("imageIndex")
    nm = imgs[ii].get("name") if ii is not None and ii < len(imgs) else "?"
    print("   +%s  %s" % (fr.get("imageOffset"), nm))
