for p, old, new in [
  (r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py",
   "    symbols:              [ \" + \", \".join(\"'%s'\" % s for s in sorted(syms)) + \" ]\",",
   "    symbols:              [ " + chr(34) + " + \", \".join(s for s in sorted(syms)) + " + chr(34) + \" ],"),
  (r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py",
   "    symbols:              [ %s ]\" % \", \".join(\"'%s'\" % s for s in sorted(syms))",
   "    symbols:              [ %s ]\" % \", \".join(s for s in sorted(syms))"),
]:
    t = open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
        open(p, "w", encoding="utf-8").write(t)
        print("patched", p)
    else:
        print("NOT FOUND in", p)
