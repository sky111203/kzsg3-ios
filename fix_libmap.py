p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
start = t.find("    for name in [\"libcurl_arm64.a\"")
end = t.find("    args.append(fwd(SM_ARM64))")
block = '''    libmap = {
        "libcurl_arm64.a": os.path.join(CX, "external", "curl", "prebuilt", "ios", "libcurl_arm64.a"),
        "libfreetype_arm64.a": os.path.join(CX, "external", "freetype2", "prebuilt", "ios", "libfreetype_arm64.a"),
        "libjpeg_arm64.a": os.path.join(CX, "external", "jpeg", "prebuilt", "ios", "libjpeg_arm64.a"),
        "libpng_arm64.a": os.path.join(CX, "external", "png", "prebuilt", "ios", "libpng_arm64.a"),
        "libtiff_arm64.a": os.path.join(CX, "external", "tiff", "prebuilt", "ios", "libtiff_arm64.a"),
        "libwebp_arm64.a": os.path.join(CX, "external", "webp", "prebuilt", "ios", "libwebp_arm64.a"),
        "libwebsockets_arm64.a": os.path.join(CX, "external", "websockets", "prebuilt", "ios", "libwebsockets_arm64.a"),
    }
    for k, p2 in libmap.items():
        if os.path.isfile(p2):
            args.append(fwd(p2))
'''
t = t[:start] + block + t[end:]
open(p, "w", encoding="utf-8").write(t)
print("fixed")
