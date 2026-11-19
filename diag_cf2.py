t = open(r"D:\dsh\kzsg3_port\sdk156\iPhoneOS15.6.sdk\System\Library\Frameworks\CoreFoundation.framework\CoreFoundation.tbd", encoding="utf-8", errors="replace").read()
i = t.find("_CFRelease")
# find all "- targets:" occurrences in whole file and their distance to i
import re
last = None
for m in re.finditer(r'- targets:\s*\[([^\]]*)\]', t):
    if m.start() < i:
        last = (m.start(), m.group(1))
print("last targets block before CFRelease:", last[1] if last else None)
# check where arm64 section is
for m in re.finditer(r'- targets:\s*\[([^\]]*)\]', t):
    if "arm64-ios" in m.group(1) or "arm64e" in m.group(1):
        print("arm64 section at", m.start(), m.group(1)[:60])
        break
