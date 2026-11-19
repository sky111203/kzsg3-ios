# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = """    for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', doc, re.S):
        for s in re.findall(r"'([^']+)'", mm.group(1)):
            syms.add("_OBJC_CLASS_$_" + s)
            syms.add("_OBJC_METACLASS_$_" + s)"""
new = """    for mm in re.finditer(r'objc-classes:\\s*\\[(.*?)\\]', doc, re.S):
        foundq = re.findall(r"'([^']+)'", mm.group(1))
        if foundq:
            objc_classes.update(foundq)
        else:
            for s in mm.group(1).split(','):
                s = s.strip()
                if s and not s.startswith('"'):
                    objc_classes.add(s)"""
assert old in t, "pattern missing"
# also declare objc_classes at function start of _symbols_from_doc
t = t.replace(old, new)
old2 = """def _symbols_from_doc(doc):
    syms = set()"""
if old2 in t:
    t = t.replace(old2, """def _symbols_from_doc(doc):
    syms = set()
    objc_classes = set()""")
    t = t.replace("""    return syms

DEFAULT_INSTALL""", """    for c in objc_classes:
        syms.add("_OBJC_CLASS_$_" + c)
        syms.add("_OBJC_METACLASS_$_" + c)
    return syms

DEFAULT_INSTALL""")
open(p, "w", encoding="utf-8").write(t)
print("tbd_merge fully patched")
