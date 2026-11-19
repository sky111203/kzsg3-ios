t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
print("len:", len(t))
i = t.rfind("====")
print(t[i:i+1200])
