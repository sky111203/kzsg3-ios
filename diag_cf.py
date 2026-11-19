t = open(r"D:\dsh\kzsg3_port\sdk156\iPhoneOS15.6.sdk\System\Library\Frameworks\CoreFoundation.framework\CoreFoundation.tbd", encoding="utf-8", errors="replace").read()
i = t.find("_CFRelease")
seg = t[max(0,i-4000):i]
import re
for m in re.finditer(r'^\s*(- targets:.*)$', seg, re.M):
    print(m.group(1)[:120])
print("--- keys near:")
for m in re.finditer(r'^(\s*[a-zA-Z-]+:)', t[i-4000:i+10], re.M):
    print(repr(m.group(1)))
print("has arm64-ios anywhere before CFRelease within 4000:", "arm64-ios" in seg)
