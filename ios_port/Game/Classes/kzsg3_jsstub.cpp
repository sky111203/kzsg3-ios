// kzsg3_jsstub.cpp — iOS arm64 预编译 libjs_static 的 ABI 补桩
// 该 SM 构建的个别内部符号未随 .a 导出; 单线程加载场景下返回 false 恒安全。
#include "jsapi.h"

namespace js {
bool OffThreadParsingMustWaitForGC(JSRuntime *rt) { return false; }
}
