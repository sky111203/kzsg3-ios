# -*- coding: utf-8 -*-
"""Cross-compile the whole engine + app for arm64 iOS on Windows, then link & package IPA."""
import os, sys, json, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))            # ios_port/
CX = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x"
ENGINE = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings"
SDK = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk"
CLANG = r"C:\Program Files\LLVM\bin\clang++.exe"
OBJ = r"D:\dsh\kzsg3_port\obj"
OUTDIR = r"D:\dsh\kzsg3_port\out"
RES = os.path.join(BASE, "Game", "Resources")
APP_CLASSES = os.path.join(BASE, "Game", "Classes")
APP_IOS = os.path.join(BASE, "Game", "ios")

WORKERS = 14

BASE_FLAGS = [
    "-target", "arm64-apple-ios12.0.0",
    "-isysroot", SDK,
    "-miphoneos-version-min=12.0",
    "-stdlib=libc++",
    "-std=gnu++11",
    "-fexceptions",
    "-fno-objc-arc",
    "-Wno-deprecated-declarations",
    "-Wno-ignored-qualifiers",
    "-Wno-unused-function",
    "-Wno-unused-variable",
    "-Wno-unused-but-set-variable",
    "-Wno-switch",
    "-Wno-parentheses-equality",
    "-Wno-tautological-compare",
    "-Wno-constant-logical-operand",
    "-Wno-unknown-warning-option",
    "-O1",
    "-g",
]
DEFINES = [
    "-DNDEBUG", "-DUSE_FILE32API", "-DCOCOS2D_JAVASCRIPT",
    "-DCC_TARGET_OS_IPHONE", "-DCC_ENABLE_CHIPMUNK_INTEGRATION",
]
INCLUDES = [
    "-I" + ENGINE + "/cocos2d-x",
    "-I" + ENGINE + "/cocos2d-x/cocos",
    "-I" + ENGINE + "/cocos2d-x/cocos/base",
    "-I" + ENGINE + "/cocos2d-x/cocos/math",
    "-I" + ENGINE + "/cocos2d-x/cocos/math/kazmath",
    "-I" + ENGINE + "/cocos2d-x/cocos/2d",
    "-I" + ENGINE + "/cocos2d-x/cocos/ui",
    "-I" + ENGINE + "/cocos2d-x/cocos/network",
    "-I" + ENGINE + "/cocos2d-x/cocos/audio/include",
    "-I" + ENGINE + "/cocos2d-x/cocos/editor-support",
    "-I" + ENGINE + "/cocos2d-x/cocos/editor-support/cocostudio",
    "-I" + ENGINE + "/cocos2d-x/cocos/editor-support/cocostudio/WidgetReader",
    "-I" + ENGINE + "/cocos2d-x/cocos/editor-support/cocosbuilder",
    "-I" + ENGINE + "/cocos2d-x/cocos/editor-support/spine",
    "-I" + ENGINE + "/cocos2d-x/cocos/platform",
    "-I" + ENGINE + "/cocos2d-x/cocos/platform/ios",
    "-I" + ENGINE + "/cocos2d-x/cocos/deprecated",
    "-I" + ENGINE + "/cocos2d-x/cocos/storage",
    "-I" + ENGINE + "/cocos2d-x/cocos/storage/local-storage",
    "-I" + ENGINE + "/cocos2d-x/extensions",
    "-I" + ENGINE + "/cocos2d-x/external",
    "-I" + ENGINE + "/cocos2d-x/external/chipmunk/include/chipmunk",
    "-I" + ENGINE + "/cocos2d-x/external/curl/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/websockets/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/tinyxml2",
    "-I" + ENGINE + "/cocos2d-x/external/jpeg/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/webp/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/png/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/freetype2/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/tiff/include/ios",
    "-I" + ENGINE + "/cocos2d-x/external/edtaa3func",
    "-I" + ENGINE + "/cocos2d-x/external/unzip",
    "-I" + ENGINE + "/cocos2d-x/external/xxhash",
    "-I" + ENGINE + "/cocos2d-x/external/ConvertUTF",
    "-I" + ENGINE + "/cocos2d-x/plugin/protocols/include",
    "-I" + ENGINE + "/cocos2d-x/plugin/jsbindings/manual",
    "-I" + ENGINE + "/cocos2d-x/plugin/jsbindings/auto",
    "-I" + APP_CLASSES,
    "-I" + APP_IOS,
    "-I" + ENGINE + "/bindings/auto",
    "-I" + ENGINE + "/bindings/manual",
    "-I" + ENGINE + "/external/spidermonkey/include/ios",
]

def fwd(p): return p.replace("\\", "/")

def obj_for(target, src):
    h = hashlib.md5(src.encode()).hexdigest()[:8]
    base = os.path.splitext(os.path.basename(src))[0]
    tdir = target.replace(" ", "_").replace("/", "_")
    return os.path.join(OBJ, tdir, base + "_" + h + ".o")

def compile_one(target, src, extra_defines):
    out = obj_for(target, src)
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src):
        return None
    os.makedirs(os.path.dirname(out), exist_ok=True)
    flags = BASE_FLAGS
    lang = []
    pch = os.path.join(APP_IOS, "Prefix.pch")
    if src.endswith(".mm"):
        lang = ["-x", "objective-c++", "-include", fwd(pch)]
    elif src.endswith(".m"):
        flags = [f for f in flags if f != "-std=gnu++11"]
        lang = ["-x", "objective-c", "-include", fwd(pch)]
    elif src.endswith(".c"):
        lang = ["-x", "c", "-std=gnu99"]
        flags = [f if f != "-std=gnu++11" else "-std=gnu99" for f in BASE_FLAGS]
    rsp = out + ".rsp"
    args = flags + lang + DEFINES + extra_defines + INCLUDES + ["-c", fwd(src), "-o", fwd(out)]
    with open(rsp, "w", encoding="utf-8") as f:
        f.write("\n".join(fwd(a) for a in args))
    r = subprocess.run([CLANG, "@" + fwd(rsp)], capture_output=True, text=True)
    if r.returncode != 0:
        return (src, r.stderr[-3000:], r.stdout[-500:])
    os.remove(rsp)
    return None

def main():
    spec = json.load(open(r"D:\dsh\kzsg3_port\crossbuild_spec.json", encoding="utf-8"))
    tasks = []
    target_defines = {
        "cocos2dx iOS": [],
        "cocos2dx-extensions iOS": [],
        "chipmunk iOS": [],
        "CocosDenshion iOS": [],
        "jsbindings iOS": [],
    }
    for tname, d in spec["targets"].items():
        for s in d["sources"]:
            # plugin-x 桥是死代码: 游戏渠道调用走 KGOperatorBridge, 且其 C++ 核心未被编译
            if "plugin/jsbindings" in s.replace("\\", "/"):
                continue
            tasks.append((tname, s))
    # app sources
    app_sources = [
        os.path.join(APP_CLASSES, "AppDelegate.cpp"),
        os.path.join(APP_CLASSES, "KGOperatorBridge.cpp"),
        os.path.join(APP_CLASSES, "kzsg3_jsstub.cpp"),
        os.path.join(APP_CLASSES, "JSErrorHUD.cpp"),
        os.path.join(APP_IOS, "KZCrashHandler.mm"),
        os.path.join(APP_IOS, "AppController.mm"),
        os.path.join(APP_IOS, "RootViewController.mm"),
        os.path.join(APP_IOS, "main.m"),
    ]
    for s in app_sources: tasks.append(("app", s))

    print("total compile units:", len(tasks))
    errors = []
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {}
        for t, s in tasks:
            futs[ex.submit(compile_one, t, s, target_defines.get(t, []))] = (t, s)
        for f in as_completed(futs):
            done += 1
            r = f.result()
            if r:
                errors.append(r)
                if len(errors) <= 8:
                    t, s = futs[f]
                    print(f"[{done}/{len(tasks)}] FAIL {os.path.basename(s)} ({t})")
            if done % 50 == 0:
                print(f"  progress {done}/{len(tasks)} errors={len(errors)}")
    print("compile done. errors:", len(errors))
    # dump first errors in detail
    for i, (src, err, out) in enumerate(errors[:6]):
        print("=" * 20, "ERROR", i + 1, os.path.basename(src))
        print(err[:2200])
    with open(r"D:\dsh\kzsg3_port\compile_errors.log", "w", encoding="utf-8") as f:
        for src, err, out in errors:
            f.write("==== " + src + "\n" + err + "\n")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
