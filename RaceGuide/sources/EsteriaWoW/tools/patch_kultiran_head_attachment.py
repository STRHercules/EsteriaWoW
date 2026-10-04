"""Re-anchor Kul Tiran head components to the character model's head geometry."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import math
import shutil
import struct
from collections import deque
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, Storm


REPO = Path(__file__).resolve().parents[1]
CLIENT_DATA = REPO / "3.3.5a - Dev" / "Data"
PATCH_G = CLIENT_DATA / "Patch-G.MPQ"
PATCH_Y = CLIENT_DATA / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev" / "Backups"

READ_ONLY = 0x00000100
ATTACHMENT_TABLE_SLOT = 0xF0
ATTACHMENT_STRIDE = 0x28
HEAD_ATTACHMENT_ID = 11
BONE_TABLE_SLOT = 0x2C
BONE_STRIDE = 0x58
HEAD_KEY_BONE = 6
VERTEX_TABLE_SLOT = 0x3C
VERTEX_STRIDE = 48
HEAD_CEILING = 0.30
CALIBRATION_HELM = {
    "M": r"Item\ObjectComponents\Head\Helm_Leather_B_06_KtM.m2",
    "F": r"Item\ObjectComponents\Head\Helm_Leather_B_06_KtF.m2",
}
MODEL_KEYS = {
    "M": (
        r"Character\Naga_\male\kultiranmale.m2",
        r"Character\KulTiran\Male\KulTiranMale.m2",
    ),
    "F": (
        r"Character\Naga_\Female\kultiranfemale.m2",
        r"Character\KulTiran\Female\KulTiranFemale.m2",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_read(storm: Storm, path: Path):
    handle = c.c_void_p()
    if not storm.dll.SFileOpenArchive(str(path), 0, READ_ONLY, c.byref(handle)):
        raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
    return handle


def read_entry(storm: Storm, archive, name: str) -> bytes:
    return storm.read(archive, name)


def attachment_record(payload: bytes) -> tuple[int, tuple[float, float, float]]:
    count, offset = struct.unpack_from("<II", payload, ATTACHMENT_TABLE_SLOT)
    if not (1 <= count <= 128) or offset + count * ATTACHMENT_STRIDE > len(payload):
        raise ValueError("invalid header-referenced attachment table")
    matches = []
    for index in range(count):
        record = offset + index * ATTACHMENT_STRIDE
        if struct.unpack_from("<I", payload, record)[0] == HEAD_ATTACHMENT_ID:
            matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"expected one real attachment 11, found {len(matches)}")
    record = matches[0]
    return record, struct.unpack_from("<3f", payload, record + 8)


def patch_real_attachment(
    payload: bytes,
    pivot: tuple[float, float, float],
) -> tuple[bytes, tuple[float, float, float]]:
    record, old = attachment_record(payload)
    patched = bytearray(payload)
    struct.pack_into("<3f", patched, record + 8, *pivot)
    return bytes(patched), old


def head_bone_data(payload: bytes) -> tuple[int, list[tuple[int, int, tuple[float, float, float]]]]:
    count, offset = struct.unpack_from("<II", payload, BONE_TABLE_SLOT)
    if not (1 <= count <= 4096) or offset + count * BONE_STRIDE > len(payload):
        raise ValueError("invalid M2 bone table")
    bones = []
    head_index = None
    for index in range(count):
        record = offset + index * BONE_STRIDE
        key_bone = struct.unpack_from("<i", payload, record)[0]
        parent = struct.unpack_from("<h", payload, record + 8)[0]
        pivot = struct.unpack_from("<3f", payload, record + BONE_STRIDE - 12)
        bones.append((key_bone, parent, pivot))
        if key_bone == HEAD_KEY_BONE:
            head_index = index
    if head_index is None:
        raise ValueError("M2 has no head key bone")
    return head_index, bones


def head_bone_members(payload: bytes) -> tuple[int, list[tuple[int, int, tuple[float, float, float]]], set[int]]:
    head_index, bones = head_bone_data(payload)
    children: dict[int, list[int]] = {}
    for index, (_key_bone, parent, _pivot) in enumerate(bones):
        children.setdefault(parent, []).append(index)
    members = {head_index}
    pending = deque([head_index])
    while pending:
        parent = pending.popleft()
        for child in children.get(parent, []):
            if child in members:
                continue
            members.add(child)
            pending.append(child)
    return head_index, bones, members


def skull_box(payload: bytes) -> tuple[list[float], list[float]]:
    head_index, bones, members = head_bone_members(payload)
    vertex_count, vertex_offset = struct.unpack_from("<II", payload, VERTEX_TABLE_SLOT)
    if vertex_offset + vertex_count * VERTEX_STRIDE > len(payload):
        raise ValueError("invalid M2 vertex table")
    ceiling = bones[head_index][2][2] + HEAD_CEILING
    low = [float("inf")] * 3
    high = [float("-inf")] * 3
    for index in range(vertex_count):
        record = vertex_offset + index * VERTEX_STRIDE
        point = struct.unpack_from("<3f", payload, record)
        if any(abs(value) > 100 for value in point) or point[2] > ceiling:
            continue
        weights = payload[record + 12 : record + 16]
        bone_indices = payload[record + 16 : record + 20]
        dominant = max(range(4), key=lambda slot: weights[slot])
        if not weights[dominant] or bone_indices[dominant] not in members:
            continue
        for axis, value in enumerate(point):
            low[axis] = min(low[axis], value)
            high[axis] = max(high[axis], value)
    if any(value == float("inf") for value in low + high):
        raise ValueError("no head-skinned vertices found")
    return low, high


def model_anchor(character: bytes, helmet: bytes) -> tuple[float, float, float]:
    _record, old = attachment_record(character)
    skull_low, skull_high = skull_box(character)
    helm_low = struct.unpack_from("<3f", helmet, 0xA0)
    helm_high = struct.unpack_from("<3f", helmet, 0xAC)
    return (
        ((skull_low[0] + skull_high[0]) - (helm_low[0] + helm_high[0])) / 2,
        old[1],
        ((skull_low[2] + skull_high[2]) - (helm_low[2] + helm_high[2])) / 2,
    )


def model_aliases(sex: str) -> tuple[str, ...]:
    keys = MODEL_KEYS[sex]
    return tuple(
        alias
        for key in keys
        for alias in (key, key[:-3] + ".mdx")
    )


def vectors_close(actual: tuple[float, float, float], expected: tuple[float, float, float]) -> bool:
    return all(math.isclose(left, right, rel_tol=0.0, abs_tol=1e-6) for left, right in zip(actual, expected))


def backup_target(target: Path) -> tuple[Path, str]:
    before = sha256(target)
    backup = BACKUP_ROOT / f"Patch-Y-before-kultiran-head-{before[:12]}.MPQ"
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        if sha256(backup) != before:
            raise ValueError(f"existing backup hash mismatch: {backup}")
    else:
        shutil.copy2(target, backup)
    if sha256(backup) != before:
        raise ValueError("backup hash does not match Patch-Y")
    return backup, before


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--target", type=Path, default=PATCH_Y)
    parser.add_argument("--source", type=Path, default=PATCH_G)
    args = parser.parse_args()

    for path in (args.target, args.source):
        if not path.is_file():
            raise FileNotFoundError(path)

    storm = Storm(DLL_DEFAULT)
    source = open_read(storm, args.source)
    target = open_read(storm, args.target)
    try:
        entries: dict[str, bytes] = {}
        reports = {}
        for sex, keys in MODEL_KEYS.items():
            character = read_entry(storm, source, keys[0])
            helmet = read_entry(storm, target, CALIBRATION_HELM[sex])
            anchor = model_anchor(character, helmet)
            patched, old = patch_real_attachment(character, anchor)
            for key in model_aliases(sex):
                entries[key] = patched
            reports[sex] = {
                "source_model": keys[0],
                "old_attachment_11": old,
                "new_attachment_11": anchor,
                "staged_entries": list(model_aliases(sex)),
            }
    finally:
        storm.dll.SFileCloseArchive(source)
        storm.dll.SFileCloseArchive(target)

    if args.dry_run:
        print(json.dumps({"status": "dry-run", "models": reports}, indent=2))
        return

    backup, before = backup_target(args.target)
    storm.replace_archive_entries(args.target, entries)

    target_handle = open_read(storm, args.target)
    try:
        for sex, keys in MODEL_KEYS.items():
            expected = tuple(reports[sex]["new_attachment_11"])
            for key in keys:
                payload = read_entry(storm, target_handle, key)
                _record, actual = attachment_record(payload)
                if not vectors_close(actual, expected):
                    raise ValueError(f"verification mismatch for {key}: {actual} != {expected}")
    finally:
        storm.dll.SFileCloseArchive(target_handle)

    print(
        json.dumps(
            {
                "status": "patched",
                "target": str(args.target),
                "source": str(args.source),
                "backup": str(backup),
                "before_sha256": before,
                "after_sha256": sha256(args.target),
                "models": reports,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
