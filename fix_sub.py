# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_strict.py"
t = open(p, encoding="utf-8").read()
old = '''        sub = {"curl": "curl", "freetype2": "freetype2", "jpeg": "jpeg",
               "png": "png", "tiff": "tiff", "webp": "webp",
               "websockets": "websockets"}[name.replace("_arm64.a", "").replace("lib", "", 1)]'''
new = '''        libmap2 = {
            "libcurl_arm64.a": "curl", "libfreetype_arm64.a": "freetype2",
            "libjpeg_arm64.a": "jpeg", "libpng_arm64.a": "png",
            "libtiff_arm64.a": "tiff", "libwebp_arm64.a": "webp",
            "libwebsockets_arm64.a": "websockets"}
        sub = libmap2[name]'''
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("fixed")
