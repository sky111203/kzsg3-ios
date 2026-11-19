# -*- coding: utf-8 -*-
"""创建 GitHub 上传包（拖拽到 github.com 即可）"""
import zipfile, os, shutil

SRC = r"D:\dsh\kzsg3_port"
DST = r"D:\dsh\kzsg3_port\github_upload.zip"

# 需要的文件列表（相对 ios_port/ 的路径）
INCLUDE_DIRS = [
    "Game/Classes",
    "Game/ios",
    "Game/mac",
    "Game/KZSG3.xcodeproj",
    "Game/Resources",
    "tools",
    "build",
]
INCLUDE_FILES = ["README_构建与安装.md"]
EXCLUDE_EXT = {".ipa", ".log", ".o", ".rsp"}

# .gitignore
GITIGNORE = """ios_port/engine/
ios_port/Game/bld/
ios_port/Game/Payload/
ios_port/Game/*.ipa
ios_port/Game/KZSG3.xcodeproj/project.xcworkspace/
*.log
"""

if os.path.exists(DST):
    os.remove(DST)

zf = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED, compresslevel=6)
n = 0

# .gitignore
zf.writestr(".gitignore", GITIGNORE)

# workflow 必须在 .github/workflows/
wf_path = os.path.join(SRC, "ios_port", "build", "build_ipa.yml")
zf.write(wf_path, ".github/workflows/build_ipa.yml")
n += 1

# ios_port 文件
for d in INCLUDE_DIRS:
    dp = os.path.join(SRC, "ios_port", d.replace("/", os.sep))
    if not os.path.isdir(dp):
        continue
    for dp2, dn, fn in os.walk(dp):
        for f in fn:
            if os.path.splitext(f)[1] in EXCLUDE_EXT:
                continue
            fp = os.path.join(dp2, f)
            rel = os.path.relpath(fp, SRC)
            zf.write(fp, rel)
            n += 1

# README
readme = os.path.join(SRC, "ios_port", "README_构建与安装.md")
if os.path.isfile(readme):
    zf.write(readme, "ios_port/README_构建与安装.md")
    n += 1

zf.close()
size = os.path.getsize(DST)
print(f"upload package: {DST}")
print(f"files: {n}, size: {size/1048576:.1f} MB")
