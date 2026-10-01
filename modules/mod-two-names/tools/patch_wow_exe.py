#!/usr/bin/env python3
"""
AzerothCore mod-two-names: Client Wow.exe Patcher (Python)

Patches Wow.exe (3.3.5a build 12340):
1. Patches ValidateName (offset 0x2B0390) so that spaces in character names
   (e.g. "John Doe") are accepted during character creation and sent to the server.
2. Patches EditBox::InsertChar (offset 0x564F23) to unlock the 12-character keyboard
   typing limit so players can create longer names.

Usage:
    python patch_wow_exe.py [path/to/Wow.exe]
"""

import os
import shutil
import sys

target_path = sys.argv[1] if len(sys.argv) > 1 else "Wow.exe"

if not os.path.isfile(target_path):
    print(f"[Error] Target file '{target_path}' not found.")
    print("Usage: python patch_wow_exe.py <path-to-Wow.exe>")
    sys.exit(1)

backup_path = target_path + ".bak_two_names"
if not os.path.isfile(backup_path):
    shutil.copyfile(target_path, backup_path)
    print(f"[Backup] Created backup at '{backup_path}'")

with open(target_path, "r+b") as f:
    f.seek(0x2B0390)
    f.write(b"\xb8\x57\x00\x00\x00\xc3")

    f.seek(0x564F23)
    f.write(b"\xe9\xf5\x00\x00\x00\x90")

print(f"[Success] Successfully patched '{target_path}' for dual names & expanded name length!")
