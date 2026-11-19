import zipfile
z = zipfile.ZipFile(r"D:\dsh\kzsg3_port\out\KZSG3-ios-arm64-unsigned.ipa")
names = z.namelist()
app = [n for n in names if n.startswith("Payload/KZSG3.app/")]
print("entries:", len(names))
def has(rel): return any(n == "Payload/KZSG3.app/" + rel for n in names)
for probe in ["Info.plist", "PkgInfo", "KZSG3", "main.jsc", "script/jsb_boot.jsc", "src/GameLayer.jsc",
              "res/config/shopConfigIOS.json", "res/sound/mainTheme.ogg", "Icon-120.png"]:
    print(has(probe), probe)
sizes = sum(i.file_size for i in z.infolist())
print("uncompressed total MB:", round(sizes/1048576, 1))
