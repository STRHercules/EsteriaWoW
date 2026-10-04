"""Stream ciphers used by BLTE's encrypted (``E``) chunks.

Blizzard ships unreleased content encrypted and publishes the keys later, so a
CASC reader that cannot decrypt is a CASC reader that silently misses files.
Both ciphers are tiny, so they are implemented here rather than pulling in a
crypto dependency for two algorithms used on a handful of files.

Nothing here is used to protect data -- it only reads what Blizzard wrote.
"""

from __future__ import annotations

import struct

_MASK = 0xFFFFFFFF


def _rotl(v: int, n: int) -> int:
    return ((v << n) | (v >> (32 - n))) & _MASK


def _salsa20_block(state: list[int]) -> bytes:
    x = list(state)
    for _ in range(10):  # 20 rounds, two per iteration
        # column round
        x[4] ^= _rotl((x[0] + x[12]) & _MASK, 7)
        x[8] ^= _rotl((x[4] + x[0]) & _MASK, 9)
        x[12] ^= _rotl((x[8] + x[4]) & _MASK, 13)
        x[0] ^= _rotl((x[12] + x[8]) & _MASK, 18)
        x[9] ^= _rotl((x[5] + x[1]) & _MASK, 7)
        x[13] ^= _rotl((x[9] + x[5]) & _MASK, 9)
        x[1] ^= _rotl((x[13] + x[9]) & _MASK, 13)
        x[5] ^= _rotl((x[1] + x[13]) & _MASK, 18)
        x[14] ^= _rotl((x[10] + x[6]) & _MASK, 7)
        x[2] ^= _rotl((x[14] + x[10]) & _MASK, 9)
        x[6] ^= _rotl((x[2] + x[14]) & _MASK, 13)
        x[10] ^= _rotl((x[6] + x[2]) & _MASK, 18)
        x[3] ^= _rotl((x[15] + x[11]) & _MASK, 7)
        x[7] ^= _rotl((x[3] + x[15]) & _MASK, 9)
        x[11] ^= _rotl((x[7] + x[3]) & _MASK, 13)
        x[15] ^= _rotl((x[11] + x[7]) & _MASK, 18)
        # row round
        x[1] ^= _rotl((x[0] + x[3]) & _MASK, 7)
        x[2] ^= _rotl((x[1] + x[0]) & _MASK, 9)
        x[3] ^= _rotl((x[2] + x[1]) & _MASK, 13)
        x[0] ^= _rotl((x[3] + x[2]) & _MASK, 18)
        x[6] ^= _rotl((x[5] + x[4]) & _MASK, 7)
        x[7] ^= _rotl((x[6] + x[5]) & _MASK, 9)
        x[4] ^= _rotl((x[7] + x[6]) & _MASK, 13)
        x[5] ^= _rotl((x[4] + x[7]) & _MASK, 18)
        x[11] ^= _rotl((x[10] + x[9]) & _MASK, 7)
        x[8] ^= _rotl((x[11] + x[10]) & _MASK, 9)
        x[9] ^= _rotl((x[8] + x[11]) & _MASK, 13)
        x[10] ^= _rotl((x[9] + x[8]) & _MASK, 18)
        x[12] ^= _rotl((x[15] + x[14]) & _MASK, 7)
        x[13] ^= _rotl((x[12] + x[15]) & _MASK, 9)
        x[14] ^= _rotl((x[13] + x[12]) & _MASK, 13)
        x[15] ^= _rotl((x[14] + x[13]) & _MASK, 18)
    return struct.pack("<16I", *[(a + b) & _MASK for a, b in zip(x, state)])


def salsa20(key: bytes, nonce: bytes, data: bytes) -> bytes:
    """Salsa20/20 keystream XOR. Accepts 16- or 32-byte keys."""
    if len(key) == 16:
        constants = b"expand 16-byte k"
        key_words = struct.unpack("<4I", key) * 2
    elif len(key) == 32:
        constants = b"expand 32-byte k"
        key_words = struct.unpack("<8I", key)
    else:
        raise ValueError(f"Salsa20 key must be 16 or 32 bytes, got {len(key)}")

    # BLTE nonces are shorter than the 8 bytes Salsa20 wants; pad with zeroes.
    iv = (bytes(nonce) + b"\0" * 8)[:8]
    c = struct.unpack("<4I", constants)
    n = struct.unpack("<2I", iv)

    out = bytearray(len(data))
    counter = 0
    for offset in range(0, len(data), 64):
        state = [
            c[0], key_words[0], key_words[1], key_words[2],
            key_words[3], c[1], n[0], n[1],
            counter & _MASK, (counter >> 32) & _MASK, c[2], key_words[4],
            key_words[5], key_words[6], key_words[7], c[3],
        ]
        block = _salsa20_block(state)
        chunk = data[offset : offset + 64]
        for i, byte in enumerate(chunk):
            out[offset + i] = byte ^ block[i]
        counter += 1  # noqa: SIM113 -- cipher block counter, not an index
    return bytes(out)


def arc4(key: bytes, nonce: bytes, data: bytes) -> bytes:
    """ARC4, the other cipher BLTE's ``E`` chunks use."""
    seed = bytes(key) + bytes(nonce)
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + seed[i % len(seed)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    out = bytearray(len(data))
    i = j = 0
    for n, byte in enumerate(data):
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out[n] = byte ^ s[(s[i] + s[j]) & 0xFF]
    return bytes(out)
