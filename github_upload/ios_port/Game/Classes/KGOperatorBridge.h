#ifndef __KG_OPERATOR_BRIDGE_H__
#define __KG_OPERATOR_BRIDGE_H__

#include "jsapi.h"

// koogame 渠道桥 iOS 本地实现 — 注册入口
// 在 ScriptingCore 启动序列里以 addRegisterCallback(register_KG_Operator) 挂载
void register_KG_Operator(JSContext *cx, JSObject *global);

#endif
