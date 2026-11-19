import re, sys
p = r"D:\dsh\kzsg3_port\ipadump_page.html"
try:
    t = open(p, encoding="utf-8", errors="replace").read()
except Exception as e:
    print("read fail", e); sys.exit(0)
print("len:", len(t))
urls = re.findall(r'https?://[^"\'<> ]+', t)
for m in urls[:30]:
    print(m[:130])
print("--- hrefs ---")
for m in re.findall(r'href="([^"]+)"', t)[:30]:
    print(m[:130])
print("--- ipa mentions ---")
for m in re.findall(r'[^"\'<> ]*\.ipa[^"\'<> ]*', t)[:20]:
    print(m[:130])
