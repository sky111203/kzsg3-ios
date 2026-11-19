# -*- coding: utf-8 -*-
"""Strip 're-exports' blocks from tbd files so lld stops hunting re-export chains.
We already pass every needed leaf tbd explicitly."""
import os, re, sys

SDK = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk"

def strip_reexports(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    out, skipping, removed = [], False, 0
    for ln in lines:
        if skipping:
            # a new top-level key ends the block (no leading spaces, ends with ':')
            if re.match(r'^[A-Za-z_-]+:\s*$', ln):
                skipping = False
                out.append(ln)
            else:
                removed += 1
            continue
        if re.match(r'^re-exports:\s*$', ln) or re.match(r'^reexported-libraries:\s*$', ln):
            skipping = True
            removed += 1
            continue
        out.append(ln)
    if removed:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    return removed

def fix_inputs(tbd_paths):
    total = 0
    for p in tbd_paths:
        if os.path.isfile(p):
            total += strip_reexports(p)
    return total

if __name__ == "__main__":
    for p in sys.argv[1:]:
        n = strip_reexports(p)
        print(os.path.basename(p), "removed lines:", n)
