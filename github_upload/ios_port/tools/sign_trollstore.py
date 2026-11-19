# -*- coding: utf-8 -*-
"""Pre-sign the IPA with ldid (ad-hoc) for TrollStore, then repack."""
import os, zipfile, shutil, subprocess, sys

IPA = r"D:\dsh\kzsg3_port\out\KZSG3-ios-arm64-unsigned.ipa"
LDID = r"D:\dsh\kzsg3_port\ldid.exe"
WORK = r"D:\dsh\kzsg3_port\out\sign_work"
OUT = r"D:\dsh\kzsg3_port\out\KZSG3-ios-arm64-trollstore.ipa"

def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK, exist_ok=True)
    with zipfile.ZipFile(IPA) as z:
        z.extractall(WORK)
    app = os.path.join(WORK, "Payload", "KZSG3.app")
    exe = os.path.join(app, "KZSG3")
    print("signing:", exe)
    r = subprocess.run([LDID, "-S", exe], capture_output=True, text=True)
    print("rc:", r.returncode, r.stderr[-500:] if r.stderr else "")
    if r.returncode != 0:
        sys.exit(1)
    # verify signature present
    r2 = subprocess.run([LDID, "-d", exe], capture_output=True, text=True)
    print(r2.stdout[:400])
    # repack
    if os.path.exists(OUT):
        os.remove(OUT)
    zf = zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6)
    n = 0
    for dp, dn, fn in os.walk(os.path.join(WORK, "Payload")):
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, WORK)
            zf.write(p, rel)
            n += 1
    zf.close()
    print("signed IPA:", OUT, os.path.getsize(OUT), "files:", n)

if __name__ == "__main__":
    main()
