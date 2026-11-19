import sys
sys.path.insert(0, r"D:\dsh\kzsg3_port\ios_port\tools")
import tbd_fix, os
p = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk\System\Library\Frameworks\UIKit.framework\UIKit.tbd"
print("exists:", os.path.isfile(p))
t = open(p, encoding="utf-8", errors="replace").read()
i = t.find("re-exports")
print("re-exports idx:", i)
print(t[max(0,i-80):i+400])
