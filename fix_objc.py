# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = '''        for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', doc, re.S):
            for s in re.findall(r"'([^']+)'", mm.group(1)):
                objc_classes.add(s)'''
new = '''        for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', doc, re.S):
            foundq = re.findall(r"'([^']+)'", mm.group(1))
            if foundq:
                objc_classes.update(foundq)
            else:
                for s in mm.group(1).split(','):
                    s = s.strip()
                    if s and not s.startswith('"'):
                        objc_classes.add(s)'''
assert old in t, "pattern missing"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("objc-classes parsing fixed")
