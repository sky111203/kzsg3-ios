# -*- coding: utf-8 -*-
import subprocess, os
os.chdir(r"D:\dsh\kzsg3_port")
git = r"C:\Program Files\Git\bin\git.exe"

# 移除所有大文件/无关文件
remove_patterns = [
    "*.zip", "*.ipa", "*.xz", "*.tar.gz",
    "KZSG3-iOS-移植包.zip", "github_upload.zip",
    "KZSG3-ios-arm64-trollstore.ipa", "KZSG3-ios-arm64-unsigned.ipa",
    "cocos2d-js-v3.0-beta.zip", "cocos2d-js-v3.0.zip", "cocos2d-js-v3.1.zip",
    "cocos2d-x-3.0-full.zip", "cocos2d-x-3.1.zip", "cocos2d-x-3.2.zip",
    "cocos2d-x-3.0.tar.gz", "iPhoneOS16.5.sdk.tar.xz", "iPhoneOS15.6.sdk.tar.xz",
    "py32.zip", "ldid.exe",
    "out/", "sdk/", "sdk156/", "enginejs/", "engine31/", "engine32/",
    "obj/", "link_out.txt", "strict_out.txt", "flat_link.txt",
    "compile_errors.log", "build.log",
    "dis_*.txt", "dis_*.py", "check_*.py", "diag_*.py", "scan_*.py",
    "parse_*.py", "audit_*.py", "verify_*.py", "entropy.py",
    "find_*.py", "dump_*.py", "probe_*.py", "sections.py",
    "axml*.py", "rel_*.py", "sym_*.py", "pe_*.py", "pe_*.txt",
    "disasm*.py", "disasm*.txt", "dis_*.py", "dis_*.txt",
    "decompile_jsc.py", "extract_sdk.py", "extract_sdk156.py",
    "jsc_headers.py", "jsc_strings.py", "main_strs.py",
    "pay_strs.py", "custom_natives.py", "goods_cmp.py",
    "make_icons.py", "mk120.py", "diff_shop.py", "check_tm.py",
    "check_lc*.py", "check_macho.py", "check_ipa.py", "check_undef*.py",
    "parse_*.py", "probe_*.py", "fix_*.py", "patch_*.py",
    "link_out.txt", "strict_out.txt", "flat_link.txt",
    "smoke.rsp", "smoke_test*",
]
# 更新 .gitignore
gi_path = ".gitignore"
gi = open(gi_path, encoding="utf-8").read() if os.path.isfile(gi_path) else ""
gi += """
*.zip
*.ipa
*.xz
*.tar.gz
*.exe
*.o
*.rsp
*.log
out/
sdk/
sdk156/
enginejs/
engine31/
engine32/
obj/
link_out.txt
strict_out.txt
flat_link.txt
compile_errors.log
"""
open(gi_path, "w", encoding="utf-8").write(gi)

# 从 git index 中移除这些文件
for pattern in remove_patterns:
    subprocess.run([git, "rm", "--cached", "-r", "-q", "--", pattern],
                   capture_output=True)

# 添加新的 .gitignore
subprocess.run([git, "add", ".gitignore"], capture_output=True)

# 重新添加 ios_port 目录
subprocess.run([git, "add", "ios_port/", ".github/"], capture_output=True)

# 检查 staged 的文件大小
r = subprocess.run([git, "diff", "--cached", "--stat"], capture_output=True, text=True)
print(r.stdout[-500:] if r.stdout else "no output")

# 提交
subprocess.run([git, "commit", "-m", "clean: remove large files, add .gitignore"],
               capture_output=True)
print("committed")
