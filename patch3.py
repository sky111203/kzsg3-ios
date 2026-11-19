p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
t = t.replace('"-error-limit=0"', '"--error-limit=0"')
open(p, "w", encoding="utf-8").write(t)
p2 = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t2 = open(p2, encoding="utf-8").read()
t2 = t2.replace('''        m = re.search(r"install-name:\\s*'([^']+)'", doc)''',
'''        m = re.search(r"install-name:\\s*'([^']+)'|install-name:\\s*\\"([^\\"]+)\\"", doc)
        if m and not m.group(1):
            m = re.search(r"install-name:\\s*(\\S+)", doc)''')
open(p2, "w", encoding="utf-8").write(t2)
print("patched both")
