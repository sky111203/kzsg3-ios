# -*- coding: utf-8 -*-
"""Link arm64 Mach-O with -flat_namespace + -undefined suppress, package IPA."""
import os, glob, subprocess, shutil, sys, re

OBJ = r"D:\dsh\kzsg3_port\obj"
OUT = r"D:\dsh\kzsg3_port\out"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(BASE, "Game", "Resources")
SDK = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk"
CX = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\cocos2d-x"
SM_ARM64 = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\ios\libjs_static.arm64.a"
LLD = r"C:\Program Files\LLVM\bin\ld64.lld.exe"

FRAMEWORKS = [
    "UIKit", "Foundation", "OpenGLES", "QuartzCore", "OpenAL", "AudioToolbox",
    "AVFoundation", "CoreGraphics", "CoreMotion", "MediaPlayer", "CFNetwork",
    "SystemConfiguration",
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
        "-flat_namespace",
        "-undefined", "suppress",
        "-no_fixup_chains",
        "-no_function_starts",
        "--error-limit=0",
    ]
    for f in FRAMEWORKS:
        fw_tbd = os.path.join(SDK, "System", "Library", "Frameworks", f + ".framework", f + ".tbd")
        if os.path.isfile(fw_tbd):
            args.append(fwd(fw_tbd))
    libmap = {
        "libcurl_arm64.a": os.path.join(CX, "external", "curl", "prebuilt", "ios", "libcurl_arm64.a"),
        "libfreetype_arm64.a": os.path.join(CX, "external", "freetype2", "prebuilt", "ios", "libfreetype_arm64.a"),
        "libjpeg_arm64.a": os.path.join(CX, "external", "jpeg", "prebuilt", "ios", "libjpeg_arm64.a"),
        "libpng_arm64.a": os.path.join(CX, "external", "png", "prebuilt", "ios", "libpng_arm64.a"),
        "libtiff_arm64.a": os.path.join(CX, "external", "tiff", "prebuilt", "ios", "libtiff_arm64.a"),
        "libwebp_arm64.a": os.path.join(CX, "external", "webp", "prebuilt", "ios", "libwebp_arm64.a"),
        "libwebsockets_arm64.a": os.path.join(CX, "external", "websockets", "prebuilt", "ios", "libwebsockets_arm64.a"),
    }
    for k, p in libmap.items():
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
        for l in [l for l in err.splitlines() if "error:" in l][:10]:
            print("  LINK ERR:", l[-170:])
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
