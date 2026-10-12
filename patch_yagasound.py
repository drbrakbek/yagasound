#!/usr/bin/env python3
"""No-CD patch for yagasound.dll (Yaga engine / Humongous games, e.g. Pajama Sam 4 Steam).

Usage: python patch_yagasound.py path/to/yagasound.dll [more.dll ...]

Finds the redbook init code by byte pattern (not a fixed offset), so it also works on
other builds. Makes <file>.bak first. Changes 3 bytes: 0F 95 C0 (setne al) -> B0 01 90
(mov al,1; nop), so AIL_redbook_open() returning 0 (no CD drive) no longer fails init.
"""
import sys, shutil

# xor eax,eax / test ecx,ecx / mov ecx,[esp+0Ch] / pop edi / [setne al] / pop esi / restore SEH
PRE  = bytes.fromhex("33c0" "85c9" "8b4c240c" "5f")
OLD  = bytes.fromhex("0f95c0")
POST = bytes.fromhex("5e" "64890d00000000")
NEW  = bytes.fromhex("b00190")

def patch(path):
    data = bytearray(open(path, "rb").read())
    needle = PRE + OLD + POST
    first = data.find(needle)
    if first < 0:
        if PRE + NEW + POST in data:
            return "already patched"
        return "pattern not found, nothing changed"
    if data.find(needle, first + 1) >= 0:
        return "pattern found more than once, nothing changed"
    shutil.copy2(path, path + ".bak")
    o = first + len(PRE)
    data[o:o+3] = NEW
    open(path, "wb").write(data)
    return "patched at 0x%X (backup: %s.bak)" % (o, path)

if len(sys.argv) < 2:
    sys.exit(__doc__)
for p in sys.argv[1:]:
    print(p + ":", patch(p))
