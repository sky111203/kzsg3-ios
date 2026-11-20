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

    JSContext *cx = sc->getGlobalContext();
    JSErrorHUD::log("boot: searchPaths:");
    for (auto &p : FileUtils::getInstance()->getSearchPaths())
        JSErrorHUD::log("  path: " + p);
    JSErrorHUD::log("  writable: " + FileUtils::getInstance()->getWritablePath());

    // 尽早装 HUD (调试场景兜底), JS 启动各阶段失败都能在屏幕看到
    JSErrorHUD::install(director, cx);

    // 启动序列与原包 lib 固化一致
    JSErrorHUD::log("boot: run script/jsb_boot.js");
    sc->runScript("script/jsb_boot.js");
    JSErrorHUD::drainJSException(cx, "jsb_boot.js");
    JSErrorHUD::log("boot: jsb_boot done");

    ScriptEngineProtocol *engine = ScriptingCore::getInstance();
    ScriptEngineManager::getInstance()->setScriptEngine(engine);

    JSErrorHUD::log("boot: run main.js");
    sc->runScript("main.js");
    JSErrorHUD::drainJSException(cx, "main.js");
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
