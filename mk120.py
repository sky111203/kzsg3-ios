from PIL import Image
img = Image.open(r"D:\dsh\kzsg3_port\ios_port\tools\app_icon.png").convert("RGBA")
img.resize((120,120), Image.LANCZOS).save(r"D:\dsh\kzsg3_port\ios_port\Game\ios\Icon-120.png")
print("ok")
