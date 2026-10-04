"""Parse a WoW 3.3.5a minidump (32-bit) and print the exception record + registers.

Usage: python dump_exception.py <file.dmp> [more.dmp ...]
"""
import struct
import sys

MDMP_SIGNATURE = 0x504D444D  # 'MDMP'

STREAM_THREAD_LIST = 3
STREAM_MODULE_LIST = 4
STREAM_MEMORY_LIST = 5
STREAM_EXCEPTION = 6
STREAM_SYSTEM_INFO = 7
STREAM_MEMORY64_LIST = 9

# x86 CONTEXT offsets
CTX_EDI, CTX_ESI, CTX_EBX, CTX_EDX = 0x9C, 0xA0, 0xA4, 0xA8
CTX_ECX, CTX_EAX, CTX_EBP, CTX_EIP = 0xAC, 0xB0, 0xB4, 0xB8
CTX_EFLAGS, CTX_ESP, CTX_SS = 0xC0, 0xC4, 0xC8


def parse(path):
    data = open(path, 'rb').read()
    sig, version, nstreams, dir_rva, checksum, tds, flags = struct.unpack_from('<IIIIIIQ', data, 0)
    if sig != MDMP_SIGNATURE:
        raise SystemExit(f'{path}: not a minidump (sig={sig:#x})')
    streams = {}
    for i in range(nstreams):
        stype, size, rva = struct.unpack_from('<III', data, dir_rva + i * 12)
        streams.setdefault(stype, []).append((size, rva))

    out = {'path': path, 'version': version, 'streams': sorted(streams),
           'streams_map': streams, 'timestamp': tds}

    if STREAM_MODULE_LIST in streams:
        size, rva = streams[STREAM_MODULE_LIST][-1]
        n = struct.unpack_from('<I', data, rva)[0]
        mods = []
        for i in range(n):
            off = rva + 4 + i * 108
            base, msize, _csum, _tds, namerva = struct.unpack_from('<QIIII', data, off)
            nlen = struct.unpack_from('<I', data, namerva)[0]
            name = data[namerva + 4:namerva + 4 + nlen].decode('utf-16-le', 'replace')
            mods.append((base, msize, name))
        out['modules'] = mods

    if STREAM_THREAD_LIST in streams:
        size, rva = streams[STREAM_THREAD_LIST][-1]
        n = struct.unpack_from('<I', data, rva)[0]
        threads = []
        for i in range(n):
            off = rva + 4 + i * 48
            tid, susp, prio_class, prio = struct.unpack_from('<IIII', data, off)
            teb = struct.unpack_from('<Q', data, off + 16)[0]
            stack_start, stack_size, stack_rva = struct.unpack_from('<QII', data, off + 24)
            csize, crva = struct.unpack_from('<II', data, off + 40)
            ctx = data[crva:crva + csize]
            regs = {
                'edi': struct.unpack_from('<I', ctx, CTX_EDI)[0],
                'esi': struct.unpack_from('<I', ctx, CTX_ESI)[0],
                'ebx': struct.unpack_from('<I', ctx, CTX_EBX)[0],
                'edx': struct.unpack_from('<I', ctx, CTX_EDX)[0],
                'ecx': struct.unpack_from('<I', ctx, CTX_ECX)[0],
                'eax': struct.unpack_from('<I', ctx, CTX_EAX)[0],
                'ebp': struct.unpack_from('<I', ctx, CTX_EBP)[0],
                'eip': struct.unpack_from('<I', ctx, CTX_EIP)[0],
                'eflags': struct.unpack_from('<I', ctx, CTX_EFLAGS)[0],
                'esp': struct.unpack_from('<I', ctx, CTX_ESP)[0],
            }
            threads.append({'thread_id': tid, 'teb': teb,
                            'stack': (stack_start, stack_size, stack_rva),
                            'regs': regs})
        out['threads'] = threads

    if STREAM_EXCEPTION in streams:
        size, rva = streams[STREAM_EXCEPTION][-1]
        tid, _align = struct.unpack_from('<II', data, rva)
        code, eflags = struct.unpack_from('<II', data, rva + 8)
        rec_ptr, addr = struct.unpack_from('<QQ', data, rva + 16)
        nparams = struct.unpack_from('<I', data, rva + 32)[0]
        params = struct.unpack_from('<15Q', data, rva + 40)
        tctx_size, tctx_rva = struct.unpack_from('<II', data, rva + 160)
        ctx = data[tctx_rva:tctx_rva + tctx_size]
        regs = {
            'edi': struct.unpack_from('<I', ctx, CTX_EDI)[0],
            'esi': struct.unpack_from('<I', ctx, CTX_ESI)[0],
            'ebx': struct.unpack_from('<I', ctx, CTX_EBX)[0],
            'edx': struct.unpack_from('<I', ctx, CTX_EDX)[0],
            'ecx': struct.unpack_from('<I', ctx, CTX_ECX)[0],
            'eax': struct.unpack_from('<I', ctx, CTX_EAX)[0],
            'ebp': struct.unpack_from('<I', ctx, CTX_EBP)[0],
            'eip': struct.unpack_from('<I', ctx, CTX_EIP)[0],
            'eflags': struct.unpack_from('<I', ctx, CTX_EFLAGS)[0],
            'esp': struct.unpack_from('<I', ctx, CTX_ESP)[0],
        }
        out['exception'] = {'thread_id': tid, 'code': code, 'flags': eflags,
                            'address': addr, 'nparams': nparams,
                            'params': params[:nparams], 'regs': regs,
                            'ctx_size': tctx_size}

    # stack memory available in the dump
    mem = []
    if STREAM_MEMORY_LIST in streams:
        size, rva = streams[STREAM_MEMORY_LIST][-1]
        n = struct.unpack_from('<I', data, rva)[0]
        for i in range(n):
            start, msize, mrva = struct.unpack_from('<QII', data, rva + 4 + i * 16)
            mem.append((start, msize, data[mrva:mrva + msize]))
    if STREAM_MEMORY64_LIST in streams:
        size, rva = streams[STREAM_MEMORY64_LIST][-1]
        n, base_rva = struct.unpack_from('<QQ', data, rva)
        cur = base_rva
        for i in range(n):
            start, msize = struct.unpack_from('<QQ', data, rva + 16 + i * 16)
            mem.append((start, msize, data[cur:cur + msize]))
            cur += msize
    out['memory'] = mem
    out['data'] = data
    return out


def describe(md):
    print('=' * 78)
    print(md['path'])
    if 'exception' not in md:
        print('  no exception stream')
        return
    e = md['exception']
    r = e['regs']
    print(f"  exception code   : {e['code']:#010x}")
    print(f"  exception address: {e['address']:#010x}"
          f"  (module {module_of(md, e['address'])})")
    print(f"  thread id        : {e['thread_id']}")
    for p in e['params']:
        print(f"  param            : {p:#010x}  (module {module_of(md, p)})")
    print('  registers:')
    print('    eip={eip:#010x} esp={esp:#010x} ebp={ebp:#010x} eflags={eflags:#010x}'.format(**r))
    print('    eax={eax:#010x} ebx={ebx:#010x} ecx={ecx:#010x} edx={edx:#010x}'.format(**r))
    print('    esi={esi:#010x} edi={edi:#010x}'.format(**r))
    print(f"  stack bytes in dump: {sum(m[1] for m in md['memory'])}")


def module_of(md, addr):
    for base, size, name in md.get('modules', []):
        if base <= addr < base + size:
            return f"{name}+{addr - base:#x}"
    return 'unmapped'


def read_mem(md, addr, count):
    for start, size, blob in md['memory']:
        if start <= addr and addr + count <= start + size:
            off = addr - start
            return blob[off:off + count]
    return None


def show_threads(md, want=None):
    for t in md.get('threads', []):
        r = t['regs']
        if want is not None and t['thread_id'] != want:
            continue
        print(f"  thread {t['thread_id']}: eip={r['eip']:#010x} ({module_of(md, r['eip'])}) "
              f"esp={r['esp']:#010x} ebp={r['ebp']:#010x} eax={r['eax']:#010x} "
              f"ebx={r['ebx']:#010x} ecx={r['ecx']:#010x} edx={r['edx']:#010x} "
              f"esi={r['esi']:#010x} edi={r['edi']:#010x}")


def main():
    for path in sys.argv[1:]:
        md = parse(path)
        describe(md)
        if 'threads' in md:
            ids = [t['thread_id'] for t in md['threads']]
            print(f"  threads in dump ({len(ids)}): {ids}")
        # custom stream 0x1000 - dump WoW's own crash record
        for stype in (0, 15, 4096):
            for size, rva in md['streams_map'].get(stype, []):
                blob = md['data'][rva:rva + size]
                print(f"  stream {stype} size={size}: {blob[:64].hex()}")



if __name__ == '__main__':
    main()
