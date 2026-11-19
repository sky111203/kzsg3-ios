import json
a = json.load(open(r"D:\dsh\kzsg3_port\apk_extracted\assets\res\config\shopConfig.json", encoding="utf-8"))
b = json.load(open(r"D:\dsh\kzsg3_port\apk_extracted\assets\res\config\shopConfig_bak.json", encoding="utf-8"))
def walk(o, p=""):
    if isinstance(o, dict):
        for k,v in o.items(): yield from walk(v, p+"/"+str(k))
    elif isinstance(o, list):
        for i,v in enumerate(o): yield from walk(v, f"{p}/{i}")
    else:
        yield p, o
da = dict(walk(a)); db = dict(walk(b))
keys = set(da)|set(db)
diffs = [(k, da.get(k,"<absent>"), db.get(k,"<absent>")) for k in sorted(keys) if da.get(k,"<a>") != db.get(k,"<b>")]
print("diff count:", len(diffs))
for k,x,y in diffs[:40]: print(f"  {k}: current={x}  bak={y}")
print()
print("sample shopConfig entries:")
items = a if isinstance(a, list) else a.get("item", a.get("goods", list(a.values())[0] if a else []))
print(json.dumps(a if isinstance(a,dict) and len(str(a))<800 else (items[:2] if isinstance(items,list) else list(a)[:2]), ensure_ascii=False)[:700])
