"""External animation files.

3.3.5a reads a ``.anim`` as one flat blob: the M2's per-sequence track
sub-arrays carry offsets that point straight into it.  Legion wrapped that blob
in an ``AFM2`` chunk, and a model whose rig lives in a ``.skel`` splits it
three ways, each chunk addressed by its own set of tracks and each counting its
offsets from its own start:

* ``AFM2`` -- the model's own tracks (colours, texture animation, particles,
  and bones or attachments the model defines itself);
* ``AFSB`` -- the skeleton's bones, which is where nearly all of a character's
  keyframes are;
* ``AFSA`` -- the skeleton's attachments.

Converting lays the three end to end and moves the skeleton tracks' offsets by
wherever their chunk landed, so every track addresses the one flat file the
client opens.  Dropping ``AFSB`` instead -- it looks optional, sitting beside
the chunk that used to be the whole file -- leaves every bone of an external
animation pointing at keyframes that are not there.

Relocation covers the sequences the file is named after and any alias that
plays them (``SEQUENCE_ALIAS_FLAG``): an alias has no file of its own and
carries the same spans, into this one.

What is not obvious for ``AFM2`` is *where* the offsets
baked into the model are counted from: the start of the ``AFM2`` payload, or
the start of the whole file eight bytes earlier.  Guessing wrong shifts every
keyframe array by eight bytes, which does not crash -- it animates wrongly.

So it is not guessed.  The model names, for each sequence it keeps outside
itself, the exact ``(offset, length)`` of every keyframe array this file is
expected to hold; those spans have to fit the file, and under only one of the
two readings do they land inside it and finish exactly where it ends.  That is
measured per file, and the payload is emitted to match whichever reading the
spans actually support.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable

from ..chunks import ChunkReader
from ..errors import MalformedFileError
from ..options import Options
from ..report import FileResult, Status
from .model import SEQUENCE_ALIAS_FLAG, M2Model
from .types import Track, TrackBase, relocate_external, value_size

KNOWN_ANIM_CHUNKS = {"AFM2", "AFSA", "AFSB", "AFSK"}

#: Skeleton chunks, what they animate, and the model flag saying whether that
#: part of the rig came from a skeleton (and so addresses this chunk).
SKELETON_ANIM_CHUNKS = (
    ("AFSB", "bones", "bones_from_skeleton"),
    ("AFSA", "attachments", "attachments_from_skeleton"),
)

#: Chunks that carry data 3.3.5a cannot use, with the reason.
DROPPED_ANIM_CHUNKS = {
    "AFSK": "skeleton animation overrides",
}


@dataclasses.dataclass(slots=True)
class OffsetBase:
    """Which reading of the model's track offsets this file supports."""

    #: Where offset 0 points: 0 for the AFM2 payload, 8 for the whole file.
    start: int
    #: Spans that fit under this reading, out of those measured.
    fits: int
    total: int
    #: True when the spans finish exactly at the end of the file they address.
    exact: bool

    @property
    def name(self) -> str:
        return "the AFM2 payload" if self.start == 0 else "the whole file"

    @property
    def usable(self) -> bool:
        return self.total > 0 and self.fits == self.total


def served_sequences(model: M2Model, anim_id: int, sub_id: int) -> set[int]:
    """Indices of the sequences whose external keyframes this file holds."""
    wanted = {i for i, seq in enumerate(model.sequences)
              if seq.get("id") == anim_id
              and seq.get("variation_index") == sub_id}
    aliases = {i for i, seq in enumerate(model.sequences)
               if seq.get("flags", 0) & SEQUENCE_ALIAS_FLAG
               and seq.get("alias_next") in wanted}
    return wanted | aliases


def anim_spans(model: M2Model, anim_id: int, sub_id: int,
               tracks: Iterable[Track | TrackBase] | None = None
               ) -> list[tuple[int, int]]:
    """``(offset, length)`` of every keyframe array this ``.anim`` should hold.

    Only the sequences the model keeps outside itself are asked about, and
    only the one animation this file covers.  ``tracks`` narrows it to one
    chunk's worth; by default it is the model's own tracks, which address
    ``AFM2``.
    """
    wanted = served_sequences(model, anim_id, sub_id)
    if not wanted:
        return []
    spans: list[tuple[int, int]] = []
    for track in (model.own_tracks() if tracks is None else tracks):
        for index in sorted(track.external & wanted):
            if index < len(track.timestamp_spans):
                count, offset = track.timestamp_spans[index]
                if count:
                    spans.append((offset, count * 4))
            value_spans = getattr(track, "value_spans", None)
            if value_spans and index < len(value_spans):
                count, offset = value_spans[index]
                if count:
                    spans.append((offset, count * value_size(track.kind)))
    return spans


def measure_offset_base(spans: list[tuple[int, int]], payload_len: int,
                        body_start: int) -> tuple[OffsetBase, OffsetBase]:
    """Test both readings of the offsets against the file that must hold them."""
    out = []
    for start in (0, body_start):
        end = start + payload_len
        fits = sum(1 for offset, length in spans
                   if offset >= start and offset + length <= end)
        reach = max((o + n for o, n in spans), default=0)
        out.append(OffsetBase(start=start, fits=fits, total=len(spans),
                              exact=bool(spans) and reach == end))
    return out[0], out[1]


def convert_anim(data: bytes, source_name: str, opts: Options,
                 model: M2Model | None = None,
                 result: FileResult | None = None,
                 anim_id: int | None = None,
                 sub_id: int = 0) -> tuple[bytes, FileResult]:
    """Unwrap a Legion ``.anim`` into the flat blob 3.3.5a expects."""
    res = result or FileResult(source=source_name, kind="anim")
    res.kind = "anim"
    res.bytes_in = len(data)

    if len(data) < 8:
        raise MalformedFileError(f"{source_name}: file is only {len(data)} bytes")

    # A flat .anim has no chunk structure; anything that is not a recognised
    # chunk magic is treated as already-converted payload.
    reader = ChunkReader.auto(data, KNOWN_ANIM_CHUNKS, name=source_name)
    chunks = {}
    try:
        for chunk in reader:
            chunks.setdefault(chunk.name, []).append(chunk)
    except MalformedFileError:
        chunks = {}

    if not chunks.keys() & {"AFM2", "AFSA", "AFSB"}:
        res.status = Status.PASSTHROUGH
        res.source_version = "anim (flat)"
        res.target_version = "anim (flat)"
        res.bytes_out = len(data)
        res.info("anim.passthrough", "already a flat 3.3.5a animation blob")
        return data, res

    res.source_version = f"anim (chunked, {len(chunks)} chunk kinds)"
    if "AFM2" in chunks:
        out = _afm2_region(data, chunks["AFM2"][0], model, anim_id, sub_id, res)
    else:
        out = b""
        own = (anim_spans(model, anim_id, sub_id)
               if model is not None and anim_id is not None else [])
        if own:
            res.warn("anim.offsets.unfit",
                     f"the model expects {len(own)} keyframe array(s) of its "
                     f"own in this file, but it has no AFM2 chunk to hold "
                     f"them", spans=len(own))

    out = _append_skeleton_chunks(out, chunks, model, anim_id, sub_id, res)

    dropped = [f"{n} ({DROPPED_ANIM_CHUNKS[n]})"
               for n in chunks if n in DROPPED_ANIM_CHUNKS]
    if dropped:
        res.lossy("anim.chunks.dropped",
                  "dropped animation chunks with no 3.3.5a equivalent: "
                  + ", ".join(dropped), chunks=sorted(chunks))

    res.target_version = "anim (flat)"
    res.bytes_out = len(out)
    res.info("anim.unwrapped",
             f"unwrapped {'/'.join(sorted(chunks))} into a {len(out)}-byte "
             f"flat blob")
    return out, res


def _afm2_region(data: bytes, afm2, model: M2Model | None,
                 anim_id: int | None, sub_id: int, res: FileResult) -> bytes:
    """The ``AFM2`` payload, positioned where the model's own offsets expect."""
    payload = afm2.data
    body_start = afm2.offset          # where the payload sits in the file

    # -- which reading of the offsets does this file support? -------------
    out = payload
    spans = (anim_spans(model, anim_id, sub_id)
             if model is not None and anim_id is not None else [])
    if not spans:
        res.info("anim.offsets.unmeasured",
                 "the model names no external keyframe arrays for this "
                 "animation, so the offsets could not be checked; the AFM2 "
                 "payload was kept at offset 0, which is the reading that "
                 "needs no rewriting")
    else:
        payload_base, file_base = measure_offset_base(spans, len(payload),
                                                      body_start)
        winner = _pick_base(payload_base, file_base)
        if winner is None:
            res.warn("anim.offsets.unfit",
                     f"none of the {len(spans)} keyframe array(s) the model "
                     f"expects here fit this file under either reading "
                     f"({payload_base.fits}/{payload_base.total} fit the "
                     f"payload, {file_base.fits}/{file_base.total} the whole "
                     f"file); kept the payload at offset 0 and left the "
                     f"offsets alone",
                     spans=len(spans))
        elif winner.start == 0:
            res.info("anim.offsets.payload",
                     f"{payload_base.fits} keyframe array(s) confirm the "
                     f"offsets are counted from the AFM2 payload"
                     + (", ending exactly at its end" if payload_base.exact
                        else ""))
        else:
            # The offsets count from the file, so the payload has to stay at
            # the same distance in: the chunk header is kept as padding no
            # track ever addresses.
            out = data[:body_start + len(payload)]
            res.info("anim.offsets.file",
                     f"{file_base.fits} keyframe array(s) show the offsets are "
                     f"counted from the start of the file, so the first "
                     f"{body_start} bytes were kept as padding to hold the "
                     f"keyframes at the offsets the model expects")
    return out


def _append_skeleton_chunks(out: bytes, chunks: dict, model: M2Model | None,
                            anim_id: int | None, sub_id: int,
                            res: FileResult) -> bytes:
    """Lay ``AFSB`` and ``AFSA`` after the ``AFM2`` payload, and point the
    skeleton's tracks at where they landed.

    A chunk is only placed when the model's tracks demonstrably fit it;
    anything else is dropped and reported, because moving offsets that did not
    address the chunk would break tracks that were fine.
    """
    for cname, what, flag in SKELETON_ANIM_CHUNKS:
        if cname not in chunks:
            continue
        body = chunks[cname][0].data
        if model is None or anim_id is None:
            res.lossy("anim.skeleton.unplaced",
                      f"dropped {cname} ({len(body)} bytes of skeleton "
                      f"{what} keyframes): placing it needs the model that "
                      f"addresses it, and this .anim was converted on its own",
                      chunk=cname)
            continue
        if not getattr(model, flag):
            res.lossy("anim.skeleton.unplaced",
                      f"dropped {cname} ({len(body)} bytes of skeleton "
                      f"{what} keyframes): this model's {what} did not come "
                      f"from a skeleton, so none of its tracks address it",
                      chunk=cname)
            continue

        tracks = list(model.bone_tracks() if what == "bones"
                      else model.attachment_tracks())
        spans = anim_spans(model, anim_id, sub_id, tracks)
        if not spans:
            res.info("anim.skeleton.unused",
                     f"{cname} holds {len(body)} bytes, but no skeleton "
                     f"{what} track keeps keyframes here for this animation; "
                     f"left out", chunk=cname)
            continue
        fits = sum(1 for offset, length in spans
                   if offset >= 0 and offset + length <= len(body))
        if fits != len(spans):
            res.warn("anim.skeleton.unfit",
                     f"{len(spans) - fits} of {len(spans)} skeleton {what} "
                     f"keyframe array(s) run past the end of {cname} "
                     f"({len(body)} bytes); dropped it and left the offsets "
                     f"alone, so those {what} will not animate",
                     chunk=cname, spans=len(spans))
            continue

        base = (len(out) + 3) & ~3
        out = out + bytes(base - len(out)) + body
        served = served_sequences(model, anim_id, sub_id)
        moved = sum(relocate_external(track, served, base) for track in tracks)
        res.info("anim.skeleton.placed",
                 f"placed {cname} ({len(body)} bytes of skeleton {what} "
                 f"keyframes) at offset {base} and moved {moved} offset(s) "
                 f"to match", chunk=cname, base=base, moved=moved)
    return out


def _pick_base(payload_base: OffsetBase, file_base: OffsetBase
               ) -> OffsetBase | None:
    """The reading the spans support, or ``None`` when neither does.

    An exact fill is the strong signal: an ``.anim`` exists to hold these
    arrays and nothing else, so the last one ends where the file does.  Where
    both readings fit and neither fills exactly, the payload wins, because
    that is the reading that needs no rewriting.
    """
    for candidate, other in ((payload_base, file_base), (file_base, payload_base)):
        if candidate.usable and candidate.exact and not (
                other.usable and other.exact):
            return candidate
    if payload_base.usable:
        return payload_base
    if file_base.usable:
        return file_base
    return None


def inspect_anim(data: bytes, source_name: str) -> dict:
    reader = ChunkReader.auto(data, KNOWN_ANIM_CHUNKS, name=source_name)
    try:
        chunks = {c.name: len(c.data) for c in reader}
    except MalformedFileError:
        chunks = {}
    return {
        "kind": "anim",
        "chunked": "AFM2" in chunks,
        "chunks": chunks or None,
        "bytes": len(data),
    }
