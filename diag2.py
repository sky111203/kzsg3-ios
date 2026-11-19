import sys, re
sys.path.insert(0, r"D:\dsh\kzsg3_port\ios_port\tools")
import importlib, pbx_sources
importlib.reload(pbx_sources)
from pbx_sources import parse_pbxproj, get_list, get_str
objs = parse_pbxproj(r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x\build\cocos2d_libs.xcodeproj\project.pbxproj")
target_oid = "1A01C68018F57BE800EFE3A6"
# find groups containing this oid
for oid, d in objs.items():
    if d["type"] == "PBXGroup":
        for c in get_list(d["body"], "children"):
            if c == target_oid:
                print("parent group:", oid, "label:", d["label"], "path:", get_str(d["body"], "path"))
                fr = objs[target_oid]
                print("fileRef label:", fr["label"], "path:", get_str(fr["body"], "path"), "tree:", get_str(fr["body"], "sourceTree"))
# check tree coverage
project = next(d for d in objs.values() if d["type"] == "PBXProject")
m = re.search(r'mainGroup = ([0-9A-F]{24})', project["body"])
from pbx_sources import resolve_tree
tree = resolve_tree(objs, m.group(1))
print("tree size:", len(tree))
