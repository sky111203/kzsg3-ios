# -*- coding: utf-8 -*-
"""Build a complete cross-compile spec (sources, defines, includes) from the engine pbxprojs."""
import re, os, sys, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ios_port/
ENGINE = os.environ.get("ENGINE_BINDINGS",
    r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings")
CX = os.path.join(ENGINE, "cocos2d-x")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pbx_sources import parse_pbxproj, get_list, get_str, resolve_tree

def target_sources_and_settings(pbx_path, want):
    objs = parse_pbxproj(pbx_path)
    project = next(d for d in objs.values() if d["type"] == "PBXProject")
    m = re.search(r'mainGroup = ([0-9A-F]{24})', project["body"])
    tree = resolve_tree(objs, m.group(1))
    res = {}
    for oid, d in objs.items():
        if d["type"] != "PBXNativeTarget": continue
        nm = get_str(d["body"], "name")
        if nm != want: continue
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
        settings = []
        cm = re.search(r'buildConfigurationList = ([0-9A-F]{24})', d["body"])
        if cm:
            cl = objs.get(cm.group(1))
            for cfg_oid in get_list(cl["body"], "buildConfigurations"):
                cd = objs.get(cfg_oid)
                settings.append(cd["body"])
        res = {"sources": files, "settings": settings}
    return res

def parse_list_setting(body, key):
    m = re.search(key + r'\s*=\s*\(([^;]*?)\);', body, re.S)
    if not m: return []
    items = re.findall(r'"([^"]+)"', m.group(1))
    if not items:
        items = [x.strip().strip('"') for x in re.split(r',', m.group(1)) if x.strip()]
    return items

def parse_define_setting(body, key="GCC_PREPROCESSOR_DEFINITIONS"):
    items = parse_list_setting(body, key)
    out = []
    for it in items:
        it = it.strip().strip('"')
        if not it: continue
        if "=" in it:
            k, v = it.split("=", 1)
            out.append("-D" + k + "=" + v.strip('"'))
        else:
            out.append("-D" + it)
    return out

def build_basename_index(root):
    idx = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith((".cpp", ".c", ".mm", ".m")):
                idx.setdefault(f, []).append(os.path.join(dp, f).replace("\\", "/"))
    return idx

def resolve_src(p, base_dirs, idx):
    p = p.replace("\\", "/")
    if p.startswith("???"): return None
    cands = [os.path.normpath(os.path.join(b, p)) for b in base_dirs]
    for c in cands:
        if os.path.isfile(c):
            return c.replace("\\", "/")
    base = os.path.basename(p)
    hits = idx.get(base, [])
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # disambiguate by hint fragments in p
        frags = [x for x in p.split("/") if x and x != ".." and x != base]
        for h in hits:
            if all(fr in h for fr in frags):
                return h
        return hits[0]
    return None

def main():
    libs_pbx = os.path.join(CX, "build", "cocos2d_libs.xcodeproj", "project.pbxproj")
    jsb_pbx = os.path.join(ENGINE, "bindings", "proj.ios_mac", "cocos2d_js_bindings.xcodeproj", "project.pbxproj")

    spec = {"targets": {}}
    for pbx, tname, rootbase in [
        (libs_pbx, "cocos2dx iOS", CX),
        (libs_pbx, "cocos2dx-extensions iOS", CX),
        (libs_pbx, "chipmunk iOS", CX),
        (libs_pbx, "CocosDenshion iOS", CX),
        (jsb_pbx, "jsbindings iOS", os.path.dirname(os.path.dirname(ENGINE))),
    ]:
        r = target_sources_and_settings(pbx, tname)
        if not r: continue
        # base dirs: pbx dir + project root candidates
        basedir = os.path.dirname(pbx)
        base_dirs = [basedir, CX, ENGINE, os.path.dirname(ENGINE)]
        idx = build_basename_index(CX)
        for f in os.listdir(ENGINE):
            sub = os.path.join(ENGINE, f)
            if os.path.isdir(sub):
                for k, v in build_basename_index(sub).items():
                    idx.setdefault(k, [])
                    for vv in v:
                        if vv not in idx[k]:
                            idx[k].append(vv)
        sources, missing = [], []
        for p in r["sources"]:
            ap = resolve_src(p, base_dirs, idx)
            if ap: sources.append(ap)
            else: missing.append(p)
        defines = []
        includes = []
        other = []
        for s in r["settings"]:
            defines += parse_define_setting(s)
            for inc in parse_list_setting(s, "USER_HEADER_SEARCH_PATHS") + parse_list_setting(s, "HEADER_SEARCH_PATHS"):
                includes.append(inc)
            ol = parse_list_setting(s, "OTHER_LDFLAGS")
            other += ol
        spec["targets"][tname] = {"sources": sources, "missing": missing,
                                  "defines": sorted(set(defines)),
                                  "includes_raw": includes, "other_ldflags": other}
        print(tname, "sources:", len(sources), "missing:", len(missing))
        if missing[:3]: print("  missing sample:", missing[:3])

    json.dump(spec, open(os.path.join(BASE, "..", "crossbuild_spec.json"), "w"), indent=1)
    print("spec written")

if __name__ == "__main__":
    main()
