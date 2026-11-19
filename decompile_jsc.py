# -*- coding: utf-8 -*-
"""SM28 XDR .jsc -> readable JS via mozjs-28.dll. Run with 32-bit python only."""
import ctypes, os, sys, struct

DLL = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\win32\mozjs-28.dll"
OUT = r"D:\dsh\kzsg3_port\js_dump"
ROOTS = [r"D:\dsh\kzsg3_port\apk_extracted\assets"]

k32 = ctypes.windll.kernel32
MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE = 0x1000, 0x2000, 0x40

def make_thiscall(target):
    """cdecl(callable thunk)(this, arg2, ...) -> invokes MSVC thiscall target."""
    addr = k32.VirtualAlloc(None, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    code = b"\x5A\x59\x52" + b"\xB8" + struct.pack("<I", target) + b"\xFF\xD0\xC3"
    ctypes.memmove(addr, code, len(code))
    return ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(addr)

def make_thiscall_void(target):
    addr = k32.VirtualAlloc(None, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    code = b"\x5A\x59\x52" + b"\xB8" + struct.pack("<I", target) + b"\xFF\xD0\xC3"
    ctypes.memmove(addr, code, len(code))
    return ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)(addr)

js = ctypes.CDLL(DLL)

f_init = getattr(js, "?JS_Init@@YA_NXZ"); f_init.restype = ctypes.c_bool
f_newrt = getattr(js, "?JS_NewRuntime@@YAPAUJSRuntime@@IW4JSUseHelperThreads@@@Z"); f_newrt.restype = ctypes.c_void_p
f_newctx = getattr(js, "?JS_NewContext@@YAPAUJSContext@@PAUJSRuntime@@I@Z"); f_newctx.restype = ctypes.c_void_p
f_dec = getattr(js, "?JS_DecodeScript@@YAPAVJSScript@@PAUJSContext@@PBXIPAUJSPrincipals@@2@Z"); f_dec.restype = ctypes.c_void_p
f_decomp = getattr(js, "?JS_DecompileScript@@YAPAVJSString@@PAUJSContext@@PAVJSScript@@PBDI@Z"); f_decomp.restype = ctypes.c_void_p
f_str2c = getattr(js, "?JS_GetStringCharsZAndLength@@YAPBGPAUJSContext@@PAVJSString@@PAI@Z"); f_str2c.restype = ctypes.POINTER(ctypes.c_uint16); f_str2c.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
f_desctx = getattr(js, "?JS_DestroyContext@@YAXPAUJSContext@@@Z")
f_desrt = getattr(js, "?JS_DestroyRuntime@@YAXPAUJSRuntime@@@Z")
f_isexc = getattr(js, "?JS_IsExceptionPending@@YA_NPAUJSContext@@@Z"); f_isexc.restype = ctypes.c_bool
f_excrep = getattr(js, "?JS_ReportPendingException@@YA_NPAUJSContext@@@Z"); f_excrep.restype = ctypes.c_bool
f_excclear = getattr(js, "?JS_ClearPendingException@@YAXPAUJSContext@@@Z")
f_newglob = getattr(js, "?JS_NewGlobalObject@@YAPAVJSObject@@PAUJSContext@@PBUJSClass@@PAUJSPrincipals@@W4OnNewGlobalHookOption@JS@@ABVCompartmentOptions@6@@Z"); f_newglob.restype = ctypes.c_void_p
f_initstd = getattr(js, "?JS_InitStandardClasses@@YA_NPAUJSContext@@PAVJSObject@@@Z"); f_initstd.restype = ctypes.c_bool

COPT_CTOR_ADDR = ctypes.cast(getattr(js, "??0CompartmentOptions@JS@@QAE@XZ"), ctypes.c_void_p).value
ACC_CTOR_ADDR = ctypes.cast(getattr(js, "??0JSAutoCompartment@@QAE@PAUJSContext@@PAVJSObject@@@Z"), ctypes.c_void_p).value
ACC_DTOR_ADDR = ctypes.cast(getattr(js, "??1JSAutoCompartment@@QAE@XZ"), ctypes.c_void_p).value
copt_ctor = make_thiscall(COPT_CTOR_ADDR)
acc_ctor = make_thiscall(ACC_CTOR_ADDR)
acc_dtor = make_thiscall_void(ACC_DTOR_ADDR)

# ---- JSClass (SM28 layout, 32-bit) ----
STUB6 = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
VOID4 = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
_stub_true = STUB6(lambda *a: True)
_stub_void = VOID4(lambda *a: None)
_ptrs = ctypes.cast(_stub_true, ctypes.c_void_p).value
_ptrs_void = ctypes.cast(_stub_void, ctypes.c_void_p).value
name_buf = ctypes.create_string_buffer(b"global")
JSCLASS_IS_GLOBAL = 1 << 17
SLOT_COUNT = 3 + 40 * 3 + 27
FLAGS = JSCLASS_IS_GLOBAL | (SLOT_COUNT << 8)

class JSClass(ctypes.Structure):
    _fields_ = [("name", ctypes.c_void_p), ("flags", ctypes.c_uint32),
                ("ops", ctypes.c_void_p * 13),
                ("reserved", ctypes.c_void_p * 42)]

clasp = JSClass()
clasp.name = ctypes.cast(name_buf, ctypes.c_void_p).value
clasp.flags = FLAGS
for i in range(7):
    clasp.ops[i] = _ptrs          # add, del, get, set, enumerate, resolve, convert
for i in range(7, 13):
    clasp.ops[i] = None           # finalize, checkAccess, call, hasInstance, construct, trace

def jsstring_to_py(cx, s):
    if not s:
        return None
    ln = ctypes.c_size_t(0)
    chars = f_str2c(cx, s, ctypes.byref(ln))
    if not chars:
        return None
    return "".join(map(chr, chars[:ln.value]))

def main():
    files = []
    for root in ROOTS:
        for dp, _, fl in os.walk(root):
            for f in fl:
                if f.endswith(".jsc"):
                    files.append(os.path.join(dp, f))
    print("jsc files:", len(files))
    if not f_init():
        print("JS_Init failed"); sys.exit(1)
    rt = f_newrt(1024 * 1024 * 1024, 0)
    f_setgc = getattr(js, "?JS_SetGCParameter@@YAXPAUJSRuntime@@W4JSGCParamKey@@I@Z")
    f_setgc(rt, 0, 0xF0000000)   # JSGC_MAX_BYTES -> 3.75GB, effectively no GC
    cx = f_newctx(rt, 8192)
    copts = ctypes.create_string_buffer(64)
    copt_ctor(copts, None)
    glob = f_newglob(cx, ctypes.byref(clasp), None, 1, copts)
    print("global:", hex(glob or 0))
    if not glob:
        print("JS_NewGlobalObject failed"); sys.exit(1)
    gslot = ctypes.c_void_p(glob)
    f_enter = getattr(js, "?JS_EnterCompartment@@YAPAUJSCompartment@@PAUJSContext@@PAVJSObject@@@Z"); f_enter.restype = ctypes.c_void_p
    f_leave = getattr(js, "?JS_LeaveCompartment@@YAXPAUJSContext@@PAUJSCompartment@@@Z")
    oldc = f_enter(cx, glob)
    ac = None  # not used

    ok, fail = 0, []
    for p in files:
        data = open(p, "rb").read()
        if len(data) < 20 or data[:4] != bytes([0x42, 0xC0, 0x73, 0xB9]):
            fail.append((p, "bad magic")); continue
        rel = os.path.relpath(p, ROOTS[0])
        outp = os.path.join(OUT, rel[:-4] + ".js")
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        buf = ctypes.create_string_buffer(data, len(data))
        script = f_dec(cx, buf, len(data), None, None)
        if not script:
            if f_isexc(cx): f_excclear(cx)
            fail.append((p, "decode failed")); continue
        s = f_decomp(cx, script, rel.encode(), 0)
        if not s:
            if f_isexc(cx): f_excclear(cx)
            fail.append((p, "decompile failed")); continue
        txt = jsstring_to_py(cx, s)
        if txt is None:
            fail.append((p, "string failed")); continue
        open(outp, "w", encoding="utf-8", errors="replace").write(txt)
        ok += 1

    f_leave(cx, oldc)
    f_desctx(cx)
    f_desrt(rt)
    print("decompiled:", ok, "failed:", len(fail))
    for p, e in fail[:30]:
        print("  FAIL", os.path.relpath(p, ROOTS[0]), e)

main()



