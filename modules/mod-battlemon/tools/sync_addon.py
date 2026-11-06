#!/usr/bin/env python3
"""Keep the addon's Lua source in the repository identical to the 3d-version package's two copies.

    python tools/sync_addon.py <package root>                 report differences (exit 1 if any)
    python tools/sync_addon.py <package root> --from-package  copy the package's client copy INTO the repo
    python tools/sync_addon.py <package root> --to-package    copy the repo's files into BOTH package copies and
                                                              refresh their hashes in the package's manifest.json

The package root is the folder that holds client/ and server/ (e.g. G:/Downloads/HDWoWModels/3d-version). Only the
addon's source is handled (Battlemon.lua, Battlemon.toc, Core/*.lua, UI/*.lua); the generated Data/*.lua tables, the
models and the music stay in the package. A file with no manifest row is reported: add the row by hand.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ADDON = os.path.join(ROOT, 'addon', 'Battlemon')
CLIENT = ('client', 'Interface', 'AddOns', 'Battlemon')
SERVER = ('server', 'modules', 'mod-battlemon', 'addon', 'Battlemon')


def source_files(base):
    names = {'Battlemon.lua', 'Battlemon.toc'}
    for sub in ('Core', 'UI'):
        for path in glob.glob(os.path.join(base, sub, '*.lua')):
            names.add(sub + '/' + os.path.basename(path))
    return names


def digest(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def differences(repo, other):
    """Files that differ, are missing from `other`, or exist only there."""
    out = []
    for name in sorted(source_files(repo) | source_files(other)):
        a, b = os.path.join(repo, name), os.path.join(other, name)
        if not os.path.exists(a):
            out.append(name + ' (only in ' + other + ')')
        elif not os.path.exists(b):
            out.append(name + ' (missing from ' + other + ')')
        elif digest(a) != digest(b):
            out.append(name + ' (differs from ' + other + ')')
    return out


def refresh_manifest(package, copies):
    path = os.path.join(package, 'manifest.json')
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    missing = []
    for rel_parts in copies:
        for name in sorted(source_files(os.path.join(package, *rel_parts))):
            rel = '/'.join(rel_parts) + '/' + name
            with open(os.path.join(package, *rel_parts, *name.split('/')), 'rb') as f:
                data = f.read()
            pattern = re.compile(r'("path": "' + re.escape(rel) + r'",\s*"source": "[^"]*",\s*"sha256": ")[0-9a-f]{64}'
                                 r'(",\s*"bytes": )\d+')
            text, n = pattern.subn(lambda m: m.group(1) + hashlib.sha256(data).hexdigest() + m.group(2) + str(len(data)),
                                   text)
            if n != 1:
                missing.append(rel)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    json.loads(text)   # still valid JSON
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('package')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--from-package', action='store_true')
    mode.add_argument('--to-package', action='store_true')
    args = ap.parse_args()
    client, server = (os.path.join(args.package, *parts) for parts in (CLIENT, SERVER))

    if args.from_package:
        for name in sorted(source_files(client)):
            dst = os.path.join(REPO_ADDON, *name.split('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(client, *name.split('/')), dst)
        print('imported', len(source_files(client)), 'files into', REPO_ADDON)
        return 0
    if args.to_package:
        for target in (client, server):
            for name in sorted(source_files(REPO_ADDON)):
                dst = os.path.join(target, *name.split('/'))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(REPO_ADDON, *name.split('/')), dst)
        missing = refresh_manifest(args.package, (CLIENT, SERVER))
        print('copied', len(source_files(REPO_ADDON)), 'files to both package copies; manifest refreshed')
        for rel in missing:
            print('NO MANIFEST ROW (add by hand):', rel)
        return 0

    problems = differences(REPO_ADDON, client) + differences(client, server)
    for p in problems:
        print('DIFF', p)
    print('in sync' if not problems else '%d difference(s)' % len(problems))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
