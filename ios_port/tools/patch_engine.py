# -*- coding: utf-8 -*-
"""CI 引擎补丁: 在下载的原始引擎上应用所有本地修复 (组装后/构建前运行)"""
import os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # ios_port/

def patch_file(path, transforms):
    if not os.path.isfile(path):
        print("PATCH SKIP (missing):", path)
        return False
    t = open(path, encoding="utf-8", errors="replace").read()
    orig = t
    for old, new in transforms:
        t = t.replace(old, new)
    if t != orig:
        open(path, "w", encoding="utf-8").write(t)
        print("PATCHED:", path)
        return True
    return False

# 1) AssetsManager: iOS 无 system()
patch_file(
    "engine/js-bindings/cocos2d-x/extensions/assets-manager/AssetsManager.cpp",
    [("system(command.c_str());", "// system(command.c_str()); [kzsg3-ios-port]")],
)

# 2) FileUtils.setPopupNotify 原生绑定 (final SDK 有, beta 缺失)
f = "engine/js-bindings/bindings/manual/cocos2d_specifics.cpp"
if os.path.isfile(f):
    t = open(f, encoding="utf-8", errors="replace").read()
    if "js_cocos2dx_CCFileUtils_setPopupNotify" not in t:
        func = (
            "bool js_cocos2dx_CCFileUtils_setPopupNotify(JSContext *cx, uint32_t argc, jsval *vp)\n"
            "{\n"
            "    JSObject *obj = JS_THIS_OBJECT(cx, vp);\n"
            "    js_proxy_t *proxy = jsb_get_js_proxy(obj);\n"
            "    cocos2d::FileUtils* cobj = (cocos2d::FileUtils *)(proxy ? proxy->ptr : NULL);\n"
            "    JSB_PRECONDITION2( cobj, cx, false, \"Invalid Native Object\");\n"
            "    if (argc == 1) {\n"
            "        bool arg0 = (JSVAL_TO_BOOLEAN(argv[0]) == JS_TRUE);\n"
            "        cobj->setPopupNotify(arg0);\n"
            "        JS_SET_RVAL(cx, vp, JSVAL_VOID);\n"
            "        return true;\n"
            "    }\n"
            "    JS_SET_RVAL(cx, vp, JSVAL_VOID);\n"
            "    return true;\n"
            "}\n\n"
            "bool js_cocos2dx_CCFileUtils_setSearchPaths"
        )
        t = t.replace("bool js_cocos2dx_CCFileUtils_setSearchPaths", func, 1)
        old = ('JS_DefineFunction(cx, jsb_cocos2d_FileUtils_prototype, "setSearchResolutionsOrder", '
               'js_cocos2dx_CCFileUtils_setSearchResolutionsOrder, 1, JSPROP_PERMANENT );')
        new = old + ('\n    JS_DefineFunction(cx, jsb_cocos2d_FileUtils_prototype, "setPopupNotify", '
                     'js_cocos2dx_CCFileUtils_setPopupNotify, 1, JSPROP_PERMANENT );')
        assert old in t, "registration anchor missing"
        t = t.replace(old, new, 1)
        open(f, "w", encoding="utf-8").write(t)
        print("PATCHED:", f, "(setPopupNotify)")
    else:
        print("already patched:", f)
else:
    print("PATCH SKIP (missing):", f)

print("engine patch step complete")
