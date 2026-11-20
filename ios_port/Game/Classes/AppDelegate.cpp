// -*- Mode: C++; c-basic-offset: 4; tab-width: 4 -*-
//
//  KZSG3-iOS — 狂斩三国3 (Android APK → iOS 移植)
//  AppDelegate.cpp — cocos2d-x JSB 运行时引导 (带屏幕调试 HUD + 文件日志)
//
//  游戏逻辑 100% 来自 APK 内的 SpiderMonkey XDR 字节码, 字节级原样运行。
//  引擎: cocos2d-js v3.0-beta js-bindings (cocos2d-x v3.0, SpiderMonkey 28, arm64)。
//  Android 渠道桥由 KGOperatorBridge.cpp 以"本地直接应答成功"实现。

#include "AppDelegate.h"
#include "cocos2d.h"
#include "ScriptingCore.h"
#include "jsapi.h"
#include "jsb_cocos2dx_auto.hpp"
#include "jsb_cocos2dx_ui_auto.hpp"
#include "jsb_cocos2dx_studio_auto.hpp"
#include "jsb_cocos2dx_builder_auto.hpp"
#include "jsb_cocos2dx_spine_auto.hpp"
#include "jsb_cocos2dx_extension_auto.hpp"
#include "ui/jsb_cocos2dx_ui_manual.h"
#include "cocostudio/jsb_cocos2dx_studio_manual.h"
#include "cocosbuilder/js_bindings_ccbreader.h"
#include "spine/jsb_cocos2dx_spine_manual.h"
#include "extension/jsb_cocos2dx_extension_manual.h"
#include "localstorage/js_bindings_system_registration.h"
#include "chipmunk/js_bindings_chipmunk_registration.h"
#include "jsb_opengl_registration.h"
#include "network/XMLHTTPRequest.h"
#include "network/jsb_websocket.h"
#include "network/jsb_socketio.h"
#include "KGOperatorBridge.h"
#include "JSErrorHUD.h"

USING_NS_CC;
using namespace CocosDenshion;

AppDelegate::AppDelegate()
{
}

AppDelegate::~AppDelegate()
{
    ScriptEngineManager::destroyInstance();
}

bool AppDelegate::applicationDidFinishLaunching()
{
    JSErrorHUD::log("app: didFinishLaunching ENTER");
    auto director = Director::getInstance();
    auto glview = director->getOpenGLView();
    if (!glview) {
        JSErrorHUD::log("boot: creating GLView...");
        glview = GLView::createWithRect("KZSG3", Rect(0, 0, 960, 640));
        director->setOpenGLView(glview);
    }

    JSErrorHUD::log("boot: director+glview ok");
    director->setAnimationInterval(1.0 / 60);

    ScriptingCore *sc = ScriptingCore::getInstance();

    sc->addRegisterCallback(register_all_cocos2dx);
    sc->addRegisterCallback(register_all_cocos2dx_extension);
    sc->addRegisterCallback(register_cocos2dx_js_extensions);
    sc->addRegisterCallback(register_all_cocos2dx_extension_manual);
    sc->addRegisterCallback(jsb_register_chipmunk);
    sc->addRegisterCallback(jsb_register_system);
    sc->addRegisterCallback(JSB_register_opengl);
    sc->addRegisterCallback(register_all_cocos2dx_builder);
    sc->addRegisterCallback(register_CCBuilderReader);
    sc->addRegisterCallback(register_all_cocos2dx_ui);
    sc->addRegisterCallback(register_all_cocos2dx_ui_manual);
    sc->addRegisterCallback(register_all_cocos2dx_studio);
    sc->addRegisterCallback(register_all_cocos2dx_studio_manual);
    sc->addRegisterCallback(register_all_cocos2dx_spine);
    sc->addRegisterCallback(register_all_cocos2dx_spine_manual);
    sc->addRegisterCallback(MinXmlHttpRequest::_js_register);
    sc->addRegisterCallback(register_jsb_websocket);
    sc->addRegisterCallback(register_jsb_socketio);
    sc->addRegisterCallback(register_KG_Operator);

    JSErrorHUD::log("boot: register callbacks queued");
    sc->start();
    JSErrorHUD::log("boot: sc->start() ok");

    // ccs (CocoStudio 2.0) 兼容垫片: beta studio 绑定缺 ActionTimelineCache, JS 桩顶替
    sc->evalString(
        "var ccs = typeof ccs !== 'undefined' ? ccs : {};"
        "if (!ccs.ActionTimelineCache) {"
        " ccs.ActionTimelineCache = function() {"
        "  this.loadActionTimelineFromBuffer = function() { return null; };"
        "  this.loadActionTimelineWithFile = function() { return null; };"
        "  this.loadActionTimeline = function() { return null; };"
        "  this.createActionTimeline = function() { return null; };"
        "  this.bindAnimationOnNode = function() {};"
        " };"
        " ccs.ActionTimelineCache.getInstance = function() {"
        "  if (!ccs.__atcI) ccs.__atcI = new ccs.ActionTimelineCache();"
        "  return ccs.__atcI;"
        " };"
        " ccs.CSLoader = function() {"
        "  this.createNode = function() { return null; };"
        "  this.createNodeFromJson = function() { return null; };"
        "  this.createNodeFromCSB = function() { return null; };"
        "  this.loadScene = function() { return null; };"
        "  this.loadIniFile = function() { return null; };"
        "  this.bindCallback = function() {};"
        " };"
        " ccs.CSLoader.getInstance = function() {"
        "  if (!ccs.__cslI) ccs.__cslI = new ccs.CSLoader();"
        "  return ccs.__cslI;"
        " };"
        " ccs.CSLoader.createNode = function() { return null; };"
        " ccs.ActionTimelineManager = function() {"
        "  this.getActionTimeline = function() { return null; };"
        " };"
        " ccs.ActionTimelineManager.getInstance = function() {"
        "  if (!ccs.__atmI) ccs.__atmI = new ccs.ActionTimelineManager();"
        "  return ccs.__atmI;"
        " };"
        " ccs.ActionTimelineNode = function() {};"
        " ccs.ActionTimelineNode.create = function() { return null; };"
        // 游戏私改 lib 的自定义原生函数
        " var __msgbox = typeof __msgbox !== 'undefined' ? __msgbox : function(m) {"
        "  if (typeof cc !== 'undefined' && cc.log) cc.log('[msgbox] ' + m);"
        " };"
        "}",
        NULL, "ccs_shim.js", NULL);

    // 批量垫片: final SDK 有而 beta 绑定缺失的全部 cc.*/ccs.* 类 (JS 桩)
    sc->evalString(
        "var __kstub = function(n) {\n"
        " var parts = n.split('.');\n"
        " var cur = (typeof globalThis !== 'undefined') ? globalThis : this;\n"
        " for (var i = 0; i < parts.length - 1; i++) {\n"
        "  if (typeof cur[parts[i]] === 'undefined') cur[parts[i]] = {};\n"
        "  cur = cur[parts[i]];\n"
        " }\n"
        " var last = parts[parts.length - 1];\n"
        " if (typeof cur[last] !== 'undefined') return;\n"
        " var f = function() { this.isStub = true; };\n"
        " f.prototype.create = function() { return null; };\n"
        " f.create = function() { return null; };\n"
        " cur[last] = f;\n"
        "}"
        "__kstub('cc.ActionFloat');"
        "__kstub('cc.AmbientLight');"
        "__kstub('cc.AsyncTaskPool');"
        "__kstub('cc.BaseLight');"
        "__kstub('cc.CallFuncN');"
        "__kstub('cc.Camera');"
        "__kstub('cc.CameraBackgroundBrush');"
        "__kstub('cc.CameraBackgroundColorBrush');"
        "__kstub('cc.CameraBackgroundDepthBrush');"
        "__kstub('cc.CameraBackgroundSkyBoxBrush');"
        "__kstub('cc.DirectionLight');"
        "__kstub('cc.GLProgramState');"
        "__kstub('cc.Image');"
        "__kstub('cc.Material');"
        "__kstub('cc.Pass');"
        "__kstub('cc.PointLight');"
        "__kstub('cc.Properties');"
        "__kstub('cc.RenderState');"
        "__kstub('cc.SpotLight');"
        "__kstub('cc.Technique');"
        "__kstub('ccs.ActionTimeline');"
        "__kstub('ccs.ActionTimelineData');"
        "__kstub('ccs.AlphaFrame');"
        "__kstub('ccs.AnchorPointFrame');"
        "__kstub('ccs.AnimationData');"
        "__kstub('ccs.BlendFuncFrame');"
        "__kstub('ccs.BoneNode');"
        "__kstub('ccs.ColorFrame');"
        "__kstub('ccs.ComExtensionData');"
        "__kstub('ccs.ContourData');"
        "__kstub('ccs.EventFrame');"
        "__kstub('ccs.Frame');"
        "__kstub('ccs.InnerActionFrame');"
        "__kstub('ccs.MovementData');"
        "__kstub('ccs.PositionFrame');"
        "__kstub('ccs.RotationFrame');"
        "__kstub('ccs.RotationSkewFrame');"
        "__kstub('ccs.ScaleFrame');"
        "__kstub('ccs.SkeletonNode');"
        "__kstub('ccs.SkewFrame');"
        "__kstub('ccs.TextureData');"
        "__kstub('ccs.TextureFrame');"
        "__kstub('ccs.Timeline');"
        "__kstub('ccs.VisibleFrame');"
        "__kstub('ccs.ZOrderFrame');"
        ,NULL, "stub.js", NULL);
    JSErrorHUD::log("boot: batch stubs installed");

    // UI 命名空间迁移: beta 把 UI 类挂在全局根或 cc 下, 正式版在 ccui 下 → 三路兜底别名
    sc->evalString(
        "var ccui = typeof ccui !== 'undefined' ? ccui : {};"
        // EditBox: beta 引擎无原生 EditBox, 用 JS 桩 (文本输入功能受限但启动可用)
        "if (typeof ccui.EditBox === 'undefined') {"
        " ccui.EditBox = function() { this._stub = true; };"
        " ccui.EditBox.prototype.initWithSizeAndBackgroundImage = function() { return true; };"
        " ccui.EditBox.prototype.setText = function() {};"
        " ccui.EditBox.prototype.getText = function() { return ''; };"
        " ccui.EditBox.prototype.setPlaceHolder = function() {};"
        " ccui.EditBox.prototype.setPlaceholderFont = function() {};"
        " ccui.EditBox.prototype.setPlaceholderFontSize = function() {};"
        " ccui.EditBox.prototype.setPlaceholderFontColor = function() {};"
        " ccui.EditBox.prototype.setFontSize = function() {};"
        " ccui.EditBox.prototype.setFontColor = function() {};"
        " ccui.EditBox.prototype.setMaxLength = function() {};"
        " ccui.EditBox.prototype.setInputMode = function() {};"
        " ccui.EditBox.prototype.setInputFlag = function() {};"
        " ccui.EditBox.prototype.setReturnType = function() {};"
        " ccui.EditBox.prototype.setDelegate = function() {};"
        " ccui.EditBox.prototype.registerScriptEditBoxHandler = function() {};"
        " ccui.EditBox.prototype.unregisterScriptEditBoxHandler = function() {};"
        " ccui.EditBox.prototype.setPosition = function() {};"
        " ccui.EditBox.prototype.setVisible = function() {};"
        " ccui.EditBox.prototype.create = function() { return null; };"
        "}"
        "var __uialias = ['Scale9Sprite','Button','CheckBox','ImageView','Layout','ListView','LoadingBar','PageView','ScrollView','Slider','Text','TextAtlas','TextBMFont','TextField','Widget','RichText','Helper','LayoutParameter','LinearLayoutParameter','RelativeLayoutParameter','RichElement','RichElementImage','RichElementText','RichElementCustomNode'];"
        "for (var i = 0; i < __uialias.length; i++) {"
        " var n = __uialias[i];"
        " if (typeof ccui[n] !== 'undefined') continue;"
        " var src = null;"
        " try { if (typeof this[n] !== 'undefined') src = this[n]; } catch (e) {}"
        " if (src === null && typeof cc !== 'undefined' && typeof cc[n] !== 'undefined') src = cc[n];"
        " if (src === null && typeof ccs !== 'undefined' && typeof ccs[n] !== 'undefined') src = ccs[n];"
        " if (src !== null) ccui[n] = src;"
        "}"
        // ControlButton 别名 (beta 里叫 Control)
        "try { if (typeof cc !== 'undefined' && typeof cc.ControlButton === 'undefined' && typeof cc.Control !== 'undefined') cc.ControlButton = cc.Control; } catch (e) {}"
        ,NULL, "uialias.js", NULL);
    JSErrorHUD::log("boot: ccui aliases installed");
    JSErrorHUD::log("boot: ccs shim installed");

    JSContext *cx = sc->getGlobalContext();
    JSErrorHUD::setErrorReporter(cx);   // JS 编译/执行错误全部上屏
    JSErrorHUD::log("boot: searchPaths:");
    for (auto &p : FileUtils::getInstance()->getSearchPaths())
        JSErrorHUD::log("  path: " + p);
    JSErrorHUD::log("  writable: " + FileUtils::getInstance()->getWritablePath());

    // 尽早装 HUD (调试场景兜底), JS 启动各阶段失败都能在屏幕看到
    JSErrorHUD::install(director, cx);

    // 启动序列与原包 lib 固化一致
    JSErrorHUD::log("boot: main.js at: " + FileUtils::getInstance()->fullPathForFilename("main.js"));
    JSErrorHUD::log("boot: run script/jsb_boot.js");
    bool rb = sc->runScript("script/jsb_boot.js");
    JSErrorHUD::log(std::string("boot: jsb_boot rc=") + (rb ? "true" : "false"));
    JSErrorHUD::drainJSException(cx, "jsb_boot.js");
    JSErrorHUD::log("boot: jsb_boot done");

    ScriptEngineProtocol *engine = ScriptingCore::getInstance();
    ScriptEngineManager::getInstance()->setScriptEngine(engine);

    JSErrorHUD::log("boot: run main.js");
    bool rm = sc->runScript("main.js");
    JSErrorHUD::drainJSException(cx, "main.js");
    JSErrorHUD::log(std::string("boot: main.js rc=") + (rm ? "true" : "false"));
    JSErrorHUD::log("boot: main.js done");

    // 若 JS 已建好场景, HUD 自动叠加到其上
    JSErrorHUD::install(director, cx);

    return true;
}

void AppDelegate::applicationDidEnterBackground()
{
    auto director = Director::getInstance();
    director->stopAnimation();
    director->getEventDispatcher()->dispatchCustomEvent("game_on_hide");
    SimpleAudioEngine::getInstance()->pauseBackgroundMusic();
    SimpleAudioEngine::getInstance()->pauseAllEffects();
}

void AppDelegate::applicationWillEnterForeground()
{
    auto director = Director::getInstance();
    director->startAnimation();
    director->getEventDispatcher()->dispatchCustomEvent("game_on_show");
    SimpleAudioEngine::getInstance()->resumeBackgroundMusic();
    SimpleAudioEngine::getInstance()->resumeAllEffects();
}
