import json
p = r"D:\app\qq\lt\KZSG3-2026-11-18-143905.ips"
raw = open(p, encoding="utf-8", errors="replace").read()
nl = raw.index("\n")
body = json.loads(raw[nl:])
print("exception:", json.dumps(body.get("exception", {}), indent=1))
print("termination:", json.dumps(body.get("termination", {}), indent=1))
print("osVersion:", body.get("osVersion", {}).get("train"), body.get("modelCode"))
imgs = body.get("usedImages", [])
for i, im in enumerate(imgs):
    print("  img %d: %s base=%s size=%s" % (i, im.get("name"), im.get("base"), im.get("size")))
ft = body.get("faultingThread", 0)
th = body["threads"][ft]
print("== thread", ft, "crashed frames:")
for fr in th.get("frames", [])[:20]:
    ii = fr.get("imageIndex")
    nm = imgs[ii].get("name") if ii is not None and ii < len(imgs) else "?"
    print("   +%s  %s" % (fr.get("imageOffset"), nm))
print("== lastExceptionBacktrace:")
for fr in body.get("lastExceptionBacktrace", [])[:20]:
    ii = fr.get("imageIndex")
    nm = imgs[ii].get("name") if ii is not None and ii < len(imgs) else "?"
    print("   +%s  %s" % (fr.get("imageOffset"), nm))
