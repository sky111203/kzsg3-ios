t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
i = t.find("XMLHTTPRequest.cpp")
seg = t[i:i+2600]
print(seg)
