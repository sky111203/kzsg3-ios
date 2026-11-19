p = r"D:\dsh\kzsg3_port\audit_ios15.py"
t = open(p, encoding="utf-8").read()
old = """        for m in re.finditer(r'- targets:\\s*\\[[^\\]]*arm64-ios[^\\]]*\\]\\s*\\n\\s*symbols:\\s*\\[(.*?)\\]', t, re.S):"""
new = """        # v3 style: - archs: [ arm64 ] / platform: ios, then symbols: [ unquoted ]
        for m in re.finditer(r'- archs:\\s*\\[[^\\]]*arm64[^\\]]*\\]\\s*\\n\\s*symbols:\\s*\\[(.*?)\\]', t, re.S):
            for s2 in m.group(1).split(","):
                s2 = s2.strip()
                if s2 and not s2.startswith("$ld$"):
                    exports.add(s2)
        for m in re.finditer(r'- targets:\\s*\\[[^\\]]*arm64-ios[^\\]]*\\]\\s*\\n\\s*symbols:\\s*\\[(.*?)\\]', t, re.S):"""
if old in t:
    t = t.replace(old, new)
    open(p, "w", encoding="utf-8").write(t)
    print("patched v3")
else:
    print("pattern not found; manual fix needed")
