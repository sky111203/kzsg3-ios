from PIL import Image
import os, json, shutil
src = r"D:\dsh\kzsg3_port\apk_extracted\res\drawable-hdpi-v4\icon.png"
outdir = r"D:\dsh\kzsg3_port\ios_port\Game\ios\Icons"
xcdir = r"D:\dsh\kzsg3_port\ios_port\Game\ios\Assets.xcassets\AppIcon.appiconset"
os.makedirs(outdir, exist_ok=True)
os.makedirs(xcdir, exist_ok=True)
img = Image.open(src).convert("RGBA")
sizes = {
 "icon-20@2x.png":40, "icon-20@3x.png":60, "icon-29.png":29, "icon-29@2x.png":58, "icon-29@3x.png":87,
 "icon-40@2x.png":80, "icon-40@3x.png":120, "icon-60@2x.png":120, "icon-60@3x.png":180,
 "icon-76.png":76, "icon-76@2x.png":152, "icon-83.5@2x.png":167, "icon-1024.png":1024,
}
for name, px in sizes.items():
    img.resize((px,px), Image.LANCZOS).save(os.path.join(outdir, name))
def E(f, idiom, size, scale):
    return {"filename": f, "idiom": idiom, "scale": scale, "size": size}
contents = {"images": [
 E("icon-40@2x.png","iphone","20x20","2x"), E("icon-20@3x.png","iphone","20x20","3x"),
 E("icon-29.png","iphone","29x29","1x"), E("icon-29@2x.png","iphone","29x29","2x"), E("icon-29@3x.png","iphone","29x29","3x"),
 E("icon-40@2x.png","iphone","40x40","2x"), E("icon-40@3x.png","iphone","40x40","3x"),
 E("icon-60@2x.png","iphone","60x60","2x"), E("icon-60@3x.png","iphone","60x60","3x"),
 E("icon-29.png","ipad","29x29","1x"), E("icon-29@2x.png","ipad","29x29","2x"),
 E("icon-40@2x.png","ipad","40x40","2x"), E("icon-40@3x.png","ipad","40x40","3x"),
 E("icon-76.png","ipad","76x76","1x"), E("icon-76@2x.png","ipad","76x76","2x"),
 E("icon-83.5@2x.png","ipad","83.5x83.5","2x"),
 E("icon-1024.png","ios-marketing","1024x1024","1x"),
], "info": {"author": "xcode", "version": 1}}
for e in contents["images"]:
    shutil.copyfile(os.path.join(outdir, e["filename"]), os.path.join(xcdir, e["filename"]))
json.dump(contents, open(os.path.join(xcdir, "Contents.json"), "w"), indent=2)
json.dump({"info":{"author":"xcode","version":1}}, open(r"D:\dsh\kzsg3_port\ios_port\Game\ios\Assets.xcassets\Contents.json","w"), indent=2)
print("icons done:", len(contents["images"]))
