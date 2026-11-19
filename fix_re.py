p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
if not t.startswith("# -*- coding"):
    pass
t = t.replace('"""Merge multi-document tbd files into one arm64-only tbd lld can parse fully."""',
              '"""Merge multi-document tbd files into one arm64-only tbd lld can parse fully."""\nimport re')
if "import re" not in t.split("\n\n")[0] and "\nimport re\n" not in t:
    t = t.replace("def merge_arm64", "import re\n\ndef merge_arm64", 1)
open(p, "w", encoding="utf-8").write(t)
print("re imported:", "import re" in t)
