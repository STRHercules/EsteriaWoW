import re
from pathlib import Path

atlas_path = Path(r"g:\risServer\Esteria - Client\Interface\AddOns\EsteriaGarrison\Retail\Atlas.lua")
text = atlas_path.read_text(encoding="utf-8")
pattern = re.compile(r'\{"retail/(\d+)\.blp",(\d+),(\d+)(?:,(\d+),(\d+))?\}')
entries = pattern.findall(text)
by_fd = {}
for fd, cw, ch, pw, ph in entries:
    by_fd.setdefault(fd, set()).add((int(cw), int(ch), int(pw or 0), int(ph or 0)))

# Canvas measured from the cached file. Only pictures that fill most of that canvas
# are a single padded image. A shared sheet has many different member sizes.
measured = {
    "939606": (1024, 512),
}
for fd, variants in by_fd.items():
    canvases = {(pw, ph) for _, _, pw, ph in variants if pw and ph}
    contents = {(cw, ch) for cw, ch, _, _ in variants}
    if len(canvases) == 1 and len(contents) == 1:
        pw, ph = next(iter(canvases))
        cw, ch = next(iter(contents))
        if cw > pw / 2 and ch > ph / 2:
            measured[fd] = (pw, ph)

# The other garrison maps are the same 672x468 picture on a 1024x512 canvas.
for fd in ("939612", "939613", "978201", "978202", "978203", "1001820", "1001822"):
    measured[fd] = (1024, 512)

def rewrite(match):
    fd, cw, ch = match.group(1), int(match.group(2)), int(match.group(3))
    canvas = measured.get(fd)
    if not canvas:
        return '{"retail/%s.blp",%d,%d}' % (fd, cw, ch)
    return '{"retail/%s.blp",%d,%d,%d,%d}' % (fd, cw, ch, canvas[0], canvas[1])

atlas_path.write_text(pattern.sub(rewrite, text), encoding="utf-8")
print("kept", len(measured))
