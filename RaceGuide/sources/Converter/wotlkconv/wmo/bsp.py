"""Rebuilding a WMO group's collision tree.

``MOBN``/``MOBR`` hold an axis-aligned BSP over the group's triangles, and the
client uses it for every collision and line-of-sight query. Splitting a group
renumbers its triangles, which invalidates the original tree -- so the tree has
to be rebuilt, not carried over. A group without one is a group players walk
through.

Node layout (16 bytes)::

    uint16 flags        0/1/2 = split on X/Y/Z, 0x4 = leaf
    int16  negChild     child on the negative side, -1 for none
    int16  posChild
    uint16 faceCount    leaves only
    uint32 faceStart    leaves only: offset into MOBR
    float  planeDist    internal nodes only: where the split sits
"""

from __future__ import annotations

import struct
from collections.abc import Sequence

NODE_SIZE = 16

FLAG_X_AXIS = 0x0
FLAG_Y_AXIS = 0x1
FLAG_Z_AXIS = 0x2
FLAG_LEAF = 0x4

#: Node indices are int16, so a tree cannot grow past this.
MAX_NODES = 0x7FFF
#: Deep trees buy nothing and risk running out of node indices.
MAX_DEPTH = 24


def _centroids(vertices: Sequence[tuple[float, float, float]],
               triangles: Sequence[tuple[int, int, int]]) -> list[tuple[float, float, float]]:
    out = []
    count = len(vertices)
    for a, b, c in triangles:
        if a >= count or b >= count or c >= count:
            out.append((0.0, 0.0, 0.0))
            continue
        va, vb, vc = vertices[a], vertices[b], vertices[c]
        out.append(((va[0] + vb[0] + vc[0]) / 3.0,
                    (va[1] + vb[1] + vc[1]) / 3.0,
                    (va[2] + vb[2] + vc[2]) / 3.0))
    return out


def build_bsp(vertices: Sequence[tuple[float, float, float]],
              triangles: Sequence[tuple[int, int, int]],
              max_faces: int | None = None) -> tuple[bytes, bytes]:
    """Build (MOBN, MOBR) over ``triangles``.

    ``max_faces`` is the most triangles a leaf may hold; it defaults to a value
    that keeps the node count inside the int16 index space for the number of
    triangles given.
    """
    face_count = len(triangles)
    if face_count == 0:
        return b"", b""

    if max_faces is None:
        # Two nodes per leaf in the worst case, and leave headroom.
        max_faces = max(24, (2 * face_count) // (MAX_NODES // 2) + 1)

    centroids = _centroids(vertices, triangles)
    nodes: list[bytearray] = []
    order: list[int] = []

    def emit_leaf(faces: list[int]) -> int:
        start = len(order)
        order.extend(faces)
        node = bytearray(NODE_SIZE)
        struct.pack_into("<HhhHIf", node, 0, FLAG_LEAF, -1, -1,
                         len(faces), start, 0.0)
        nodes.append(node)
        return len(nodes) - 1

    def build(faces: list[int], depth: int) -> int:
        if len(faces) <= max_faces or depth >= MAX_DEPTH or \
                len(nodes) >= MAX_NODES - 2:
            return emit_leaf(faces)

        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3
        for face in faces:
            c = centroids[face]
            for axis in range(3):
                lo[axis] = min(lo[axis], c[axis])
                hi[axis] = max(hi[axis], c[axis])
        axis = max(range(3), key=lambda a: hi[a] - lo[a])
        if hi[axis] - lo[axis] <= 1e-6:
            return emit_leaf(faces)

        faces.sort(key=lambda f: centroids[f][axis])
        middle = len(faces) // 2
        plane = centroids[faces[middle]][axis]
        negative = faces[:middle]
        positive = faces[middle:]
        if not negative or not positive:
            return emit_leaf(faces)

        index = len(nodes)
        nodes.append(bytearray(NODE_SIZE))     # placeholder, patched below
        neg_child = build(negative, depth + 1)
        pos_child = build(positive, depth + 1)
        struct.pack_into("<HhhHIf", nodes[index], 0,
                         (FLAG_X_AXIS, FLAG_Y_AXIS, FLAG_Z_AXIS)[axis],
                         neg_child, pos_child, 0, 0, plane)
        return index

    build(list(range(face_count)), 0)
    mobn = b"".join(bytes(node) for node in nodes)
    mobr = struct.pack("<" + "H" * len(order), *order) if order else b""
    return mobn, mobr


def node_count(mobn: bytes) -> int:
    return len(mobn) // NODE_SIZE


def validate(mobn: bytes, mobr: bytes, face_count: int) -> list[str]:
    """Structural checks, used by the tests rather than at conversion time."""
    problems: list[str] = []
    count = node_count(mobn)
    seen: set[int] = set()
    for i in range(count):
        flags, neg, pos, faces, start, _plane = struct.unpack_from(
            "<HhhHIf", mobn, i * NODE_SIZE)
        if flags & FLAG_LEAF:
            if start + faces > len(mobr) // 2:
                problems.append(f"leaf {i} runs past the face list")
            for n in range(faces):
                face = struct.unpack_from("<H", mobr, (start + n) * 2)[0]
                if face >= face_count:
                    problems.append(f"leaf {i} references triangle {face}")
                seen.add(face)
        else:
            for child in (neg, pos):
                if child < 0 or child >= count:
                    problems.append(f"node {i} has child {child}")
    if len(seen) != face_count:
        problems.append(f"tree covers {len(seen)} of {face_count} triangles")
    return problems
