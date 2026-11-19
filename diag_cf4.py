import re
p = r"D:\dsh\kzsg3_port\sdk156\iPhoneOS15.6.sdk\System\Library\Frameworks\CoreFoundation.framework\CoreFoundation.tbd"
t = open(p, encoding="utf-8", errors="replace").read()
ms = list(re.finditer(r'- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S))
for m in ms:
    cap = m.group(1)
    print("capture len:", len(cap))
    print(cap[:300])
    print("---")
