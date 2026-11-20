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
            "    jsval *argv = JS_ARGV(cx, vp);\n"
            "    JSObject *obj = JS_THIS_OBJECT(cx, vp);\n"
            "    js_proxy_t *proxy = jsb_get_js_proxy(obj);\n"
            "    cocos2d::FileUtils* cobj = (cocos2d::FileUtils *)(proxy ? proxy->ptr : NULL);\n"
            "    JSB_PRECONDITION2( cobj, cx, false, \"Invalid Native Object\");\n"
            "    if (argc >= 1) {\n"
            "        bool arg0 = (JSVAL_TO_BOOLEAN(argv[0]) != 0);\n"
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

# 3) cc.ReverseTime 类绑定 (final SDK 有, beta 自动绑定缺失; 游戏引擎 API 层直接引用)
fa = "engine/js-bindings/bindings/auto/jsb_cocos2dx_auto.cpp"
if os.path.isfile(fa):
    ta = open(fa, encoding="utf-8", errors="replace").read()
    if "js_register_cocos2dx_ReverseTime" not in ta:
        block = (
            "JSClass  *jsb_cocos2d_ReverseTime_class;\n"
            "JSObject *jsb_cocos2d_ReverseTime_prototype;\n\n"
            "static void js_cocos2d_ReverseTime_finalize(JSFreeOp *fop, JSObject *obj) {\n"
            "}\n\n"
            "bool js_cocos2dx_ReverseTime_create(JSContext *cx, uint32_t argc, jsval *vp)\n"
            "{\n"
            "\tjsval *argv = JS_ARGV(cx, vp);\n"
            "\tbool ok = true;\n"
            "\tif (argc == 1) {\n"
            "\t\tcocos2d::FiniteTimeAction* arg0;\n"
            "\t\tdo {\n"
            "\t\t\tif (!argv[0].isObject()) { ok = false; break; }\n"
            "\t\t\tjs_proxy_t *jsProxy;\n"
            "\t\t\tJSObject *tmpObj = JSVAL_TO_OBJECT(argv[0]);\n"
            "\t\t\tjsProxy = jsb_get_js_proxy(tmpObj);\n"
            "\t\t\targ0 = (cocos2d::FiniteTimeAction*)(jsProxy ? jsProxy->ptr : NULL);\n"
            "\t\t\tJSB_PRECONDITION2( arg0, cx, false, \"Invalid Native Object\");\n"
            "\t\t} while (0);\n"
            "\t\tJSB_PRECONDITION2( ok, cx, false, \"js_cocos2dx_ReverseTime_create : Error processing arguments\");\n"
            "\t\tcocos2d::ReverseTime* ret = cocos2d::ReverseTime::create(arg0);\n"
            "\t\tjsval jsret = JSVAL_NULL;\n"
            "\t\tdo {\n"
            "\t\t\tif (ret) {\n"
            "\t\t\t\tjs_proxy_t *jsProxy = js_get_or_create_proxy<cocos2d::ReverseTime>(cx, (cocos2d::ReverseTime*)ret);\n"
            "\t\t\t\tjsret = OBJECT_TO_JSVAL(jsProxy->obj);\n"
            "\t\t\t} else {\n"
            "\t\t\t\tjsret = JSVAL_NULL;\n"
            "\t\t\t}\n"
            "\t\t} while (0);\n"
            "\t\tJS_SET_RVAL(cx, vp, jsret);\n"
            "\t\treturn true;\n"
            "\t}\n"
            "\tJS_ReportError(cx, \"wrong number of arguments: %d, was expecting %d\", argc, 1);\n"
            "\treturn false;\n"
            "}\n\n"
            "void js_register_cocos2dx_ReverseTime(JSContext *cx, JSObject *global) {\n"
            "\tjsb_cocos2d_ReverseTime_class = (JSClass *)calloc(1, sizeof(JSClass));\n"
            "\tjsb_cocos2d_ReverseTime_class->name = \"ReverseTime\";\n"
            "\tjsb_cocos2d_ReverseTime_class->addProperty = JS_PropertyStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->delProperty = JS_DeletePropertyStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->getProperty = JS_PropertyStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->setProperty = JS_StrictPropertyStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->enumerate = JS_EnumerateStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->resolve = JS_ResolveStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->convert = JS_ConvertStub;\n"
            "\tjsb_cocos2d_ReverseTime_class->finalize = js_cocos2d_ReverseTime_finalize;\n"
            "\tjsb_cocos2d_ReverseTime_class->flags = JSCLASS_HAS_RESERVED_SLOTS(2);\n\n"
            "\tstatic JSPropertySpec properties[] = {\n"
            "\t\t{\"__nativeObj\", 0, JSPROP_ENUMERATE | JSPROP_PERMANENT, JSOP_WRAPPER(js_is_native_obj), JSOP_NULLWRAPPER},\n"
            "\t\t{0, 0, 0, JSOP_NULLWRAPPER, JSOP_NULLWRAPPER}\n"
            "\t};\n\n"
            "\tstatic JSFunctionSpec funcs[] = {\n"
            "\t\tJS_FS_END\n"
            "\t};\n\n"
            "\tstatic JSFunctionSpec st_funcs[] = {\n"
            "\t\tJS_FN(\"create\", js_cocos2dx_ReverseTime_create, 1, JSPROP_PERMANENT | JSPROP_ENUMERATE),\n"
            "\t\tJS_FS_END\n"
            "\t};\n\n"
            "\tjsb_cocos2d_ReverseTime_prototype = JS_InitClass(\n"
            "\t\tcx, global,\n"
            "\t\tjsb_cocos2d_ActionInterval_prototype,\n"
            "\t\tjsb_cocos2d_ReverseTime_class,\n"
            "\t\tjs_cocos2dx_ReverseTime_create, 0,\n"
            "\t\tproperties,\n"
            "\t\tfuncs,\n"
            "\t\tNULL,\n"
            "\t\tst_funcs);\n\n"
            "\tTypeTest<cocos2d::ReverseTime> t;\n"
            "\tjs_type_class_t *p;\n"
            "\tstd::string typeName = t.s_name();\n"
            "\tif (_js_global_type_map.find(typeName) == _js_global_type_map.end())\n"
            "\t{\n"
            "\t\tp = (js_type_class_t *)malloc(sizeof(js_type_class_t));\n"
            "\t\tp->jsclass = jsb_cocos2d_ReverseTime_class;\n"
            "\t\tp->proto = jsb_cocos2d_ReverseTime_prototype;\n"
            "\t\tp->parentProto = jsb_cocos2d_ActionInterval_prototype;\n"
            "\t\t_js_global_type_map.insert(std::make_pair(typeName, p));\n"
            "\t}\n"
            "}\n\n"
            "void js_register_cocos2dx_ScaleTo(JSContext *cx, JSObject *obj) {"
        )
        anchor = "void js_register_cocos2dx_ScaleTo(JSContext *cx, JSObject *obj) {"
        assert anchor in ta, "ScaleTo js_register anchor missing"
        ta = ta.replace(anchor, block, 1)
        call_anchor = "js_register_cocos2dx_ScaleTo(cx, obj);"
        assert call_anchor in ta, "ScaleTo call anchor missing"
        ta = ta.replace(call_anchor, call_anchor + "\n\tjs_register_cocos2dx_ReverseTime(cx, obj);", 1)
        open(fa, "w", encoding="utf-8").write(ta)
        print("PATCHED:", fa, "(ReverseTime class binding)")
    else:
        print("already patched:", fa)
else:
    print("PATCH SKIP (missing):", fa)

print("engine patch step complete")
