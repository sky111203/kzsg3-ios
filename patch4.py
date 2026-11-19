p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = '''        m = re.search(r"install-name:\\s*'([^']+)'|install-name:\\s*\\"([^\\"]+)\\"", doc)
        if m and not m.group(1):
            m = re.search(r"install-name:\\s*(\\S+)", doc)'''
new = '''        m = None
        for mm in re.finditer(r"install-name:\\s*(.+)", doc):
            m = mm
            break
        if m:
            install_name = m.group(1).strip().strip("'\\\"")'''
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("patched")
