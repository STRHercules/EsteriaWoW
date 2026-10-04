# Dreadlord asset override

Create a standalone `G:/RetroPorterWork/dreadlord/output/Patch-Dr.MPQ` for the existing NPC model
`Creature\Dreadlord\DreadLord.m2`. Preserve the normal and green legacy texture names and all existing
display/model IDs. Package only native 3.3.5 models, skins, animations, and their textures.

Use the supplied simplified model and split LOD skin without changing the donor folder. Recover only
required Retail dependencies through the established hash-verified, pinned source reader. Resolve the
authored material/geoset choices before conversion. Reuse the established external-animation embedding
and StormLib packaging helpers. Normalize the supplied body texture's malformed trailing mip entries.

Validate every reference, geometry and animation bounds, native mesh palettes, image mip ranges, and
archive entry readback. Record source/output hashes and rendering approximations outside the archive.
Leave the installed client and server unchanged; delivery is the completed standalone archive.
