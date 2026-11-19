import sys, re, os
sys.path.insert(0, r"D:\dsh\kzsg3_port\ios_port\tools")
from pbx_sources import parse_pbxproj, get_list, get_str
objs = parse_pbxproj(r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x\build\cocos2d_libs.xcodeproj\project.pbxproj")
mg = objs["1551A334158F2AB200E66CFE"]
print("mainGroup type:", mg["type"], "label:", mg["label"])
ch = get_list(mg["body"], "children")
print("children:", len(ch), ch[:5])
body_head = mg["body"][:400]
print(body_head)
