# Vulpera Retail source and art conversion

Verified on October 2, 2026 against installed Retail product `wow`, version `12.1.0.69933`,
build key `dcfc90fffd79ba00406ae46f5f657592`. Source identifiers belong to Retail; Esteria's existing Vulpera
identity is a separate integration contract.

| Source | Male | Female |
| --- | --- | --- |
| ChrRaces | 35 | 35 |
| ChrModel | 69 | 70 |
| CreatureDisplayInfo | 83913 | 83914 |
| Player M2 FileDataID | 1890761 | 1890759 |
| CharComponentTextureLayout | 145 | 146 |
| Converted vertices | 22163 | 22487 |
| Converted bones | 216 | 222 |
| Converted animation sequences | 336 | 336 |

Both converted bodies are flat M2 version 264 and inspect as `wotlk_compatible: True`. Their own source M2 chunks
contain all animation and bone data: no `SKID`, parent `SKPD`, or `BFID` dependency was found. Source closure includes
102 `AFID` animation references, 14 `SFID` skin references and six hard `TXID` references. Twelve skin references are
Retail LODs; the converter preserves the two full body skins and compacts vertices unused by those skins.

The customization graph contains 20 options, 150 choices, 386 elements, 52 geosets and 293 materials. It contains no
external Vulpera customization collection models. Reachable source assets total 377, each stored with its FileDataID,
logical name, source content key, decoded SHA-256 and dependency relationships in the local inventory.

The complete staged art has 310 files: two M2, two SKIN, 102 ANIM and 204 BLP. This art stage does not establish live
character customization or equipment acceptance. Retail replacement texture types 16 through 19 require explicit
Wrath runtime material mapping. Layouts 145 and 146 are both 2048 by 1024: the conventional body component atlas
occupies the left 1024 by 1024 region, with character extras on the right. Preserve these source rectangles when
retargeting body UVs and armor textures.

## Source recovery

Twenty-two textures initially failed with `not a BLTE stream`. Direct inspection showed their CASC index offsets
point at `BLTE` itself; installed Converter unconditionally removes a 30-byte archive entry header. Reading those
entries without removing the header recovered the exact source bytes. Each recovery verified the BLTE header MD5
against the encoding key and the decoded MD5 against the pinned root's content key. No Retail files or installed
Converter files were modified. The final source inventory contains zero unreadable assets.

The ordinary Converter report retains its 22 skips as original evidence. The supplemental offline report records
their successful conversion, and the combined physical staging tree contains all 204 selected BLPs. Use both reports
when assessing completeness.

`CreatureDisplayInfo.db2` still needs unavailable TACT key `583C5B29BF208655`. The 26 other required DB2 tables extracted
successfully; verified player M2 IDs come from named listfile records and decoded source M2s, not guessed display joins.

## Playable choice boundaries

Fur Color has eight ordinary choices plus one Transmog placeholder (`ChrCustomizationReqID` 10).
Eye Color has 14 ordinary choices, one Death Knight choice, one Transmog placeholder and 18 internal/special choices
(`ChrCustomizationReqID` 12). Eye Style's three choices are also requirement 12. Inventory all these rows, but avoid
treating internal or Transmog placeholder entries as ordinary creator options.

Other playable options are Face (six), Ears (six male/eight female), Snout (six), Pattern (three), Earrings (two),
and Eyesight (four). Hair Style contains one source choice. Requirement rows preserve the class masks for ordinary,
Death Knight and Eyesight choices.

## Local evidence and replay

```text
G:\RetroPorterWork\vulpera\reports\source-pin.json
G:\RetroPorterWork\vulpera\reports\discovery.json
G:\RetroPorterWork\vulpera\reports\source-inventory.json
G:\RetroPorterWork\vulpera\reports\texture-layouts.json
G:\RetroPorterWork\vulpera\reports\asset-convert.json
G:\RetroPorterWork\vulpera\reports\asset-convert-recovered.json
G:\RetroPorterWork\vulpera\raw\
G:\RetroPorterWork\vulpera\output\patch-root\custom\vulpera\
```

The local replay scripts guard the source product, version and build key before and after each stage, log their
commands, reject changed existing raw files, and keep extracted Blizzard data outside the repository:

```powershell
rtk python G:\RetroPorterWork\vulpera\run_source.py check extract discover plan dryrun convert
rtk python G:\RetroPorterWork\vulpera\inventory_source.py
rtk python G:\RetroPorterWork\vulpera\convert_recovered.py
```
