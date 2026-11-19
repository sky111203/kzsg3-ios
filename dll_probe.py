import ctypes
dll = ctypes.CDLL(r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\win32\mozjs-28.dll")
names = ["JS_Init","JS_ShutDown","JS_NewRuntime","JS_NewContext","JS_DecodeScript","JS_DecompileScript","JS_GetStringCharsZAndLength","js_Init","JS_StartEngine","JS_InitStandardClasses","JS_NewGlobalObject","JS_DestroyRuntime","JS_DestroyContext","JS_ReportPendingException","JS_ClearPendingException","JS_IsExceptionPending","JS_GetPendingException","JS_ExceptionStringRepresentation"]
import struct
for n in names:
    try:
        f = getattr(dll, n)
        print("OK  ", n)
    except AttributeError:
        print("MISS", n)
