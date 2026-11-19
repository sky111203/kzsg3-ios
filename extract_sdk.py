# -*- coding: utf-8 -*-
"""Extract iPhoneOS SDK tar.xz on Windows: resolve symlinks transitively, hardlinks from archive root."""
import tarfile, os, shutil, subprocess, sys

ARCHIVE = r"D:\dsh\kzsg3_port\iPhoneOS16.5.sdk.tar.xz"
DEST = r"D:\dsh\kzsg3_port\sdk"

def norm(p):
    return p.replace("\\", "/")

def main():
    tf = tarfile.open(ARCHIVE, "r:xz")
    members = tf.getmembers()
    reg, links = {}, {}
    dirs = set()
    for m in members:
        n = norm(m.name)
        if m.isdir():
            dirs.add(n)
        elif m.isfile():
            reg[n] = m
        elif m.issym() or m.islnk():
            links[n] = (m.linkname, m.issym())
    print("files:", len(reg), "dirs:", len(dirs), "links:", len(links))

    done = 0
    for n in dirs:
        os.makedirs(os.path.join(DEST, n.replace("/", os.sep)), exist_ok=True)
    for n, m in reg.items():
        p = os.path.join(DEST, n.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tf.extract(m, DEST, set_attrs=False)
        done += 1
    print("regular files extracted:", done)

    def exists_reg(n):
        return n in reg or os.path.isfile(os.path.join(DEST, n.replace("/", os.sep)))

    def resolve(n, linkname, is_sym):
        if is_sym and not linkname.startswith("/"):
            base = os.path.dirname(n)
            t = os.path.normpath(os.path.join(base, linkname)).replace("\\", "/")
        else:
            t = linkname.lstrip("/").replace("\\", "/")
        seen = 0
        while t in links and seen < 10:
            ln, sym = links[t]
            if sym and not ln.startswith("/"):
                t = os.path.normpath(os.path.join(os.path.dirname(t), ln)).replace("\\", "/")
            else:
                t = ln.lstrip("/").replace("\\", "/")
            seen += 1
        return t

    copied = junctions = failed = 0
    for n, (linkname, is_sym) in links.items():
        p = os.path.join(DEST, n.replace("/", os.sep))
        if os.path.exists(p):
            continue
        t = resolve(n, linkname, is_sym)
        tgt_fs = os.path.join(DEST, t.replace("/", os.sep))
        if exists_reg(t) or os.path.isfile(tgt_fs):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copyfile(tgt_fs, p)
            copied += 1
        elif os.path.isdir(tgt_fs) or t in dirs:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            r = subprocess.run(["cmd", "/c", "mklink", "/J", p, tgt_fs], capture_output=True)
            if r.returncode == 0:
                junctions += 1
            else:
                failed += 1
                if failed < 10:
                    print("  junction fail:", n, "->", t)
        else:
            failed += 1
            if failed < 15:
                print("  unresolvable:", n, "->", linkname, "(final:", t + ")")
    print("copied:", copied, "junctions:", junctions, "failed:", failed)

    for probe in ["usr/include/stdlib.h", "usr/include/pthread.h",
                  "System/Library/Frameworks/UIKit.framework/Headers/UIKit.h",
                  "usr/lib/libobjc.tbd", "usr/lib/libc++.tbd",
                  "System/Library/Frameworks/OpenGLES.framework/Headers/ES2/gl.h"]:
        print(probe, "->", os.path.exists(os.path.join(DEST, probe.replace("/", os.sep))))

if __name__ == "__main__":
    main()
