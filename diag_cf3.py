import re
p = r"D:\dsh\kzsg3_port\sdk156\iPhoneOS15.6.sdk\System\Library\Frameworks\CoreFoundation.framework\CoreFoundation.tbd"
t = open(p, encoding="utf-8", errors="replace").read()
syms = set()
n = 0
for m in re.finditer(r'- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
    n += 1
    for s in re.findall(r"'([^']+)'", m.group(1)):
        syms.add(s)
print("matches:", n, "syms:", len(syms))
print("_CFRelease in:", "_CFRelease" in syms)
