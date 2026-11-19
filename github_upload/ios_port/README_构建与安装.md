# 狂斩三国3 — Android APK → iOS 移植包

把《狂斩三国3》Android 破解版 APK 的**完整游戏逻辑**原样搬到 iOS 上运行。

## ✅ 已直出未签名 IPA

`out/KZSG3-ios-arm64-unsigned.ipa`（约 54MB，arm64，iOS 12+，未签名）

在 **Windows 本机**直接交叉编译生成（不需要 Mac）：

```
tools/extract_build_spec.py   # 从引擎 pbxproj 提取 397 个编译单元 + 编译参数
tools/crossbuild.py           # clang -target arm64-apple-ios 全量编译(并行, 增量)
tools/link_ipa.py             # lld 链接 + 组装 Payload/KZSG3.app + 打包 IPA
```

前置条件（本机已装好）：
1. LLVM（clang + ld64.lld）：`winget install LLVM.LLVM`
2. iPhoneOS SDK：`https://github.com/theos/sdks/releases/latest/download/iPhoneOS16.5.sdk.tar.xz` 解压到 `D:\dsh\kzsg3_port\sdk\`（脚本中的路径常量按需修改）
3. cocos2d-js v3.0-beta 引擎包：`http://cdn.cocos2d-x.org/cocos2d-js-v3.0-beta.zip` 解压到 `D:\dsh\kzsg3_port\enginejs\`
4. Python + Pillow（图标生成）

一条龙：
```bash
python tools/extract_build_spec.py
python tools/crossbuild.py
python tools/link_ipa.py
```

引擎补丁已内建（脚本幂等）：CCRefPtr.h nullptr 比较、AssetsManager system() 调用、
jsbindings pluginx 死代码剔除、libjs_static.arm64 缺失符号补桩（kzsg3_jsstub.cpp）。

## 签名安装（拿到 IPA 后一步）

用 **Sideloadly**（sideloadly.io，Windows 直接装）：
1. 手机连电脑，打开 Sideloadly
2. 拖入 `KZSG3-ios-arm64-unsigned.ipa`
3. 填 Apple ID（免费账号即可）→ Start
4. 手机上：设置 → 通用 → VPN与设备管理 → 信任开发者证书 → 打开游戏

其他方式：AltStore / 爱思助手自签名 / TrollStore（iOS 14.0–16.7.1 永久签名）。

---

## 移植原理（为什么功能逻辑不变）

对 APK 的逆向结论：

| 项 | 结论 |
|---|---|
| 引擎 | cocos2d-x v3.0 血统 JSB（Cocos2d-JS v3.0-beta 时代），SpiderMonkey 28 |
| 游戏逻辑 | 全部在 **228 个 .jsc 文件**（SpiderMonkey XDR 字节码，未加密：首 4 字节 `42 C0 73 B9` = SM 官方 XDR_BYTECODE_VERSION） |
| 资源 | `res/`（图集 plist/png、CocoStudio ExportJson 骨骼动画、fnt 位图字体、TTF） |
| 音频 | `res/sound/*.ogg` → 已转码为 WAV 内容（保留 .ogg 文件名，iOS AVAudioPlayer 按内容解码，JS 零改动） |
| 渠道桥 | JS 调 `KG::Operator::RequestChannel(module, method, args, callback)` → iOS 侧由 `KGOperatorBridge.cpp` 本地直接应答成功（**保持破解版免费购买行为**） |
| 平台分支 | 包内自带 `src/ios/define/*.jsc`，`main.jsc` 用 `sys.OS_IOS` 分支 → iOS 路径本来就存在 |

**验证**：用引擎自带的 SpiderMonkey 对包内全部 228 个 .jsc 解码，**228/228 全部成功**，字节码与运行时完全兼容。iOS 端不改一个字节、不改一行 JS 逻辑。

## 目录结构

```
ios_port/
├── Game/
│   ├── KZSG3.xcodeproj/        Xcode 工程（由 tools/assemble_project.py 从模板生成）
│   ├── Classes/
│   │   ├── AppDelegate.cpp/h   JSB 引导: 注册绑定 → script/jsb_boot.js → main.js（与原包一致）
│   │   └── KGOperatorBridge.cpp/h  koogame 渠道桥 iOS 本地实现
│   ├── ios/                    AppController / RootViewController / Info.plist / 图标 / 启动图
│   ├── mac/                    (Mac target 文件, 仅保证工程可打开)
│   └── Resources/              游戏资源: main.jsc + script/ + src/ + res/（来自 APK 原样）
├── engine/                     cocos2d-js v3.0-beta 的 js-bindings（assemble 脚本自动拷贝）
├── tools/
│   ├── assemble_project.py     一键组装（本地/CI 通用，相对路径）
│   ├── stage_assets.py         从 APK 抽取资源并转码音频（需已解包 APK）
│   └── app_icon.png            应用图标源图
└── build/
    ├── build_ipa.yml           GitHub Actions 云端构建工作流
    ├── build_mac.sh            macOS 本地构建脚本
    └── entitlements.plist      签名 entitlements
```

## 构建路线 A：GitHub Actions 云端出包（无 Mac 也能出）

1. 把整个 `ios_port/` 推到一个 GitHub 仓库（`Game/Resources/` 必须包含在内；`engine/` 不用推，CI 会自动下载引擎，可在 `.gitignore` 里忽略它）：

   .gitignore 建议：
   ```
   ios_port/engine/
   ios_port/Game/bld/
   ios_port/Game/Payload/
   ```

2. 仓库 → Actions → 选 "Build KZSG3 iOS IPA (unsigned)" → Run workflow。
3. 跑完下载 artifact `KZSG3-ios-arm64-unsigned` → 得到**未签名 IPA**。
4. 转到下面"签名与安装"。

## 构建路线 B：本地 Mac

```bash
./build/build_mac.sh          # 产出 Game/KZSG3-ios-arm64.ipa（未签名）
# 有开发者身份时:
./build/build_mac.sh "Apple Development: 你的名字 (XXXXXXXX)"
```

## 签名与安装（Windows 上就能做）

未签名 IPA 需要"自签"后才能装进手机（免费 Apple ID 7 天有效，付费开发者账号 1 年）：

| 方式 | 适用 | 说明 |
|---|---|---|
| **Sideloadly**（推荐） | Windows/macOS | 官网 sideloadly.io；手机连电脑 → 拖入 IPA → 填 Apple ID → Start。免费账号需在 设置→通用→VPN与设备管理 里信任证书 |
| **AltStore** | Windows/macOS | 装 AltServer，手机装 AltStore，通过 AltStore 打开 IPA 安装，7 天自动续签 |
| **爱思助手** | Windows | 工具箱 → 自签名安装，流程与 Sideloadly 类似 |
| **TrollStore** | iOS 14.0–16.7.1（含 15.x 全部） | 永久签名免续签，直接把 IPA 用 TrollStore 打开安装 |

> 真机要求：iPhone（arm64），系统建议 iOS 12–17；iPad 也可装（工程含 iPad 目标）。

## 游戏运行说明

- 首屏会播放漫画 + 主界面，横屏模式。
- **商店/充值/VIP**：渠道桥本地应答成功，等价于原破解版的免费购买效果。
- **网络对战/好友/排行榜**：原服务器早已停服，这些功能会请求超时后按原逻辑失败，不影响单机主线。
- 存档通过 localStorage 存在 App 沙盒里。

## 常见构建问题

CI/本地构建若报错，按下面顺序处理（引擎是 2014 年代码，现代 Xcode 需要少量适配）：

| 报错特征 | 修复 |
|---|---|
| `error: use of undeclared identifier 'xxx'`（头文件） | 在 Game/KZSG3.xcodeproj 的 iOS target `USER_HEADER_SEARCH_PATHS` 补对应路径（引擎头都在 `ios_port/engine/js-bindings/` 下） |
| `'register' storage class` / `std::auto_ptr` 报错 | 保持 `CLANG_CXX_LANGUAGE_STANDARD = gnu++11`（工程已设），若被覆盖改回 |
| 链接缺 curl/jpeg/png 符号 | 工程已用 `OTHER_LDFLAGS[arch=arm64]` 自动切 `_arm64` 库；确认构建用了 `ARCHS=arm64` |
| `libjs_static.a` 架构不符 | jsbindings 工程会按 `OTHER_LDFLAGS[arch=arm64]` 取 `libjs_static.arm64.a`，同样确认 `ARCHS=arm64` |
| 老式 ObjC（release/dealloc）报 ARC 错 | 工程未开 ARC，直接用模板配置即可；若手工新建工程需 `CLANG_ENABLE_OBJC_ARC = NO` |
| Xcode 报 missing Development Team | 未签名构建传 `CODE_SIGNING_ALLOWED=NO`（脚本已带） |

## 重新生成工程（改了资源/类之后）

```bash
python3 tools/assemble_project.py   # 幂等：每次都从模板+引擎重新生成 pbxproj/图标/plist
```

`Game/Classes/` 下的代码是手写层，assemble 不会覆盖它。
