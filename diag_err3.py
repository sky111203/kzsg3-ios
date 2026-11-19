import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
blocks = re.split(r"==== (D:[^\n]+)", t)
for j in range(1, len(blocks), 2):
    p, body = blocks[j], blocks[j+1]
    errs = [l for l in body.splitlines() if ": error:" in l or "fatal error:" in l]
    if errs:
        print("=====", p.split("/")[-1], len(errs))
        for e in errs[:4]:
            print("   ", e[-180:])
