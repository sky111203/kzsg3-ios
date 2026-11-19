import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
# find blocks for the four js files and extract only 'error:' lines
for name in ["XMLHTTPRequest.cpp", "jsb_websocket.cpp", "js_bindings_system_functions.cpp", "js_bindings_system_registration.cpp"]:
    i = t.find("==== ")
    blocks = re.split(r"==== (D:[^\n]+)", t)
    # blocks: ['', path, body, path, body...]
    for j in range(1, len(blocks), 2):
        p, body = blocks[j], blocks[j+1]
        if p.endswith(name):
            errs = [l for l in body.splitlines() if ": error:" in l]
            print("=====", name, "errors:", len(errs))
            for e in errs[:6]:
                print("   ", e[:180])
