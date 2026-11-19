import sys, re, os
sys.path.insert(0, r"D:\dsh\kzsg3_port\ios_port\tools")
from pbx_sources import parse_pbxproj, resolve_tree
objs = parse_pbxproj(r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x\build\cocos2d_libs.xcodeproj\project.pbxproj")
project = next(d for d in objs.values() if d["type"] == "PBXProject")
m = re.search(r'mainGroup = ([0-9A-F]{24})', project["body"])
tree = resolve_tree(objs, m.group(1))
print("tree size:", len(tree))
t = tree.get("1A01C68018F57BE800EFE3A6")
print("sample CCSet.cpp:", t)
