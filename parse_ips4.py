import json
p = r"D:\app\qq\lt\KZSG3-2026-11-18-161348.ips"
raw = open(p, encoding="utf-8", errors="replace").read()
nl = raw.index("\n")
body = json.loads(raw[nl:])
print("exception:", json.dumps(body.get("exception", {})))
print("termination:", json.dumps(body.get("termination", {}), indent=1))
print("model:", body.get("modelCode"), "os:", body.get("osVersion", {}).get("train"))
imgs = body.get("usedImages", [])
print("images loaded:", len(imgs))
ft = body.get("faultingThread", 0)
th = body["threads"][ft]
print("thread", ft, "frames:")
for fr in th.get("frames", [])[:30]:
    ii = fr.get("imageIndex")
    nm = imgs[ii].get("name") if ii is not None and ii < len(imgs) else "?"
    print("   +%s  %s" % (fr.get("imageOffset"), nm))
