// JSErrorHUD.cpp — 启动诊断实现 (适配 cocos2d-x v3.0-beta API)
#include "JSErrorHUD.h"
#include "cocos2d.h"
#include "ScriptingCore.h"
#include "jsapi.h"

#include <string>
#include <vector>
#include <sys/stat.h>
#include <sys/types.h>

USING_NS_CC;

static std::vector<std::string> g_lines;
static std::string g_file;
static bool g_installed = false;

static void append_file(const std::string &s)
{
    if (g_file.empty())
        g_file = FileUtils::getInstance()->getWritablePath() + "kzsg3_log.txt";
    // Documents 目录可能不存在: 先递归创建, 否则 fopen 静默失败
    static bool dir_ensured = false;
    if (!dir_ensured) {
        size_t pos = g_file.rfind('/');
        if (pos != std::string::npos) {
            std::string dir = g_file.substr(0, pos);
            mkdir(dir.c_str(), 0755);
        }
        dir_ensured = true;
    }
    FILE *f = fopen(g_file.c_str(), "a");
    if (f) {
        fputs((s + "\n").c_str(), f);
        fclose(f);
    }
}

void JSErrorHUD::log(const std::string &line)
{
    g_lines.push_back(line);
    if (g_lines.size() > 60)
        g_lines.erase(g_lines.begin());
    append_file(line);
    CCLOG("KZSG3: %s", line.c_str());
}

static std::string jsval_to_std(JSContext *cx, JS::HandleValue v)
{
    JS::RootedString s(cx, JS::ToString(cx, v));
    if (!s) return "(unstringable)";
    size_t len = 0;
    const char16_t *chars = JS_GetStringCharsAndLength(cx, s, &len);
    if (!chars) return "(no chars)";
    std::string out;
    for (size_t i = 0; i < len; ++i) {
        char16_t c = chars[i];
        if (c < 128) out += (char)c;
        else out += '?';
    }
    return out;
}

void JSErrorHUD::drainJSException(JSContext *cx, const std::string &where)
{
    if (!cx) return;
    if (!JS_IsExceptionPending(cx))
        return;
    JS::RootedValue exn(cx);
    if (JS_GetPendingException(cx, &exn)) {
        JS_ClearPendingException(cx);
        JSObject *g = ScriptingCore::getInstance()->getGlobalObject();
        if (g) {
            JSAutoCompartment ac(cx, g);
            log("JS EXCEPTION @ " + where + ": " + jsval_to_std(cx, exn));
        } else {
            log("JS EXCEPTION @ " + where + ": (no global)");
        }
    } else {
        log("JS EXCEPTION @ " + where + ": (unfetchable)");
    }
}

// JS log() 重定向
static bool js_kzsg3_log(JSContext *cx, unsigned argc, JS::Value *vp)
{
    JS::CallArgs args = JS::CallArgsFromVp(argc, vp);
    std::string out;
    for (unsigned i = 0; i < args.length(); ++i) {
        out += jsval_to_std(cx, args[i]);
        if (i + 1 < args.length()) out += " ";
    }
    JSErrorHUD::log("JS: " + out);
    args.rval().setUndefined();
    return true;
}

class HUDUpdater : public Ref
{
public:
    static HUDUpdater *getInstance()
    {
        static HUDUpdater *inst = nullptr;
        if (!inst) { inst = new HUDUpdater(); inst->retain(); }
        return inst;
    }
    virtual void update(float dt)
    {
        auto director = Director::getInstance();
        auto scene = director->getRunningScene();
        if (!scene) return;
        auto label = dynamic_cast<Label *>(scene->getChildByTag(987654));
        if (!label) {
            label = Label::createWithSystemFont("", "Arial", 22,
                Size(980, 620), TextHAlignment::LEFT);
            if (!label) return;
            label->setTag(987654);
            label->setAnchorPoint(Vec2(0, 1));
            label->setPosition(Vec2(15, 620));
            label->setColor(Color3B(0, 255, 60));
            scene->addChild(label, 999999);
        }
        std::string s = "[KZSG3 iOS boot log]\n";
        for (auto &l : g_lines) { s += l; s += "\n"; }
        label->setString(s);
    }
};

static void hud_tick(float) {}

void JSErrorHUD::install(Director *director, JSContext *cx)
{
    if (g_installed) return;
    g_installed = true;
    log("boot: installing HUD");
    // 不再创建调试场景抢占游戏场景: cc.game.run() 的场景在主循环异步创建
    auto updater = HUDUpdater::getInstance();
    director->getScheduler()->scheduleUpdate(updater, 0, false);
    director->getScheduler()->schedule(hud_tick, updater, 0.25f, false, "kzsg3_tick");

    if (cx) {
        JSObject *global = ScriptingCore::getInstance()->getGlobalObject();
        if (global) {
            // 关键修复: 先进入全局 compartment, 否则 cx->global() 为空,
            // JS_DefineFunction -> GetClassPrototype 会在 NULL+0x40 崩溃
            JSAutoCompartment ac(cx, global);
            JS_DefineFunction(cx, global, "log", js_kzsg3_log, 0,
                              JSPROP_READONLY | JSPROP_PERMANENT | JSPROP_ENUMERATE);
            log("boot: JS log() redirected to file/HUD");
        }
    }
}
