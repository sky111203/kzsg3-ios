# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_strict.py"
t = open(p, encoding="utf-8").read()
# 改为使用 15.6 SDK 原始 tbd 文件路径
old_tbd = 'TBD = r"D:\\dsh\\kzsg3_port\\out\\good_tbd"'
new_tbd = 'TBD = r"D:\\dsh\\kzsg3_port\\sdk156\\iPhoneOS15.6.sdk"'
t = t.replace(old_tbd, new_tbd)
# libSystem 路径从 usr/lib/libSystem.tbd 改为直接找
t = t.replace('''    for l in ["libSystem.tbd", "libc++.tbd", "libz.tbd", "libsqlite3.tbd", "libobjc.tbd"]:
        p = os.path.join(TBD, l)
        if os.path.isfile(p):
            args.append(fwd(p))''',
'''    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",
              "usr/lib/libz.tbd", "usr/lib/libsqlite3.tbd",
              "usr/lib/libobjc.tbd"]:
        p = os.path.join(TBD, l.replace("/", os.sep))
        if os.path.isfile(p):
            args.append(fwd(p))''')
# 框架 tbd 路径
t = t.replace(
    '''        p = os.path.join(TBD, f + ".tbd")''',
    '''        p = os.path.join(TBD, "System", "Library", "Frameworks", f + ".framework", f + ".tbd")''')
open(p, "w", encoding="utf-8").write(t)
print("link_strict patched to use 15.6 SDK originals")
