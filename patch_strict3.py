# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_strict.py"
t = open(p, encoding="utf-8").read()
# 添加 CoreFoundation.tbd 显式输入
if "CoreFoundation.tbd" not in t:
    t = t.replace(
        '''    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",''',
        '''    cf_tbd = os.path.join(TBD, "System", "Library", "Frameworks", "CoreFoundation.framework", "CoreFoundation.tbd")
    if os.path.isfile(cf_tbd):
        args.append(fwd(cf_tbd))
    fp_tbd = os.path.join(TBD, "System", "Library", "Frameworks", "FileProvider.framework", "FileProvider.tbd")
    if os.path.isfile(fp_tbd):
        args.append(fwd(fp_tbd))
    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",''')
# 加 -undefined dynamic_lookup 兜底
t = t.replace('"-no_function_starts",', '"-no_function_starts",\n        "-undefined", "dynamic_lookup",')
open(p, "w", encoding="utf-8").write(t)
print("patched")
