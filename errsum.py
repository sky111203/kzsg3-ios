import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
fatals = sorted(set(re.findall(r"fatal error: '([^']+)' file not found", t)))
print("== missing headers ==")
for h in fatals: print("  ", h)
# count per-file failures
files = re.findall(r"==== (D:[^\n]+)", t)
print("failed files:", len(files))
# other real error lines (non-fatal)
errs = re.findall(r"^D:[^\n]*?:\d+:\d+: error: (.*)$", t, re.M)
from collections import Counter
c = Counter(errs)
print("== top error kinds ==")
for k, v in c.most_common(25):
    print(f"  x{v:4d}  {k[:130]}")
