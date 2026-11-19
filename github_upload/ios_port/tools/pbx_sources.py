# -*- coding: utf-8 -*-
"""Extract per-target source lists from pbxproj with brace-balanced object parsing."""
import re, os, sys, json

def parse_pbxproj(path):
    t = open(path, encoding="utf-8").read()
    objs = {}
    # object entries look like: \n\t\tXXXX24 /* label */ = {\n ... \n\t\t};   (label may be absent)
    for m in re.finditer(r'\n\t\t([0-9A-F]{24})(?: /\* ([^*]+) \*/)? = \{', t):
        oid = m.group(1)
        i = m.end()  # position after '{'
        depth = 1
        j = i
        while depth > 0 and j < len(t):
            c = t[j]
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            j += 1
        body = t[i:j-1]
        # find trailing 'type' via isa
        im = re.search(r'isa = (\w+);', body)
        objs[oid] = {"oid": oid, "label": (m.group(2) or "").strip(),
                     "type": im.group(1) if im else "?", "body": body}
    return objs

def get_list(body, key):
    m = re.search(key + r'\s*=\s*\(', body)
    if not m: return []
    i = m.end()
    depth = 1
    j = i
    while depth > 0 and j < len(body):
        c = body[j]
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        j += 1
    inner = body[i:j-1]
    return re.findall(r'([0-9A-F]{24}) /\*', inner)

def get_str(body, key):
    m = re.search(key + r'\s*=\s*"([^"]*)"', body)
    return m.group(1) if m else None

def get_setting(body, key):
    m = re.search(r'^\s*' + re.escape(key) + r'\s*=\s*(.+?);\s*$', body, re.M)
    return m.group(1).strip() if m else None

def resolve_tree(objs, root_group):
    out = {}
    def walk(oid, base):
        d = objs.get(oid)
        if not d: return
        if d["type"] == "PBXGroup":
            gpath = get_str(d["body"], "path")
            cur = os.path.join(base, gpath) if gpath else base
            for c in get_list(d["body"], "children"):
                walk(c, cur)
        elif d["type"] == "PBXFileReference":
            fpath = get_str(d["body"], "path")
            fname = fpath if fpath else d["label"]
            out[oid] = os.path.join(base, fname).replace("\\", "/") if fname else base
    walk(root_group, "")
    return out

def main(pbx, want=None, out_json=None):
    objs = parse_pbxproj(pbx)
    project = next(d for d in objs.values() if d["type"] == "PBXProject")
    m = re.search(r'mainGroup = ([0-9A-F]{24})', project["body"])
    tree = resolve_tree(objs, m.group(1))
    result = {}
    # build configuration lists (settings per target)
    for oid, d in objs.items():
        if d["type"] != "PBXNativeTarget": continue
        nm = get_str(d["body"], "name")
        if want and nm not in want: continue
        files = []
        for ph in get_list(d["body"], "buildPhases"):
            pd = objs.get(ph)
            if not pd or pd["type"] != "PBXSourcesBuildPhase": continue
            for bf in get_list(pd["body"], "files"):
                bd = objs.get(bf)
                if not bd: continue
                mm = re.search(r'fileRef = ([0-9A-F]{24})', bd["body"])
                if not mm: continue
                files.append(tree.get(mm.group(1), "???" + mm.group(1)))
        # config list
        settings = {}
        cm = re.search(r'buildConfigurationList = ([0-9A-F]{24})', d["body"])
        if cm:
            cl = objs.get(cm.group(1))
            if cl:
                for cfg_oid in get_list(cl["body"], "buildConfigurations"):
                    cd = objs.get(cfg_oid)
                    if not cd: continue
                    base = re.search(r'baseConfigurationReference = ([0-9A-F]{24})', cd["body"])
                    cname = get_str(cd["body"], "name")
                    settings[cname] = cd["body"]
        result[nm] = {"sources": files, "count": len(files),
                      "configs": {k: v for k, v in settings.items()}}
    if out_json:
        json.dump(result, open(out_json, "w", encoding="utf-8"), indent=1)
    for nm, r in result.items():
        print("=== %s : %d sources" % (nm, r["count"]))
        bad = [f for f in r["sources"] if f.startswith("???")]
        if bad: print("  UNRESOLVED:", len(bad), bad[:3])
        for f in r["sources"][:10]:
            print("   ", f)
        if r["count"] > 10:
            print("    ... +%d more" % (r["count"] - 10))

if __name__ == "__main__":
    outj = None
    argv = sys.argv[1:]
    if argv and argv[-1].endswith(".json"):
        outj = argv.pop()
    main(argv[0], argv[1:] or None, outj)
