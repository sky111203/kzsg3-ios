// JSErrorHUD.h — 启动诊断: 屏幕日志 + 文件日志 + JS 异常捕获
#ifndef __JS_ERROR_HUD_H__
#define __JS_ERROR_HUD_H__

#include "cocos2d.h"
#include "jsapi.h"
#include <string>

class JSErrorHUD
{
public:
    // 追加一行日志(屏幕缓冲 + Documents/kzsg3_log.txt)
    static void log(const std::string &line);
    // 若 JS 有未决异常, 取出并记录
    static void drainJSException(JSContext *cx, const std::string &where);
    // 若无运行场景则建调试场景, 否则叠加 HUD; 并挂帧刷新 + 注册 JS log 重定向
    static void install(cocos2d::Director *director, JSContext *cx);
};

#endif
