// KGOperatorBridge.cpp — koogame 渠道桥的 iOS 本地实现
//
// 原理:
//   原包 Android 侧由 Java/KooCocos2dx + KG::Operator(libcocos2dx.so) 承接
//   JS 通过 ChannelExport.js 发出的渠道调用 (模块 kooum/koopay/koomarketmodule/...),
//   支付走短信/渠道计费。本 APK 为已破解版本: 支付被改为直接成功。
//   iOS 侧没有这些渠道 SDK, 本桥以"本地直接应答成功"复刻同样的运行时行为,
//   使商店购买/赠送/活动奖励等功能与破解版逻辑完全一致。
//
// 桥接面 (以包内 ChannelExport.jsc / Pay.jsc 的调用形状为准):
//   RequestChannel(module, method, args, callback)
//   ResponseChannel(module, json) — 由 native 主动回 JS (payCB 等价物)
// 本桥对任意调用形状做防御式匹配, 回调给出 canonical 成功 JSON:
//   {"status":1,"success":true,"result":1,"payState":2,...}

#include "KGOperatorBridge.h"
#include "cocos2d.h"
#include "ScriptingCore.h"
#include "jsapi.h"

#include <string>

USING_NS_CC;

// ---- helpers ----

static JSObject *GetGlobal(JSContext *cx)
{
    return ScriptingCore::getInstance()->getGlobalObject();
}

static std::string jsval_to_stdstring(JSContext *cx, jsval v)
{
    JS::RootedValue vv(cx, v);
    JSString *s = JS::ToString(cx, vv);
    if (!s) return "";
    JSAutoByteString b(cx, s);
    return b.ptr() ? std::string(b.ptr()) : std::string();
}

// canonical 成功应答
static std::string success_payload(const std::string &method, const std::string &module)
{
    std::string s = "{\"status\":1,\"success\":true,\"result\":1,\"ret\":0,\"code\":0,";
    s += "\"payState\":2,\"payResult\":1,\"isSuccess\":true,";
    s += "\"method\":\"" + method + "\",\"module\":\"" + module + "\",";
    s += "\"msg\":\"ok\",\"data\":null}";
    return s;
}

// 在 JS 里求值 JSON 字面量得到数据对象
static bool eval_payload(JSContext *cx, const std::string &module,
                         const std::string &method, jsval &out)
{
    JSObject *global = GetGlobal(cx);
    if (!global) return false;
    std::string payload = success_payload(method, module);
    std::string expr = "(JSON.parse('" + payload + "'))";
    return JS_EvaluateScript(cx, global, expr.c_str(), (unsigned)expr.size(), "KGBridge", 1, &out);
}

// 触发 window.KGOperatorResponse(module, data) (若 JS 侧有监听)
static void fire_global_response(JSContext *cx, const std::string &module,
                                 const std::string &method)
{
    JSObject *global = GetGlobal(cx);
    if (!global) return;
    JS::RootedValue listenerv(cx);
    if (!JS_GetProperty(cx, global, "KGOperatorResponse", &listenerv))
        return;
    if (JSVAL_IS_PRIMITIVE(listenerv))
        return;
    JS::RootedObject fn(cx, JSVAL_TO_OBJECT(listenerv));
    if (!JS_ObjectIsFunction(cx, fn))
        return;

    jsval data = JSVAL_NULL;
    if (!eval_payload(cx, module, method, data))
        return;

    JSString *mstr = JS_NewStringCopyZ(cx, module.c_str());
    jsval argv[2];
    argv[0] = STRING_TO_JSVAL(mstr);
    argv[1] = data;
    jsval rv = JSVAL_NULL;
    JS_CallFunctionValue(cx, global, listenerv, 2, argv, &rv);
}

// 分发回调: callback 可能是 function 或 {callback: fn} 等形状
static void call_js_callback(JSContext *cx, jsval callback, const std::string &module,
                             const std::string &method)
{
    jsval data = JSVAL_NULL;
    bool have_data = eval_payload(cx, module, method, data);

    jsval fn = JSVAL_NULL;
    if (!JSVAL_IS_PRIMITIVE(callback)) {
        JS::RootedObject o(cx, JSVAL_TO_OBJECT(callback));
        if (JS_ObjectIsFunction(cx, o)) {
            fn = callback;                       // 直接是函数
        } else {
            static const char *fields[] = {"callback", "cb", "onSuccess", "onsuccess",
                                           "success", "succuss", "succCallback", "func"};
            for (int i = 0; i < 8; ++i) {
                JS::RootedValue v(cx);
                if (JS_GetProperty(cx, o, fields[i], &v) && !JSVAL_IS_PRIMITIVE(v)
                    && JS_ObjectIsFunction(cx, JSVAL_TO_OBJECT(v))) {
                    fn = v;
                    break;
                }
            }
        }
    }

    if (!JSVAL_IS_NULL(fn)) {
        JS::RootedObject fobj(cx, JSVAL_TO_OBJECT(fn));
        jsval argv[1];
        argv[0] = have_data ? data : JSVAL_TRUE;
        jsval rv = JSVAL_NULL;
        JS_CallFunctionValue(cx, fobj, fn, 1, argv, &rv);
        return;
    }

    fire_global_response(cx, module, method);
}

// ---- natives ----

// RequestChannel(module, method, args, callback)
static bool js_KG_RequestChannel(JSContext *cx, unsigned argc, jsval *vp)
{
    jsval *args = vp + 2;
    std::string module = (argc > 0) ? jsval_to_stdstring(cx, args[0]) : "koojscb";
    std::string method = (argc > 1) ? jsval_to_stdstring(cx, args[1]) : "";
    jsval callback = JSVAL_NULL;
    if (argc >= 4)      callback = args[3];
    else if (argc == 3) callback = args[2];   // (module, method, callback) 变体

    CCLOG("KZSG3-iOS: KG RequestChannel module=%s method=%s", module.c_str(), method.c_str());
    call_js_callback(cx, callback, module, method);
    JS::CallArgs cargs = JS::CallArgsFromVp(argc, vp);
    cargs.rval().setBoolean(true);
    return true;
}

// RequestChannel({module|Operator, method, args, callback}) 单对象变体
static bool js_KG_RequestChannelObj(JSContext *cx, unsigned argc, jsval *vp)
{
    jsval *args = vp + 2;
    std::string module = "koojscb", method = "";
    jsval callback = JSVAL_NULL;
    if (argc >= 1 && !JSVAL_IS_PRIMITIVE(args[0])) {
        JS::RootedObject o(cx, JSVAL_TO_OBJECT(args[0]));
        JS::RootedValue v(cx);
        if (JS_GetProperty(cx, o, "module", &v) && !JSVAL_IS_PRIMITIVE(v))
            module = jsval_to_stdstring(cx, v);
        if (JS_GetProperty(cx, o, "Operator", &v) && !JSVAL_IS_PRIMITIVE(v))
            module = jsval_to_stdstring(cx, v);
        if (JS_GetProperty(cx, o, "method", &v) && !JSVAL_IS_PRIMITIVE(v))
            method = jsval_to_stdstring(cx, v);
        if (JS_GetProperty(cx, o, "callback", &v) && !JSVAL_IS_PRIMITIVE(v))
            callback = v;
        else if (JS_GetProperty(cx, o, "cb", &v) && !JSVAL_IS_PRIMITIVE(v))
            callback = v;
    }
    call_js_callback(cx, callback, module, method);
    JS::CallArgs cargs = JS::CallArgsFromVp(argc, vp);
    cargs.rval().setBoolean(true);
    return true;
}

static bool js_KG_ResponseChannel(JSContext *cx, unsigned argc, jsval *vp)
{
    CCLOG("KZSG3-iOS: KG ResponseChannel (no-op)");
    JS::CallArgs cargs = JS::CallArgsFromVp(argc, vp);
    cargs.rval().setBoolean(true);
    return true;
}

static bool js_KG_isPlatformSupported(JSContext *cx, unsigned argc, jsval *vp)
{
    JS::CallArgs cargs = JS::CallArgsFromVp(argc, vp);
    cargs.rval().setBoolean(true);
    return true;
}

// ---- 注册 ----

static void define_fn(JSContext *cx, JSObject *obj, const char *name, JSNative fn, unsigned nargs)
{
    if (obj)
        JS_DefineFunction(cx, obj, name, fn, nargs,
                          JSPROP_READONLY | JSPROP_PERMANENT | JSPROP_ENUMERATE);
}

static JSObject *define_object(JSContext *cx, JSObject *parent, const char *name)
{
    JSObject *o = JS_NewObject(cx, NULL, NULL, parent);
    if (o) {
        JS::RootedValue v(cx, OBJECT_TO_JSVAL(o));
        JS_SetProperty(cx, parent, name, v);
    }
    return o;
}

static void register_operator_object(JSContext *cx, JSObject *o)
{
    define_fn(cx, o, "RequestChannel", js_KG_RequestChannel, 4);
    define_fn(cx, o, "RequestChannelObj", js_KG_RequestChannelObj, 1);
    define_fn(cx, o, "ResponseChannel", js_KG_ResponseChannel, 2);
    define_fn(cx, o, "Operator", js_KG_RequestChannel, 4);
    define_fn(cx, o, "isPlatformSupported", js_KG_isPlatformSupported, 0);
}

void register_KG_Operator(JSContext *cx, JSObject *global)
{
    // window.KG.Operator.*
    JSObject *kg = define_object(cx, global, "KG");
    if (kg) {
        JSObject *op = define_object(cx, kg, "Operator");
        register_operator_object(cx, op);
    }

    // window.KGOperator.*
    JSObject *kgo = define_object(cx, global, "KGOperator");
    register_operator_object(cx, kgo);

    // window.KGOperatorNative.* (额外别名, 提高命中率)
    JSObject *kgn = define_object(cx, global, "KGOperatorNative");
    register_operator_object(cx, kgn);

    // window.RequestChannel 直挂
    define_fn(cx, global, "RequestChannel", js_KG_RequestChannel, 4);

    // 渠道模块对象兜底: KGOperatorUM / KGOperatorSys / ...
    static const char *modules[] = {
        "KGOperatorUM", "KGOperatorSys", "KGOperatorKooMarket", "KGOperatorKooKTPlay",
        "KGOperatorKooData", "KGOperatorAync", "KGOperatorJSCB", "KGOperatorPay",
        "KGOperatorWeChat", "KGOperatorAdWall", "KGOperatorAd"
    };
    for (int i = 0; i < 11; ++i) {
        JS::RootedValue existing(cx);
        bool has = JS_GetProperty(cx, global, modules[i], &existing);
        if (has && !JSVAL_IS_PRIMITIVE(existing)
            && !JS_ObjectIsFunction(cx, JSVAL_TO_OBJECT(existing))) {
            // JS 侧已定义该模块对象: 补齐缺失的 RequestChannel
            JSObject *mo = JSVAL_TO_OBJECT(existing);
            JS::RootedValue hasRC(cx);
            if (!(JS_GetProperty(cx, mo, "RequestChannel", &hasRC) && !JSVAL_IS_PRIMITIVE(hasRC)))
                register_operator_object(cx, mo);
        } else {
            JSObject *mo = define_object(cx, global, modules[i]);
            register_operator_object(cx, mo);
        }
    }

    CCLOG("KZSG3-iOS: KGOperatorBridge registered");
}
