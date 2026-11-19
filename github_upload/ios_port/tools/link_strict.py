# -*- coding: utf-8 -*-
"""Link arm64 Mach-O (strict two-level namespace with complete 15.6 SDK tbds), package IPA."""
import os, glob, subprocess, shutil, sys

OBJ = r"D:\dsh\kzsg3_port\obj"
OUT = r"D:\dsh\kzsg3_port\out"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(BASE, "Game", "Resources")
SDK = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk"
TBD = r"D:\dsh\kzsg3_port\sdk156\iPhoneOS15.6.sdk"
CX = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x"
SM_ARM64 = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\ios\libjs_static.arm64.a"
LLD = r"C:\Program Files\LLVM\bin\ld64.lld.exe"

FRAMEWORKS = [
    "UIKit", "Foundation", "OpenGLES", "QuartzCore", "OpenAL", "AudioToolbox",
    "AVFoundation", "CoreGraphics", "CoreMotion", "MediaPlayer", "CFNetwork",
    "SystemConfiguration", "Security", "CoreText", "GameController",
]

def fwd(p): return p.replace("\\", "/")

def collect_objects():
    return sorted(glob.glob(os.path.join(OBJ, "**", "*.o"), recursive=True))

def link(objs):
    exe = os.path.join(OUT, "KZSG3")
    args = [
        "-arch", "arm64",
        "-platform_version", "ios", "12.0", "16.5",
        "-syslibroot", SDK,
        "-o", fwd(exe),
        "-ObjC",
        "-no_fixup_chains",
        "-no_function_starts",
        "-undefined", "dynamic_lookup",
        "--error-limit=0",
    ]
    # 使用 iOS 15.6 SDK 的完整 v4 tbd (包含全部 arm64 导出符号)
    for f in FRAMEWORKS:
        p = os.path.join(TBD, "System", "Library", "Frameworks", f + ".framework", f + ".tbd")
        if os.path.isfile(p):
            args.append(fwd(p))
    cf_tbd = os.path.join(TBD, "System", "Library", "Frameworks", "CoreFoundation.framework", "CoreFoundation.tbd")
    if os.path.isfile(cf_tbd):
        args.append(fwd(cf_tbd))
    fp_tbd = os.path.join(TBD, "System", "Library", "Frameworks", "FileProvider.framework", "FileProvider.tbd")
    if os.path.isfile(fp_tbd):
        args.append(fwd(fp_tbd))
    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",
              "usr/lib/libz.tbd", "usr/lib/libsqlite3.tbd",
              "usr/lib/libobjc.tbd", "usr/lib/libobjc.A.tbd"]:
        p = os.path.join(TBD, l.replace("/", os.sep))
        if os.path.isfile(p):
            args.append(fwd(p))
    # 预编译第三方库
    for name in ["libcurl_arm64.a", "libfreetype_arm64.a", "libjpeg_arm64.a",
                 "libpng_arm64.a", "libtiff_arm64.a", "libwebp_arm64.a",
                 "libwebsockets_arm64.a"]:
        libmap2 = {
            "libcurl_arm64.a": "curl", "libfreetype_arm64.a": "freetype2",
            "libjpeg_arm64.a": "jpeg", "libpng_arm64.a": "png",
            "libtiff_arm64.a": "tiff", "libwebp_arm64.a": "webp",
            "libwebsockets_arm64.a": "websockets"}
        sub = libmap2[name]
        p = os.path.join(CX, "external", sub, "prebuilt", "ios", name)
        if os.path.isfile(p):
            args.append(fwd(p))
    args.append(fwd(SM_ARM64))
    for o in objs:
        args.append(fwd(o))

    rsp = os.path.join(OUT, "link.rsp")
    os.makedirs(OUT, exist_ok=True)
    with open(rsp, "w", encoding="utf-8") as f:
        f.write("\n".join(args))
    r = subprocess.run([LLD, "@" + fwd(rsp)], capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout)
        und = [l for l in err.splitlines() if "undefined symbol" in l]
        print("undefined count:", len(und))
        for l in und[:25]:
            print("  ", l[-160:])
        other = [l for l in err.splitlines() if "error:" in l and "undefined symbol" not in l]
        for l in other[:10]:
            print("  OTHER:", l[-170:])
        with open(os.path.join(OUT, "link_err.log"), "w", encoding="utf-8") as f:
            f.write(err)
        return False
    print("exe:", exe, os.path.getsize(exe))
    return True

def package():
    app = os.path.join(OUT, "Payload", "KZSG3.app")
    if os.path.isdir(os.path.join(OUT, "Payload")):
        shutil.rmtree(os.path.join(OUT, "Payload"))
    os.makedirs(app, exist_ok=True)
    shutil.copyfile(os.path.join(OUT, "KZSG3"), os.path.join(app, "KZSG3"))
    import plistlib
    pl = {
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleDisplayName": "狂斩三国3",
        "CFBundleExecutable": "KZSG3",
        "CFBundleIcons": {"CFBundlePrimaryIcon": {"CFBundleIconFiles": [
            "Icon-29", "Icon-40", "Icon-58", "Icon-80", "Icon-120", "Icon-57", "Icon-114", "Icon-72", "Icon-144"]}},
        "CFBundleIcons~ipad": {"CFBundlePrimaryIcon": {"CFBundleIconFiles": [
            "Icon-29", "Icon-40", "Icon-58", "Icon-80", "Icon-120", "Icon-72", "Icon-76", "Icon-152", "Icon-144"]}},
        "CFBundleIdentifier": "com.kzsg3.sanguo3",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "KZSG3",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0.5",
        "CFBundleVersion": "1.0.5",
        "LSRequiresIPhoneOS": True,
        "NSAppTransportSecurity": {"NSAllowsArbitraryLoads": True},
        "UIRequiredDeviceCapabilities": {"opengles-2": True, "arm64": True},
        "UIStatusBarHidden": True,
        "UISupportedInterfaceOrientations": ["UIInterfaceOrientationLandscapeRight", "UIInterfaceOrientationLandscapeLeft"],
        "ITSAppUsesNonExemptEncryption": False,
        "MinimumOSVersion": "12.0",
        "UIFileSharingEnabled": True,
        "LSSupportsOpeningDocumentsInPlace": True,
    }
    with open(os.path.join(app, "Info.plist"), "wb") as f:
        plistlib.dump(pl, f)
    with open(os.path.join(app, "PkgInfo"), "w") as f:
        f.write("APPL????")
    icons_dir = os.path.join(BASE, "Game", "ios")
    for f in os.listdir(icons_dir):
        if f.startswith("Icon-") and f.endswith(".png"):
            shutil.copy2(os.path.join(icons_dir, f), os.path.join(app, f))
    for entry in os.listdir(RES):
        s = os.path.join(RES, entry)
        d = os.path.join(app, entry)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    ipa = os.path.join(OUT, "KZSG3-ios-arm64-unsigned.ipa")
    if os.path.exists(ipa):
        os.remove(ipa)
    pw = os.path.dirname(app)
    code = (
        "import zipfile, os\n"
        "base=r'%s'\nzf=zipfile.ZipFile(r'%s','w',zipfile.ZIP_DEFLATED,compresslevel=6)\nn=0\n"
        "for dp,dn,fn in os.walk(base):\n    for f in fn:\n"
        "        p=os.path.join(dp,f); rel=os.path.relpath(p, os.path.dirname(base)); zf.write(p, rel); n+=1\n"
        "zf.close(); print('ipa files:', n)\n" % (pw, ipa))
    r = subprocess.run(["python", "-c", code], capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip()[:200])
    print("IPA:", ipa, os.path.getsize(ipa) if os.path.exists(ipa) else "MISSING")

if __name__ == "__main__":
    objs = collect_objects()
    print("objects:", len(objs))
    if link(objs):
        package()
    else:
        sys.exit(1)
