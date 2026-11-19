from concurrent.futures import ThreadPoolExecutor
import subprocess, os
CLANG = r"C:\Program Files\LLVM\bin\clang++.exe"
for src in [r"D:\dsh\kzsg3_port\ios_port\Game\Classes\JSErrorHUD.cpp"]:
    rsp = r"D:\dsh\kzsg3_port\obj\app\JSErrorHUD.cpp.rsp"
    r = subprocess.run([CLANG, "@" + rsp.replace("\\","/")], capture_output=True, text=True)
    err = r.stderr
    lines = [l for l in err.splitlines() if ": error:" in l or "fatal" in l]
    print("errors:", len(lines))
    for l in lines[:10]: print("  ", l[-190:])
