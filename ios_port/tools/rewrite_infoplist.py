# -*- coding: utf-8 -*-
"""CI 用: 用完整版 Info.plist 覆盖模板 (TrollStore 注册所需全部字段)"""
import plistlib, os

pl = {
    "CFBundleDevelopmentRegion": "zh_CN",
    "CFBundleDisplayName": "狂斩三国3",
    "CFBundleExecutable": "KZSG3 iOS",
    "CFBundleIcons": {"CFBundlePrimaryIcon": {"CFBundleIconFiles": [
        "Icon-29", "Icon-40", "Icon-57", "Icon-58", "Icon-72", "Icon-76",
        "Icon-80", "Icon-100", "Icon-114", "Icon-120", "Icon-144", "Icon-152"]}},
    "CFBundleIdentifier": "com.kzsg3.sanguo3",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "KZSG3 iOS",
    "CFBundlePackageType": "APPL",
    "CFBundleShortVersionString": "1.0.5",
    "CFBundleVersion": "1.0.5",
    "LSRequiresIPhoneOS": True,
    "MinimumOSVersion": "12.0",
    "UIRequiredDeviceCapabilities": ["arm64"],
    "UIStatusBarHidden": True,
    "UISupportedInterfaceOrientations": [
        "UIInterfaceOrientationLandscapeRight",
        "UIInterfaceOrientationLandscapeLeft"],
    "UIFileSharingEnabled": True,
}

dst = os.path.join("Game", "ios", "Info.plist")
with open(dst, "wb") as f:
    plistlib.dump(pl, f)
print("Info.plist rewritten ->", dst)
