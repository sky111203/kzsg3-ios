# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_strict.py"
t = open(p, encoding="utf-8").read()
# 添加 CoreFoundation 和 libobjc
t = t.replace(
    '''    FRAMEWORKS = [
        "UIKit", "Foundation", "OpenGLES", "QuartzCore", "OpenAL", "AudioToolbox",
        "AVFoundation", "CoreGraphics", "CoreMotion", "MediaPlayer", "CFNetwork",
        "SystemConfiguration", "Security", "CoreText", "GameController",
    ]''',
    '''    FRAMEWORKS = [
        "UIKit", "Foundation", "CoreFoundation", "OpenGLES", "QuartzCore", "OpenAL", "AudioToolbox",
        "AVFoundation", "CoreGraphics", "CoreMotion", "MediaPlayer", "CFNetwork",
        "SystemConfiguration", "Security", "CoreText", "GameController", "FileProvider",
    ]''')
# 添加 libobjc tbd
t = t.replace(
    '''    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",
              "usr/lib/libz.tbd", "usr/lib/libsqlite3.tbd",
              "usr/lib/libobjc.tbd"]:''',
    '''    for l in ["usr/lib/libSystem.tbd", "usr/lib/libc++.tbd",
              "usr/lib/libz.tbd", "usr/lib/libsqlite3.tbd",
              "usr/lib/libobjc.tbd", "usr/lib/libobjc.A.tbd"]:''')
# 确保 KZCrashHandler.mm 在编译列表里
if "KZCrashHandler.mm" not in t:
    pass  # link_strict 不含 app sources, 只处理 .o
open(p, "w", encoding="utf-8").write(t)
print("link_strict patched")
