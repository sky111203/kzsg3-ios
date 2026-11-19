import plistlib
p = r"D:\dsh\kzsg3_port\ios_port\Game\ios\Info.plist"
pl = plistlib.load(open(p, "rb"))
print("DisplayName:", pl["CFBundleDisplayName"])
print("Identifier:", pl["CFBundleIdentifier"])
print("Version:", pl["CFBundleVersion"], pl.get("CFBundleShortVersionString"))
print("ATS:", pl.get("NSAppTransportSecurity"))
print("Caps:", pl.get("UIRequiredDeviceCapabilities"))
