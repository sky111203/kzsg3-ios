# -*- coding: utf-8 -*-
"""
Stage assets from the extracted APK into the iOS Resources bundle.
- Copies main.jsc / script/ / src/ / res/ byte-for-byte (SM24 XDR bytecode runs as-is)
- Converts res/sound/*.ogg -> PCM WAV content, KEEPS .ogg filename
  (iOS AVAudioPlayer decodes by content; JS keeps calling .ogg paths untouched)
- Drops Android-channel-only resource dirs (unicom SDK etc.)
- Extracts app icon candidates from APK res/
"""
import os, sys, shutil, subprocess, hashlib

FFMPEG = r"D:\python3.12\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"
SRC = r"D:\dsh\kzsg3_port\apk_extracted\assets"
DST = r"D:\dsh\kzsg3_port\ios_port\Game\Resources"
APK_RES = r"D:\dsh\kzsg3_port\apk_extracted\res"

SKIP_TOP = {"x86", "UnicomConsume", "unicom_account", "unicom_base"}

def copy_tree():
    n = 0
    for entry in os.listdir(SRC):
        if entry in SKIP_TOP:
            continue
        s = os.path.join(SRC, entry)
        d = os.path.join(DST, entry)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
            n += sum(len(f) for _, _, f in os.walk(d))
        else:
            shutil.copy2(s, d)
            n += 1
    return n

def convert_audio():
    snd = os.path.join(DST, "res", "sound")
    conv, fail = 0, []
    for f in os.listdir(snd):
        if not f.lower().endswith(".ogg"):
            continue
        p = os.path.join(snd, f)
        tmp = p + ".wav"
        r = subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", p,
                            "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", tmp],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(tmp):
            os.replace(tmp, p)   # keep .ogg filename, WAV content inside
            conv += 1
        else:
            fail.append((f, r.stderr.decode("utf-8", "replace")[:120]))
    return conv, fail

def find_icons():
    icons = []
    for dp, _, fn in os.walk(APK_RES):
        for f in fn:
            if "icon" in f.lower() and f.lower().endswith(".png"):
                icons.append(os.path.join(dp, f))
    icons.sort(key=lambda p: os.path.getsize(p), reverse=True)
    return icons[:6]

if __name__ == "__main__":
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(DST, exist_ok=True)
    n = copy_tree()
    print(f"staged {n} files")
    conv, fail = convert_audio()
    print(f"audio converted: {conv}, failed: {len(fail)}")
    for f, e in fail[:10]:
        print("  FAIL", f, e)
    print("icon candidates:")
    for p in find_icons():
        print("  ", os.path.getsize(p), p)
