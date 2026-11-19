import json
for f in ["goods.json","goodsIOS.json","shopConfigIOS.json"]:
    a = json.load(open(rf"D:\dsh\kzsg3_port\apk_extracted\assets\res\config\{f}", encoding="utf-8"))
    items = a if isinstance(a, list) else list(a.values())[0] if isinstance(a,dict) and not isinstance(list(a.values())[0], str) else a
    s = json.dumps(items if isinstance(items,list) else a, ensure_ascii=False)
    print(f"== {f}: type={type(a).__name__} len={len(s)}")
    print(s[:500].encode("gbk","replace").decode("gbk"))
    print()
