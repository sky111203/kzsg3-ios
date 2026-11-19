import sys
sys.path.insert(0, r"D:\dsh\kzsg3_port\ios_port\tools")
from pbx_sources import parse_pbxproj, get_str
objs = parse_pbxproj(r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x\build\cocos2d_libs.xcodeproj\project.pbxproj")
fr = objs.get("1A01C68018F57BE800EFE3A6")
print("fileRef type:", fr["type"] if fr else "MISSING")
if fr: print("path:", get_str(fr["body"], "path"), "tree:", get_str(fr["body"], "sourceTree"))
project = next(d for d in objs.values() if d["type"] == "PBXProject")
import re
m = re.search(r'mainGroup = ([0-9A-F]{24})', project["body"])
print("mainGroup:", m.group(1) if m else "NOT FOUND")
mg = objs.get(m.group(1)) if m else None
if mg:
    print("mainGroup children sample:")
    for line in mg["body"].splitlines()[:12]: print("   ", line.strip())
print("total objs:", len(objs))
groups = sum(1 for d in objs.values() if d["type"]=="PBXGroup")
frs = sum(1 for d in objs.values() if d["type"]=="PBXFileReference")
print("groups:", groups, "fileRefs:", frs)
