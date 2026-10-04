# Customization Strategy

Retail customization is richer than the WotLK character system. The pipeline therefore separates **source discovery** from **WotLK normalization**.

Source discovery resolves Retail options, choices, elements, geosets, skinned models, materials, bone sets, conditional models, display overrides, and their file dependencies into a per-race source cache.

Normalization then flattens that graph into the smaller WotLK concepts used by tables such as `CharSections`, `CharHairGeosets`, and `CharacterFacialHairStyles`.

For `CharSections`, preserve the legacy selector axes instead of encoding Retail combinations into one field. Skin Color remains the section color index. Face remains the section variation/style index, with one face row for every supported `(face, skin)` pair. If the HD model uses an Orc2-style extra-head texture, section 0 should provide one body/base-head pair per skin while section 1 provides the FaceLower/FaceUpper overlays. Do not turn a 9-skin x 9-face race into 81 synthetic skin colors just to carry complete Retail head materials.

When generated compositor art is corrected, put it at a new virtual path or replace the copy in the actual global MPQ chain. A corrected locale-only copy is not sufficient for 3.3.5a character compositing when a stale global copy of the same path still exists.

Start every new race with the manifest's minimum viable customization target. Expand only after the small set renders and creates characters correctly.
