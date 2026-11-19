import json, os, hashlib, sys
OBJ = r"D:\dsh\kzsg3_port\obj"
spec = json.load(open(r"D:\dsh\kzsg3_port\crossbuild_spec.json", encoding="utf-8"))
APP_CLASSES = r"D:\dsh\kzsg3_port\ios_port\Game\Classes"
APP_IOS = r"D:\dsh\kzsg3_port\ios_port\Game\ios"
def obj_for(target, src):
    h = hashlib.md5(src.encode()).hexdigest()[:8]
    base = os.path.splitext(os.path.basename(src))[0]
    tdir = target.replace(" ", "_").replace("/", "_")
    return os.path.join(OBJ, tdir, base + "_" + h + ".o")
missing = []
tasks = []
for t, d in spec["targets"].items():
    for s in d["sources"]:
        tasks.append((t, s))
for s in ["AppDelegate.cpp", "KGOperatorBridge.cpp"]:
    tasks.append(("app", os.path.join(APP_CLASSES, s)))
for s in ["AppController.mm", "RootViewController.mm", "main.m"]:
    tasks.append(("app", os.path.join(APP_IOS, s)))
for t, s in tasks:
    o = obj_for(t, s)
    if not os.path.exists(o):
        missing.append((t, s))
print("tasks:", len(tasks), "missing .o:", len(missing))
from collections import Counter
c = Counter(t for t, s in missing)
print(dict(c))
for t, s in missing[:20]:
    print("  ", t, "|", os.path.basename(s))
