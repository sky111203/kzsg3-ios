# -*- coding: utf-8 -*-
"""
Assemble the KZSG3 iOS Xcode project from the cocos2d-js v3.0-beta template.
- Copies template ios/mac app layer into Game/
- Copies engine tree (js-bindings) into Game/../engine
- Transforms template project.pbxproj: paths, resources, target name, KG bridge sources
- Generates template-named icons + launch images from the APK icon
Run: python assemble_project.py
"""
import os, re, shutil, subprocess
from PIL import Image, ImageDraw

# 路径全部相对本脚本位置, 供本机与 CI 共用
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # ios_port/
GAME = os.path.join(BASE, "Game")
ENGINE_DST = os.path.join(BASE, "engine", "js-bindings")
RES = os.path.join(GAME, "Resources")

# cocos2d-js 引擎解包根目录: 环境变量 COCOS2D_JS_ROOT 优先, 否则用本机默认位置
_CJS = os.environ.get("COCOS2D_JS_ROOT")
if _CJS:
    ENGINE_SRC = _CJS
else:
    ENGINE_SRC = os.path.join(os.path.dirname(BASE), "enginejs", "cocos2d-js-v3.0-beta",
                              "frameworks", "js-bindings")
TPL = os.path.join(ENGINE_SRC, "..", "..", "templates", "js-template-default",
                   "frameworks", "runtime-src")
TPL = os.path.normpath(TPL)

ICON_SRC = os.path.join(BASE, "tools", "app_icon.png")
_ICON_FALLBACK = r"D:\dsh\kzsg3_port\apk_extracted\res\drawable-hdpi-v4\icon.png"
if not os.path.exists(ICON_SRC) and os.path.exists(_ICON_FALLBACK):
    ICON_SRC = _ICON_FALLBACK

IOS_FILES = ["AppController.h", "AppController.mm", "RootViewController.h",
             "RootViewController.mm", "main.m", "Prefix.pch", "Info.plist"]

# JS file refs present in template pbxproj that our bundle replaces via folder ref
JS_REFS = ["project.json", "main.js", "jsb_boot.js", "jsb_create_apis.js",
           "jsb_ext_create_apis.js", "jsb_loaders.js", "jsb_chipmunk_constants.js",
           "jsb_chipmunk.js", "jsb_cocos2d_constants.js", "jsb_cocos2d_extension.js",
           "jsb_cocos2d_ui.js", "jsb_cocos2d_studio.js", "jsb_cocos2d.js",
           "jsb_cocosbuilder.js", "jsb_debugger.js", "jsb_deprecated.js",
           "jsb_opengl_constants.js", "jsb_opengl.js", "jsb_property_apis.js",
           "jsb_property_impls.js", "jsb.js", "debugger", "src", "res"]

def copy_app_layer():
    src_ios = os.path.join(TPL, "proj.ios_mac", "ios")
    dst_ios = os.path.join(GAME, "ios")
    os.makedirs(dst_ios, exist_ok=True)
    for f in IOS_FILES:
        shutil.copy2(os.path.join(src_ios, f), os.path.join(dst_ios, f))
    # mac target files (kept so project opens cleanly; not built in CI)
    dst_mac = os.path.join(GAME, "mac")
    os.makedirs(dst_mac, exist_ok=True)
    for f in os.listdir(os.path.join(TPL, "proj.ios_mac", "mac")):
        shutil.copy2(os.path.join(TPL, "proj.ios_mac", "mac", f), dst_mac)
    # splash screens
    img = Image.open(ICON_SRC).convert("RGB")
    navy = (16, 24, 66)
    for name, wh in [("Default.png", (320, 480)), ("Default@2x.png", (640, 960)),
                     ("Default-568h@2x.png", (640, 1136))]:
        im = Image.new("RGB", wh, navy)
        d = ImageDraw.Draw(im)
        icon = img.resize((120, 120), Image.LANCZOS)
        im.paste(icon, ((wh[0]-120)//2, (wh[1]-240)//2))
        d.text(((wh[0])/2-60, (wh[1])/2+80), "KZSG3", fill=(240, 240, 240))
        im.save(os.path.join(dst_ios, name))

def make_icons():
    img = Image.open(ICON_SRC).convert("RGBA")
    names = {"Icon.png": 57, "Icon@2x.png": 114, "Icon-57.png": 57, "Icon-114.png": 114,
             "Icon-72.png": 72, "Icon-144.png": 144, "Icon-76.png": 76, "Icon-152.png": 152,
             "Icon-29.png": 29, "Icon-58.png": 58, "Icon-40.png": 40, "Icon-80.png": 80,
             "Icon-50.png": 50, "Icon-100.png": 100}
    out = os.path.join(GAME, "ios")
    for n, px in names.items():
        img.resize((px, px), Image.LANCZOS).save(os.path.join(out, n))
    img.resize((1024, 1024), Image.LANCZOS).save(os.path.join(BASE, "AppIcon-1024.png"))

def copy_engine():
    if os.path.isdir(ENGINE_DST):
        shutil.rmtree(ENGINE_DST)
    os.makedirs(os.path.dirname(ENGINE_DST), exist_ok=True)
    shutil.copytree(ENGINE_SRC, ENGINE_DST,
                    ignore=shutil.ignore_patterns("proj.win32", "proj.win8.1-universal",
                                                  "proj.android", "*.vcxproj*"))

def gen_pbxproj():
    src = os.path.join(TPL, "proj.ios_mac", "HelloJavascript.xcodeproj", "project.pbxproj")
    t = open(src, encoding="utf-8").read()

    # 1) engine path prefix (all occurrences: file refs and header search paths)
    t = t.replace('"../../js-bindings/', '"../engine/js-bindings/')
    t = t.replace("../../js-bindings/", "../engine/js-bindings/")
    # 2) product/target names
    t = t.replace("HelloJavascript", "KZSG3")

    # 3) drop individual JS file references (fileRef decls)
    for name in JS_REFS:
        t = re.sub(r'^\t\t[0-9A-F]{24} /\* %s \*/ = \{isa = PBXFileReference;.*\n' % re.escape(name),
                   '', t, flags=re.M)
    # 4) drop their build-file decls
    for name in JS_REFS:
        t = re.sub(r'^\t\t[0-9A-F]{24} /\* %s in Resources \*/ = \{isa = PBXBuildFile;.*\n' % re.escape(name),
                   '', t, flags=re.M)
    # 5) drop them from Resources build phases and groups
    t = re.sub(r'^\t\t\t\t[0-9A-F]{24} /\* (?:%s) in Resources \*/,\n' % '|'.join(re.escape(n) for n in JS_REFS),
               '', t, flags=re.M)
    # group children lines (no "in Resources" suffix)
    for name in JS_REFS:
        t = re.sub(r'^\t\t\t\t[0-9A-F]{24} /\* %s \*/,\n' % re.escape(name), '', t, flags=re.M)
    # remove JS Common group children remnant + group itself
    t = re.sub(r'^\t\tC06D18B718C02D4A003D1A65 /\* JS Common \*/ = \{.*?\n\t\t\};\n', '', t, flags=re.M | re.S)
    t = re.sub(r'\n\t\t\t\tC06D18B718C02D4A003D1A65 /\* JS Common \*/,', '', t)
    # 6) inject Resources folder ref (fileRef + buildfile + phase + group)
    t = t.replace("/* Begin PBXBuildFile section */",
        "/* Begin PBXBuildFile section */\n"
        "\t\tAAAA00000000000000000001 /* Resources in Resources */ = {isa = PBXBuildFile; fileRef = AAAA00000000000000000002 /* Resources */; };")
    t = t.replace("/* Begin PBXFileReference section */",
        "/* Begin PBXFileReference section */\n"
        "\t\tAAAA00000000000000000002 /* Resources */ = {isa = PBXFileReference; lastKnownFileType = folder; path = Resources; sourceTree = \"<group>\"; };")
    # add to Resources group + both Resources phases
    t = t.replace(
        "\t\t\t\tAAAA00000000000000000002 /* Resources */,",  # guard against double-add in group children later
        "\t\t\t\tAAAA00000000000000000002 /* Resources */,")
    t = t.replace("/* Begin PBXGroup section */\n", "/* Begin PBXGroup section */\n")
    # group children for the Resources *group* (15628F5B15F0F5C2000CF24B)
    t = re.sub(r"(15628F5B15F0F5C2000CF24B /\* Resources \*/ = \{\n\s*isa = PBXGroup;\n\s*children = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000002 /* Resources */,\n", t)
    # both build phases get the file
    t = re.sub(r"(509D4A9317EBB24E00697056 /\* Resources \*/ = \{\n\s*isa = PBXResourcesBuildPhase;\n\s*buildActionMask = 2147483647;\n\s*files = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000001 /* Resources in Resources */,\n", t)
    t = re.sub(r"(A922753B1517C094001B78AA /\* Resources \*/ = \{\n\s*isa = PBXResourcesBuildPhase;\n\s*buildActionMask = 2147483647;\n\s*files = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000001 /* Resources in Resources */,\n", t)
    # 7) KGOperatorBridge into Classes group + both Sources phases
    t = t.replace(
        "D4545215156E28EF00887EB5 /* AppDelegate.cpp */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.cpp.cpp; path = AppDelegate.cpp; sourceTree = \"<group>\"; };",
        "D4545215156E28EF00887EB5 /* AppDelegate.cpp */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.cpp.cpp; path = AppDelegate.cpp; sourceTree = \"<group>\"; };\n"
        "\t\tAAAA00000000000000000003 /* KGOperatorBridge.cpp */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.cpp.cpp; name = KGOperatorBridge.cpp; path = ../Classes/KGOperatorBridge.cpp; sourceTree = \"<group>\"; };\n"
        "\t\tAAAA00000000000000000004 /* KGOperatorBridge.h */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.c.h; name = KGOperatorBridge.h; path = ../Classes/KGOperatorBridge.h; sourceTree = \"<group>\"; };")
    t = t.replace(
        "AAAA00000000000000000001 /* Resources in Resources */ = {isa = PBXBuildFile; fileRef = AAAA00000000000000000002 /* Resources */; };",
        "AAAA00000000000000000001 /* Resources in Resources */ = {isa = PBXBuildFile; fileRef = AAAA00000000000000000002 /* Resources */; };\n"
        "\t\tAAAA00000000000000000005 /* KGOperatorBridge.cpp in Sources */ = {isa = PBXBuildFile; fileRef = AAAA00000000000000000003 /* KGOperatorBridge.cpp */; };")
    t = re.sub(r"(D4545214156E28EF00887EB5 /\* Classes \*/ = \{\n\s*isa = PBXGroup;\n\s*children = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000003 /* KGOperatorBridge.cpp */,\n\t\t\t\tAAAA00000000000000000004 /* KGOperatorBridge.h */,\n", t)
    t = re.sub(r"(A92275391517C094001B78AA /\* Sources \*/ = \{\n\s*isa = PBXSourcesBuildPhase;\n\s*buildActionMask = 2147483647;\n\s*files = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000005 /* KGOperatorBridge.cpp in Sources */,\n", t)
    t = re.sub(r"(509D4A8017EBB24E00697056 /\* Sources \*/ = \{\n\s*isa = PBXSourcesBuildPhase;\n\s*buildActionMask = 2147483647;\n\s*files = \(\n)",
               r"\1\t\t\t\tAAAA00000000000000000005 /* KGOperatorBridge.cpp in Sources */,\n", t)
    # 8) modern build settings
    t = t.replace("IPHONEOS_DEPLOYMENT_TARGET = 5.1;", "IPHONEOS_DEPLOYMENT_TARGET = 12.0;")
    t = t.replace("IPHONEOS_DEPLOYMENT_TARGET = 5.0;", "IPHONEOS_DEPLOYMENT_TARGET = 12.0;")
    t = t.replace('CLANG_CXX_LANGUAGE_STANDARD = "c++0x";', 'CLANG_CXX_LANGUAGE_STANDARD = "gnu++11";')
    t = t.replace("CODE_SIGN_IDENTITY = \"iPhone Developer\";", "CODE_SIGN_IDENTITY = \"Apple Development\";")
    t = t.replace("\t\t\t\tDevelopmentTeam = MDDB52YB8L;\n", "")
    t = t.replace("LastUpgradeCheck = 0500;", "LastUpgradeCheck = 1500;")
    # arm64 only on iOS targets (append into ios Debug/Release buildSettings)
    t = re.sub(r"(A92277011517C097001B78AA /\* Debug \*/ = \{\n\s*isa = XCBuildConfiguration;\n\s*buildSettings = \{\n)",
               r"\1\t\t\t\tARCHS = arm64;\n\t\t\t\tONLY_ACTIVE_ARCH = NO;\n", t)
    t = re.sub(r"(A92277021517C097001B78AA /\* Release \*/ = \{\n\s*isa = XCBuildConfiguration;\n\s*buildSettings = \{\n)",
               r"\1\t\t\t\tARCHS = arm64;\n\t\t\t\tONLY_ACTIVE_ARCH = NO;\n\t\t\t\tENABLE_BITCODE = NO;\n", t)
    # sanity: no stale js file refs
    leftover = [n for n in JS_REFS if ("/* %s */" % n) in t]
    if leftover:
        print("WARN leftover refs:", leftover)
    outdir = os.path.join(GAME, "KZSG3.xcodeproj")
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "project.pbxproj"), "w", encoding="utf-8").write(t)
    print("pbxproj written")

def patch_infoplist():
    import plistlib
    p = os.path.join(GAME, "ios", "Info.plist")
    with open(p, "rb") as f:
        pl = plistlib.load(f)
    pl["CFBundleDisplayName"] = "狂斩三国3"
    pl["CFBundleName"] = "KZSG3"
    pl["CFBundleIdentifier"] = "com.kzsg3.sanguo3"
    pl["CFBundleVersion"] = "1.0.5"
    pl["CFBundleShortVersionString"] = "1.0.5"
    pl["UIRequiredDeviceCapabilities"] = {"opengles-2": True, "armv7": True}
    pl["NSAppTransportSecurity"] = {"NSAllowsArbitraryLoads": True}   # 老游戏内嵌 http 请求
    pl["ITSAppUsesNonExemptEncryption"] = False
    with open(p, "wb") as f:
        plistlib.dump(pl, f)

def copy_extra():
    patch_infoplist()

if __name__ == "__main__":
    os.makedirs(GAME, exist_ok=True)
    copy_app_layer()
    make_icons()
    copy_engine()
    gen_pbxproj()
    copy_extra()
    print("assembled ->", GAME)
