p = r"D:\dsh\kzsg3_port\audit_ios15.py"
t = open(p, encoding="utf-8").read()
# 在 v3 分支后追加 objc-classes 解析（同 archs 块内的独立 key）
old = """        for m in re.finditer(r'- targets:\\s*\\[[^\\]]*arm64-ios[^\\]]*\\]\\s*\\n\\s*symbols:\\s*\\[(.*?)\\]', t, re.S):"""
new = """        # v3/v4 文件里的 objc-classes 独立块（同 frameworks 目录所有文件都扫）
        for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', t, re.S):
            for s in re.findall(r"'([^']+)'", mm.group(1)):
                exports.add("_OBJC_CLASS_$_" + s)
                exports.add("_OBJC_METACLASS_$_" + s)
        for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', t, re.S):
            for s in mm.group(1).split(","):
                s = s.strip()
                if s and not s.startswith("$ld$"):
                    exports.add("_OBJC_CLASS_$_" + s)
                    exports.add("_OBJC_METACLASS_$_" + s)
        for m in re.finditer(r'- targets:\\s*\\[[^\\]]*arm64-ios[^\\]]*\\]\\s*\\n\\s*symbols:\\s*\\[(.*?)\\]', t, re.S):"""
if old in t:
    t = t.replace(old, new, 1)
    open(p, "w", encoding="utf-8").write(t)
    print("audit patched")
else:
    print("pattern missing")
