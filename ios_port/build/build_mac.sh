#!/bin/bash
# KZSG3 iOS 本地构建脚本 (macOS)
# 用法:
#   ./build_mac.sh                  # 生成未签名 IPA
#   ./build_mac.sh identity_name    # 用指定签名身份签名 (codesign), 需已配置描述文件
set -e
cd "$(dirname "$0")/.."          # -> ios_port/

# 1) 引擎: 优先使用环境变量 COCOS2D_JS_ROOT, 否则下载
if [ -z "$COCOS2D_JS_ROOT" ]; then
  if [ ! -d ../enginejs/cocos2d-js-v3.0-beta ]; then
    echo "==> downloading cocos2d-js v3.0-beta engine bundle ..."
    curl -L --retry 3 -o /tmp/cocos2d-js.zip "http://cdn.cocos2d-x.org/cocos2d-js-v3.0-beta.zip"
    mkdir -p ../enginejs && (cd ../enginejs && unzip -q /tmp/cocos2d-js.zip)
  fi
  export COCOS2D_JS_ROOT="$(cd ../enginejs/cocos2d-js-v3.0-beta && pwd)"
fi

# 2) 组装工程 (引擎拷贝 + pbxproj + 图标)
python3 tools/assemble_project.py

# 3) 构建
cd Game
xcodebuild -project KZSG3.xcodeproj \
           -target "KZSG3 iOS" \
           -configuration Release \
           -sdk iphoneos \
           ARCHS=arm64 ONLY_ACTIVE_ARCH=NO ENABLE_BITCODE=NO \
           CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" \
           SYMROOT="$(pwd)/bld" build

# 4) 打包 IPA
APP=$(find bld -maxdepth 3 -name "*.app" | head -1)
rm -rf Payload && mkdir Payload && cp -R "$APP" Payload/
if [ -n "$1" ]; then
  echo "==> codesign with: $1"
  codesign --force --deep --sign "$1" --entitlements ../build/entitlements.plist Payload/*.app
fi
zip -qry KZSG3-ios-arm64.ipa Payload
echo "==> done: $(pwd)/KZSG3-ios-arm64.ipa"
