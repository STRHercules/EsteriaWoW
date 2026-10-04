"""Parse the minidump header for the exception record and the faulting module."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    signature, version, stream_count, directory_rva = struct.unpack_from("<IIII", data, 0)
    print(f"signature={signature:#x} streams={stream_count}")
    modules: list[tuple[int, int, str]] = []
    exception = None
    for index in range(stream_count):
        stream_type, size, rva = struct.unpack_from("<III", data, directory_rva + index * 12)
        if stream_type == 4:  # ModuleListStream
            count = struct.unpack_from("<I", data, rva)[0]
            for module_index in range(count):
                entry = rva + 4 + module_index * 108
                base, module_size = struct.unpack_from("<QI", data, entry)
                name_rva, = struct.unpack_from("<I", data, entry + 20)
                length = struct.unpack_from("<I", data, name_rva)[0]
                name = data[name_rva + 4 : name_rva + 4 + length].decode("utf-16-le", "replace")
                modules.append((base, module_size, name))
        elif stream_type == 6:  # ExceptionStream
            thread_id, = struct.unpack_from("<I", data, rva)
            code, flags, nested, address = struct.unpack_from("<IIQQ", data, rva + 8)
            params = struct.unpack_from("<15Q", data, rva + 8 + 32)
            exception = (thread_id, code, flags, address, params)

    if exception:
        thread_id, code, flags, address, params = exception
        print(f"thread={thread_id} exception={code:#x} flags={flags:#x} address={address:#x}")
        print(f"parameters={[hex(value) for value in params[:4] if value]}")
        for base, size, name in modules:
            if base <= address < base + size:
                print(f"faulting module: {name} + {address - base:#x}")
                break
        else:
            print("faulting address not inside a known module")
    else:
        print("no exception stream found")


if __name__ == "__main__":
    main()
