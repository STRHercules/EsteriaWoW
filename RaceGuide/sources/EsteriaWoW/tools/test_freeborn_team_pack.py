"""Contract test for the Freeborn client patch and its claim path.

Run: python tools/test_freeborn_team_pack.py

Hermetic checks cover the GlueXML payload, the addon, the transforms, and the server sources; the
live checks read the deployed archives. Cross-boundary checks matter here more than usual: the
create screen, the addon and the server have to agree on the CVar name and the addon-message
envelope, and a drift between them fails silently.

Note on the earlier design: an interior-space token in the create name was tried and abandoned.
The client refuses a space in a character name ("Names can only contain letters"), and a Freeborn
name has to follow exactly the same rules as an Alliance or Horde one, so nothing about the name
carries the flag.
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import freeborn_team_pack as pack  # noqa: E402

CLIENT_CANDIDATES = (
    Path(os.environ.get("ESTERIA_CLIENT_ROOT", r"G:\3.3.5a - Dev")),
    ROOT / "3.3.5a - Dev",
)

ADDON_LUA = pack.ADDON_SOURCE / "FreebornClaim.lua"
CLAIM_HEADER = ROOT / "src/server/game/Server/FreebornClaim.h"
CHAT_HANDLER = ROOT / "src/server/game/Handlers/ChatHandler.cpp"

XML_HEADER = (
    '<!-- Autora: Noa -->\n'
    '<Ui xmlns="http://www.blizzard.com/wow/ui/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xsi:schemaLocation="http://www.blizzard.com/wow/ui/\n..\\FrameXML\\UI.xsd">\n'
)

# Mirrors the shipped gender-button container so the transform is exercised against the real
# anchor rather than a re-typed approximation. pack.XML_ANCHOR closes the female CheckButton, the
# container's <Frames>, and the container itself.
FIXTURE_XML = (
    XML_HEADER
    + '    <Frame name="CharacterCreateFrame">\n'
    + "        <Frames>\n"
    + '            <Frame name="CharacterCreateRaceButtonsContainer">\n'
    + "                <Frames/>\n"
    + "            </Frame>\n"
    + '            <Frame name="CharacterCreateGenderButtonsContainer">\n'
    + "                <Frames>\n"
    + '                    <CheckButton name="CharacterCreateGenderButtonMale" '
      'inherits="CharacterCreateGenderButtonTemplate"/>\n'
    + '                    <CheckButton name="CharacterCreateGenderButtonFemale" '
      'inherits="CharacterCreateGenderButtonTemplate">\n'
    + "                        <Scripts/>\n"
    + pack.XML_ANCHOR
    + "\n"
    + "        </Frames>\n"
    + "    </Frame>\n"
    + "</Ui>\n"
)

FIXTURE_LUA = (
    "function CharacterCreate_Okay()\n"
    "    CreateCharacter(CharacterCreateNameEdit:GetText());\n"
    "end\n"
)

# Native bindings that do not exist in this client's glue creation table. The whole reason the
# name was tried as a carrier is that none of these can be called.
FORBIDDEN_BINDINGS = (
    "SetSelectedOutfit",
    "SetSelectedTeam",
    "SetPlayerTeam",
    "SetPlayerTeamId",
    "SetSelectedSkin",
    "SetSelectedFace",
    "SetSelectedHairStyle",
    "SetSelectedHairColor",
    "SetSelectedFacialHair",
    "SendCustomPacket",
)

# The race tooltips' own backdrop, as the stock file spells it out (`local Backdrop2`): the
# background, the edge texture, the 16px tile and the 4px insets. The Freeborn tooltip repeats
# these literally so its border is the race tooltip border, and the live check proves the stock
# file still says the same thing -- if the client ever restyles its race tooltips, this fails
# instead of the two drifting apart silently.
RACE_TOOLTIP_BACKDROP = (
    r'bgFile = "Interface\\Tooltips\\UI-Tooltip-Background"',
    r'edgeFile = "Interface\\Tooltips\\ui-tooltip-border-maw"',
    "tile = true, tileSize = 16, edgeSize = 16",
    "insets = { left = 4, right = 4, top = 4, bottom = 4 }",
)

# What the hover text has to say, one keyword per requirement: no allegiance, city access, quests
# from either side, grouping and guilding with other Freeborn, no grouping or guild membership with
# either faction, and mutual hostility.
TOOLTIP_FACTS = (
    "allegiance",
    "access to their cities",
    "quests from either faction",
    "group and guild freely with other Freeborn",
    "never group or guild with",
    "hostile",
)


def client_root() -> Path | None:
    for candidate in CLIENT_CANDIDATES:
        if (candidate / "Data" / pack.ARCHIVE_NAME).is_file():
            return candidate
    return None


def _load_unsafe_statements(text: str) -> list[str]:
    """Top-level statements in the block body that could index a frame the XML has not made yet.

    The Glue XML creates the frames *after* the script file is executed, so a top-level
    `CharacterCreate.selectedFreeborn = ...` is a nil index. Because it aborts the whole chunk it
    also stops every function below it from being defined, which is how an earlier revision broke
    the create screen. Only the guard assignment and declarations may sit at that level.
    """
    offenders = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.startswith("    ") or raw.startswith("     "):
            continue
        line = raw.strip()
        if not line or line.startswith("--"):
            continue
        if line.startswith("function ") or line.startswith("local "):
            continue
        # Assigning this addon's own globals is safe; indexing a frame is not.
        if line in ("end", "end;") or re.match(r"^CharacterFreeborn_\w+ = ", line):
            continue
        offenders.append(f"line {number}: {line}")
    return offenders


def assert_load_safe(text: str, where: str) -> None:
    offenders = _load_unsafe_statements(text)
    assert not offenders, f"{where}: statements that run before the frames exist (nil index): {offenders}"


def assert_lua_block_shape(lua: str, where: str) -> None:
    """Exactly one current revision of the block, and load-safe.

    Validating the DEPLOYED file rather than only the payload is the point: a stale first revision
    survived a repack precisely because only the payload was being checked.
    """
    assert lua.count(pack.LUA_BEGIN) == 1, f"{where}: expected exactly one managed block"
    assert lua.count(pack.LUA_END) == 1, f"{where}: managed block is not closed exactly once"
    assert lua.count("if not CharacterFreeborn_Init then") == 1, f"{where}: the block is duplicated"
    assert lua.count(pack.LUA_HEADER_MARKER) == 1, f"{where}: a stale revision is still present"

    block = lua[lua.index(pack.LUA_BEGIN) : lua.index(pack.LUA_END) + len(pack.LUA_END)]
    assert_load_safe(block, where)


def assert_xml_button_shape(xml: str, where: str) -> None:
    """The button is declared once and carries its own anchor."""
    assert xml.count(f'name="{pack.FREEBORN_BUTTON_NAME}"') == 1, f"{where}: button declared more than once"

    root = ElementTree.fromstring(xml)
    button = next(e for e in root.iter() if e.get("name") == pack.FREEBORN_BUTTON_NAME)
    # Without its own anchor an unpositioned frame is invisible.
    assert any(c.tag.split("}")[-1] == "Anchors" for c in button), (
        f"{where}: button has no anchor of its own"
    )


def assert_vocabulary_is_stock(xml_text: str) -> None:
    """The Freeborn subtree must not introduce XML the stock file never uses."""
    root = ElementTree.fromstring(xml_text)
    free_tags: set[str] = set()
    free_attrs: set[str] = set()
    rest_tags: set[str] = set()
    rest_attrs: set[str] = set()

    def collect(elem, inside: bool) -> None:
        is_freeborn = inside or elem.get("name") == pack.FREEBORN_BUTTON_NAME
        (free_tags if is_freeborn else rest_tags).add(elem.tag.split("}")[-1])
        (free_attrs if is_freeborn else rest_attrs).update(elem.attrib)
        for child in elem:
            collect(child, is_freeborn)

    collect(root, False)

    assert pack.FREEBORN_BUTTON_NAME in {e.get("name") for e in root.iter()}, "button is not in the file"
    assert not (free_tags - rest_tags), (
        f"Freeborn button uses elements absent from the stock file: {sorted(free_tags - rest_tags)}"
    )
    assert not (free_attrs - rest_attrs), (
        f"Freeborn button uses attributes absent from the stock file: {sorted(free_attrs - rest_attrs)}"
    )

    # Element order matters to the Glue XML parser. The stock file orders these as
    # Size, Anchors, Layers, Scripts -- see CharacterCreateNameEdit, CharCreateOkayButton,
    # CharCreateBackButton and CharacterCreateIconButtonTemplate -- so the button must not reorder
    # them relative to each other.
    canonical = ["Size", "Anchors", "Layers", "Scripts"]
    button = next(e for e in root.iter() if e.get("name") == pack.FREEBORN_BUTTON_NAME)
    children = [c.tag.split("}")[-1] for c in button]
    positions = [canonical.index(tag) for tag in children if tag in canonical]
    assert positions == sorted(positions), f"child ordering disagrees with the stock order: {children}"
    assert "Layers" in children and "Scripts" in children, f"button lost its label or scripts: {children}"


def assert_payloads() -> None:
    xml = (pack.PAYLOAD_ROOT / "CharacterCreate.freeborn.xml").read_text(encoding="utf-8")
    lua = (pack.PAYLOAD_ROOT / "CharacterCreate.freeborn.lua").read_text(encoding="utf-8")

    assert f'name="{pack.FREEBORN_BUTTON_NAME}"' in xml, "button is not declared"
    assert 'inherits="CharacterCreateGenderButtonTemplate"' in xml, "button must reuse the gender template"
    assert 'text="Freeborn"' in xml, "button needs a visible Freeborn label"
    # The plate comes from the template and is swapped at runtime, the way the male/female buttons
    # do it, so the texture elements themselves must NOT be redefined here (a second element with
    # the same $parent name would collide).
    assert "<NormalTexture" not in xml, "must not redefine the inherited plate texture element"
    assert "<PushedTexture" not in xml, "must not redefine the inherited plate texture element"
    # The XML carries the Lua string literal, where backslashes are doubled.
    xml_reference = pack.TEXTURE_REFERENCE.replace("\\", "\\\\")
    assert f'SetTexture("{xml_reference}")' in xml, "button must point at the Freeborn plate"
    assert xml.count(f'SetTexture("{xml_reference}")') == 2, (
        "both the normal and the pushed state must use the Freeborn plate"
    )

    # One name, so the reference in the XML and the packed entry cannot drift apart.
    assert pack.TEXTURE_KEY == pack.TEXTURE_REFERENCE + ".blp", "texture reference and key drifted"
    assert pack.TEXTURE_SOURCE.is_file(), f"the Freeborn plate is missing: {pack.TEXTURE_SOURCE}"

    assert "CharacterFreeborn_Init" in lua, "lua guard marker is missing"
    assert_load_safe(lua, "payload")

    # The name must reach the server exactly as typed. Every one of these guards a way an earlier
    # revision altered it, and each would break the rule that Freeborn names follow the same rules
    # as Alliance and Horde names.
    assert "CharacterFreeborn_CreateName" not in lua, "the name must not be transformed"
    assert "CreateCharacter(" not in lua, (
        "the wrapper must delegate to the stock accept path, not build the create call itself"
    )
    assert '" "' not in lua, "no space may be injected into a name"
    assert "CharacterFreeborn_NameHash" in lua, "the create screen must record the choice for the addon"

    for binding in FORBIDDEN_BINDINGS:
        assert binding not in lua, f"payload calls a binding this client does not expose: {binding}"

    # Every wrap must capture the previous function and still call it, or the wrapped
    # chain either recurses forever or silently drops the stock behaviour.
    for wrapped, local_name in (
        ("CharacterCreate_CreateGenderButtonTextures", "freeborn_originalGenderTextures"),
        ("CharacterCreate_PositionGenderButtons", "freeborn_originalPositionGenderButtons"),
        ("CharacterCreate_UpdateButtonCheckedStates", "freeborn_originalUpdateButtonCheckedStates"),
        ("CharacterCreate_OnShow", "freeborn_originalOnShow"),
        ("CharacterCreate_Okay", "freeborn_originalOkay"),
    ):
        assert f"local {local_name} = {wrapped};" in lua, f"{wrapped} is not captured before wrapping"
        assert f"{local_name}(...);" in lua, f"{wrapped} is never delegated to"


def assert_tooltip_contract() -> None:
    """The Freeborn pick explains itself on hover, behind the race tooltips' own border."""
    xml = (pack.PAYLOAD_ROOT / "CharacterCreate.freeborn.xml").read_text(encoding="utf-8")
    lua = (pack.PAYLOAD_ROOT / "CharacterCreate.freeborn.lua").read_text(encoding="utf-8")

    # The button no longer borrows the stock one-line GlueTooltip. It runs its own hover pair,
    # guarded the way its OnClick already is, so a half-applied patch cannot take the screen down.
    assert 'GlueTooltip_SetText("Freeborn"' not in xml, "the stock one-line tooltip is still wired"
    for helper in ("CharacterFreeborn_OnEnter", "CharacterFreeborn_OnLeave"):
        assert f"if ( {helper} ) then" in xml, f"{helper} is called unguarded from the XML"
        assert f"{helper}(self);" in xml, f"{helper} is never called from the XML"
        assert f"function {helper}(self)" in lua, f"{helper} is not defined in the payload"

    # Same border as the race tooltips, spelled out rather than borrowed from the stock local.
    tooltip = lua[lua.index("function CharacterFreeborn_GetTooltip()") :]
    tooltip = tooltip[: tooltip.index("\n    end")]
    for field in RACE_TOOLTIP_BACKDROP:
        assert field in tooltip, f"the Freeborn tooltip backdrop is missing {field!r}"
    assert 'CreateFrame("Frame", "CharacterFreebornTooltip", CharacterCreateFrame)' in tooltip, (
        "the tooltip must be a child of the create screen, so it hides with it"
    )
    assert '"TOOLTIP"' in tooltip, "the tooltip must sit on the tooltip strata, like the race ones"
    assert "SetBackdropColor(0, 0, 0, 1)" in tooltip, "the tooltip background must be opaque black"

    # Everything the pick actually does has to be in the hover text. The text is split across
    # adjacent string literals in the source, so sew those back together before searching it.
    body = lua[lua.index("tooltip.body:SetText(") :]
    body = re.sub(r'"\s*\.\.\s*"', "", body[: body.index(");")]).lower()
    for fact in TOOLTIP_FACTS:
        assert fact.lower() in body, f"the hover text says nothing about {fact!r}"

    # Nothing may leave it stuck on screen: off on mouse-out, on a fresh visit to the screen, and
    # in the paid-service path, where the button itself is hidden under a live mouse.
    assert lua.count("CharacterFreeborn_HideTooltip();") >= 3, (
        "the tooltip is not hidden on leave, on a fresh visit, and in the paid-service path"
    )


def assert_xml_transform() -> None:
    patched = pack.patch_character_create_xml(FIXTURE_XML.encode("utf-8"))

    # Well-formedness first: a malformed Glue XML breaks the whole create screen.
    root = ElementTree.fromstring(patched.decode("utf-8"))
    assert root.tag.endswith("Ui"), "patched xml lost its root element"

    text = patched.decode("utf-8")
    container = text.index('<Frame name="CharacterCreateGenderButtonsContainer">')
    button = text.index(f'name="{pack.FREEBORN_BUTTON_NAME}"')
    class_comment = text.index("botones de clase")
    assert container < button < class_comment, "button must land inside the gender-button container"

    female = text.index('name="CharacterCreateGenderButtonFemale"')
    assert female < button, "button must sit after the female pick, i.e. between the gender picks"
    assert 'name="CharacterCreateGenderButtonMale"' in text
    assert 'name="CharacterCreateGenderButtonFemale"' in text

    assert pack.patch_character_create_xml(patched) == patched, "xml transform is not idempotent"
    assert pack.patch_character_create_xml(FIXTURE_XML.encode("utf-8")) == patched, "xml transform is not deterministic"


def assert_lua_transform() -> None:
    original = FIXTURE_LUA.encode("utf-8")
    patched = pack.patch_character_create_lua(original)
    text = patched.decode("utf-8")

    assert text.startswith(FIXTURE_LUA), "lua transform must append, never rewrite stock code"
    assert text.rstrip().endswith(pack.LUA_END), "lua block must be closed by its end sentinel"
    assert pack.LUA_MARKER in text
    assert pack.patch_character_create_lua(patched) == patched, "lua transform is not idempotent"
    assert pack.patch_character_create_lua(original) == patched, "lua transform is not deterministic"

    # Regression for shipped breakage: the first revision had NO sentinels, so a repack appended a
    # second copy rather than replacing it. The stale copy indexed the not-yet-created
    # CharacterCreate frame at load time, which aborted the chunk and stopped the good copy from
    # defining anything -- "attempt to index global 'CharacterCreate' (a nil value)".
    legacy = (
        FIXTURE_LUA
        + "\n"
        + pack.LUA_HEADER_MARKER
        + "\nif not CharacterFreeborn_Init then\n"
        + "    CharacterFreeborn_Init = true;\n"
        + "    CharacterCreate.selectedFreeborn = false;\n"
        + "end\n"
    )
    doubled = (
        legacy + "\n" + pack.LUA_BEGIN + "\n-- stale managed revision\n" + pack.LUA_END + "\n"
    ).encode("utf-8")
    repaired = pack.patch_character_create_lua(doubled).decode("utf-8")
    assert repaired.count(pack.LUA_BEGIN) == 1, "canonicalisation left more than one managed block"
    assert repaired.count(pack.LUA_HEADER_MARKER) == 1, "a stale revision survived canonicalisation"
    assert "stale managed revision" not in repaired, "the stale managed block survived"
    assert "CharacterCreate.selectedFreeborn = false;" not in repaired, (
        "the stale load-time frame access survived"
    )
    assert repaired.startswith(FIXTURE_LUA), "canonicalisation must not disturb stock code"
    assert pack.patch_character_create_lua(repaired.encode("utf-8")) == repaired.encode("utf-8"), (
        "canonicalised output is not idempotent"
    )
    assert_lua_block_shape(repaired, "canonicalised fixture")


def assert_server_contract() -> None:
    handler = (ROOT / "src/server/game/Handlers/CharacterHandler.cpp").read_text(encoding="utf-8")
    player = (ROOT / "src/server/game/Entities/Player/Player.cpp").read_text(encoding="utf-8")
    session = (ROOT / "src/server/game/Server/WorldSession.h").read_text(encoding="utf-8")

    # The name-based carrier is gone for good: no decode, no create-time request, no name in a log.
    assert "FreebornCreateToken" not in handler, "the abandoned name token is still referenced"
    assert "requested a Freeborn character named" not in handler, "the name token is still logged"
    assert "RequestedTeamId" not in handler, "a create-packet team request is still resolved"
    assert "RequestedTeamId" not in session, "CharacterCreateInfo still carries a team request"
    assert "RequestedTeamId" not in player, "Player::Create still applies a create-time team request"

    # Creation is origin-team, and the success log records the team that was persisted.
    assert "InitializeTeamId(TeamIdForRace(createInfo->Race))" in player, "creation must set the origin team"
    assert "(persistent team {})" in handler, "the creation log must record the persisted team"


def assert_claim_contract() -> None:
    """The create screen, the addon and the server must agree, or the claim fails silently."""
    lua = (pack.PAYLOAD_ROOT / "CharacterCreate.freeborn.lua").read_text(encoding="utf-8")
    addon = ADDON_LUA.read_text(encoding="utf-8")
    header = CLAIM_HEADER.read_text(encoding="utf-8")
    chat = CHAT_HANDLER.read_text(encoding="utf-8")

    # Older revisions of the create screen recorded the chosen name in the addon's own CVar; the
    # addon still reads it, because a leftover record from those revisions must stay visible.
    assert 'CVAR = "freebornPending"' in addon, "the addon must read the legacy pending CVar"

    # Every CVar access on the glue screen must be guarded. This client raises
    # "Couldn't find CVar named '<x>'" for any name it does not already know, and an uncaught glue
    # error takes the create screen down with it -- a bare `local before = GetCVar(name)` crashed a
    # live client once. So: wrappers exist, and no line calls either binding outside a pcall.
    assert "function CharacterFreeborn_SafeGet(name)" in lua and "pcall(GetCVar, name)" in lua, (
        "the create screen must read CVars through a guarded wrapper"
    )
    assert "function CharacterFreeborn_SafeSet(name, value)" in lua and "pcall(SetCVar, name, value)" in lua, (
        "the create screen must write CVars through a guarded wrapper"
    )
    bare = [
        line.strip()
        for line in lua.splitlines()
        if ("SetCVar(" in line or "GetCVar(" in line) and "pcall(" not in line
    ]
    assert not bare, f"unguarded CVar access on the glue screen: {bare}"

    # Anything the glue screen runs on the select screen's behalf must be inside a pcall, and an
    # argument passed to pcall is evaluated first, so a builder may never be handed to pcall as an
    # argument. That is what threw "Usage: GetFactionForRace(index)" on a live select screen.
    for name in ("CharacterFreeborn_ApplyBadges",):
        assert f"pcall({name})" in lua, f"{name} must be pcall'd by its caller"

    # The carrier has to be the same cvar names on both sides, both sides have to hash a name
    # identically, and every carrier the glue writes has to be one the addon puts back.
    glue_list = re.search(r"CharacterFreeborn_CarrierCVars = \{([^}]*)\}", lua)
    assert glue_list, "the glue carrier list is missing"
    addon_list = re.search(r"CARRIERS = \{([^}]*)\}", addon)
    assert addon_list, "the addon carrier list is missing"
    glue_carriers = re.findall(r'"([^"]+)"', glue_list.group(1))
    assert glue_carriers == re.findall(r'"([^"]+)"', addon_list.group(1)), (
        "the glue and the addon disagree about which cvars carry the choice"
    )
    for carrier in glue_carriers:
        assert f"{carrier} = " in addon, f"the addon never puts {carrier} back"
    assert "CharacterFreeborn_NameHash" in lua and "local function NameHash" in addon, (
        "both sides must hash the name"
    )

    # The badge slots, and the record encoding, must be identical on both sides: a drift here shows
    # no emblem at all and fails silently. The encoding must also stay inside INT_MAX, because a
    # value this client cannot parse as a number is refused outright.
    glue_slots = re.search(r"CharacterFreeborn_BadgeCVars = \{([^}]*)\}", lua)
    assert glue_slots, "the glue badge slot list is missing"
    addon_slots = re.search(r"BADGES = \{([^}]*)\}", addon)
    assert addon_slots, "the addon badge slot list is missing"
    glue_slots_list = re.findall(r'"([^"]+)"', glue_slots.group(1))
    assert glue_slots_list == re.findall(r'"([^"]+)"', addon_slots.group(1)), (
        "the glue and the addon disagree about where the badge records live"
    )
    assert not (set(glue_slots_list) & set(glue_carriers)), (
        "a badge slot is also a claim carrier, so claiming would erase the emblem memory"
    )
    # The emblem is read on the character-select screen at the START of a session, so its memory
    # must survive a client restart. Every integer cvar tried was normalised when the client loaded
    # it: readTOS/readEULA became "1" and gameTip had a record clipped to a valid tip index, with
    # the value still sitting on disk. The store must therefore be a string cvar the client never
    # parses -- never put the emblem back into one of these.
    NEVER_EMBLEM_MEMORY = {
        "readTOS", "readEULA", "gameTip", "checkAddonVersion", "showGameTips", "screenshotQuality",
        "hwDetect", "lastCharacterIndex", "showToolsUI", "taintLog",
    }
    assert not (set(glue_slots_list) & set(NEVER_EMBLEM_MEMORY)), (
        f"the client parses {sorted(set(glue_slots_list) & set(NEVER_EMBLEM_MEMORY))} as a number at "
        "startup, so an emblem record there is gone before the character-select screen can read it"
    )
    record_base = re.search(r"CharacterFreeborn_RecordBase = (\d+)", lua)
    record_mod = re.search(r"CharacterFreeborn_RecordMod = (\d+)", lua)
    assert record_base and record_mod, "the glue record encoding is missing"
    assert f"RECORD_BASE = {record_base.group(1)}" in addon, "the two sides encode records differently"
    assert f"RECORD_MOD = {record_mod.group(1)}" in addon, "the two sides encode records differently"
    assert int(record_base.group(1)) + int(record_mod.group(1)) - 1 <= 2147483647, (
        "a record could exceed INT_MAX, which is the range this client will store"
    )
    badge_texture = re.search(r'CharacterFreeborn_BadgeTexture = "([^"]+)"', lua)
    assert badge_texture, "the glue badge texture is missing"
    assert badge_texture.group(1).replace("\\\\", "\\") == pack.BADGE_REFERENCE, (
        "the select screen points at a different emblem than the packer ships"
    )
    assert pack.BADGE_KEY == pack.BADGE_REFERENCE + ".blp", "badge texture reference and key drifted"
    assert 'Print("pending=' in addon, "the status command must report the bridge state"

    # One addon-message envelope, sent by the addon and matched by the server.
    assert 'local PREFIX = "FREEBORN";' in addon, "the addon prefix changed"
    assert 'local CLAIM = "claim";' in addon, "the addon body changed"
    assert 'local STATUS = "status";' in addon, "the addon status body changed"
    assert 'SendAddonMessage(PREFIX, body, "WHISPER", UnitName("player"))' in addon, (
        "the addon must whisper to itself, the channel this project already uses"
    )
    assert "Send(CLAIM);" in addon, "the addon must send the claim"
    assert 'AddonPrefix = "FREEBORN"' in header, "the server prefix does not match the addon"
    assert 'ClaimBody = "claim"' in header, "the server claim body does not match the addon"
    assert 'StatusBody = "status"' in header, "the server status body does not match the addon"
    assert 'ClaimEnvelope = "FREEBORN\\tclaim"' in header, "the claim envelope does not match the addon"
    assert 'StatusEnvelope = "FREEBORN\\tstatus"' in header, "the status envelope does not match the addon"

    # The status readout is what a player uses to check which team they are on, so it has to be
    # reachable in game without any GM permission.
    assert 'SLASH_FREEBORN1 = "/freeborn";' in addon, "the player-facing status command is missing"
    assert 'SlashCmdList["FREEBORN"]' in addon, "the slash command is not registered"
    assert "Send(STATUS);" in addon, "the slash command must request the status"
    # A character claimed before this addon kept records still needs a way to get its emblem.
    assert 'strlower(msg) == "claim"' in addon and "ForceClaim()" in addon, (
        "the slash command must accept `claim` so an existing Freeborn character can be badged"
    )

    # The server must actually be reached from the addon-message path.
    assert "FreebornClaim::HandleAddonMessage(sender, msg)" in chat, "the claim is never handled"
    assert '#include "FreebornClaim.h"' in chat, "the claim header is not included"

    # The addon must only claim the character it was told about, must clear the record first, and
    # must hand the borrowed carrier cvar back, in that order.
    assert 'strlower(name) == strlower(pending)' in addon, "the addon must match the pending name"
    assert "NameHash" in addon and "carrier" in addon, "the addon must also match the carrier hash"
    assert addon.index('SafeSet(CVAR, "")') < addon.index("Send(CLAIM);"), (
        "the record must be cleared before sending, so a reload cannot claim twice"
    )
    assert addon.index("SafeSet(carrier, CARRIER_RESTORE[carrier]);") < addon.index("Send(CLAIM);"), (
        "every borrowed carrier cvar must be given back before the claim is sent"
    )
    assert 'RegisterEvent("PLAYER_ENTERING_WORLD")' in addon, "the addon must hook world entry"
    # The claim must NOT be gated on isInitialLogin. That gate silently never opened on a live
    # client -- the carriers stayed armed and nothing happened -- so the safety property is
    # "clear before send" (asserted above), and a failure has to be visible in chat.
    assert "if ( not isInitialLogin ) then" not in addon, (
        "the claim must not be gated on isInitialLogin; that gate silently never opened"
    )
    assert "pcall(ClaimIfChosen" in addon, "the world-entry check must be pcall'd"
    assert 'Print("error while checking the create screen' in addon, (
        "a failure in the world-entry check must be visible in chat"
    )


def assert_team_id_reads_are_byte_wide() -> None:
    """`teamId` is TINYINT UNSIGNED, so it must be read as uint8.

    Field::GetData interprets a raw prepared-statement field with
    `*reinterpret_cast<T const*>(data.value)`, so asking for uint32 on a one-byte column reads the
    neighbouring row bytes. That is what produced "Character 478 has invalid persistent team id
    122624" and silently dropped characters out of the character list.
    """
    sources = {
        name: ROOT / relative
        for name, relative in (
            ("Player.cpp", "src/server/game/Entities/Player/Player.cpp"),
            ("PlayerStorage.cpp", "src/server/game/Entities/Player/PlayerStorage.cpp"),
            ("CharacterCache.cpp", "src/server/game/Cache/CharacterCache.cpp"),
            ("CharacterHandler.cpp", "src/server/game/Handlers/CharacterHandler.cpp"),
            ("cs_character.cpp", "src/server/scripts/Commands/cs_character.cpp"),
        )
    }

    # The exact expressions that were wrong, scoped to the file whose statement they belong to.
    # A looser "any line mentioning team" heuristic also flags the guid reads and `arenaTeamId`,
    # which are legitimately uint32.
    banned = {
        "Player.cpp": ("teamField.Get<uint32>()",),
        "PlayerStorage.cpp": ("fields[75].Get<uint32>()",),
        "CharacterCache.cpp": ("fields[7].Get<uint32>()",),
        "CharacterHandler.cpp": ("fields[3].Get<uint32>()",),
        "cs_character.cpp": ("fields[4].Get<uint32>()",),
    }
    for name, literals in banned.items():
        text = sources[name].read_text(encoding="utf-8")
        for literal in literals:
            assert literal not in text, f"{name}: teamId read with the wrong field width: {literal}"

    expected = (
        "uint32 const persistentTeamId = teamField.Get<uint8>();",
        "uint32 const persistentTeamId = fields[75].Get<uint8>();",
        "uint32 const persistentTeamId = fields[7].Get<uint8>();",
        "uint32 const oldPersistentTeamValue = fields[3].Get<uint8>();",
        "uint32 const teamIdValue = fields[4].Get<uint8>();",
    )
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in sources.values())
    for literal in expected:
        assert literal in corpus, f"missing byte-wide teamId read: {literal}"


def assert_live_archives(client: Path) -> None:
    """Once installed, both archives must agree; a half-applied patch is a failure."""
    from cars_mount_pack import DLL_DEFAULT, Storm

    storm = Storm(DLL_DEFAULT)
    for archive_path in (
        client / "Data" / pack.ARCHIVE_NAME,
        client / "Data" / "enUS" / pack.LOCALE_ARCHIVE_NAME,
    ):
        is_root = archive_path == client / "Data" / pack.ARCHIVE_NAME
        handle = storm.open_archive(archive_path)
        try:
            xml = storm.read(handle, pack.GLUE_ROOT + "CharacterCreate.xml").decode("utf-8")
            lua = storm.read(handle, pack.GLUE_ROOT + "CharacterCreate.lua").decode("utf-8")
            # The addon rides the root archive only.
            addon = (
                {
                    entry: storm.read(handle, entry)
                    for entry in (
                        *(pack.ADDON_ROOT + name for name in pack.ADDON_FILES),
                        pack.TEXTURE_KEY,
                    )
                }
                if is_root
                else {}
            )
        finally:
            storm.dll.SFileCloseArchive(handle)

        has_button = pack.FREEBORN_BUTTON_NAME in xml
        has_marker = pack.LUA_MARKER in lua
        assert has_button == has_marker, f"{archive_path.name} is half-patched"
        state = "installed" if has_button else "not installed"
        print(f"  {archive_path.name}: {state}")
        if has_button:
            assert_vocabulary_is_stock(xml)
            assert_xml_button_shape(xml, archive_path.name)
            assert_lua_block_shape(lua, archive_path.name)
            assert '" "' not in lua.split(pack.LUA_BEGIN)[1], (
                f"{archive_path.name}: a space is being injected into names"
            )
            # The Freeborn tooltip wears the race tooltips' border. Both halves of that claim are
            # read out of the deployed file: the stock prefix still has to carry those settings, and
            # the managed block has to repeat them.
            stock, installed = lua.split(pack.LUA_BEGIN, 1)
            for field in RACE_TOOLTIP_BACKDROP:
                assert field in stock, (
                    f"{archive_path.name}: the stock race tooltips no longer use {field!r}, so the "
                    "Freeborn tooltip border no longer matches them"
                )
                assert field in installed, (
                    f"{archive_path.name}: the deployed Freeborn tooltip is missing {field!r}"
                )

        # The addon and the plate ride the root archive only; nothing at those paths exists in the
        # locale archives, so there is nothing to shadow there.
        if is_root:
            sources = {
                **{pack.ADDON_ROOT + name: pack.ADDON_SOURCE / name for name in pack.ADDON_FILES},
                pack.TEXTURE_KEY: pack.TEXTURE_SOURCE,
            }
            for entry, payload in addon.items():
                assert payload == sources[entry].read_bytes(), (
                    f"{archive_path.name}: {entry} does not match the payload"
                )


def main() -> None:
    assert_payloads()
    assert_tooltip_contract()
    print("payloads: PASS")
    assert_xml_transform()
    assert_lua_transform()
    print("transforms: PASS")
    assert_server_contract()
    print("server contract: PASS")
    assert_claim_contract()
    print("claim contract: PASS")
    assert_team_id_reads_are_byte_wide()
    print("teamId field width: PASS")

    client = client_root()
    if client is None:
        print("live archives: SKIP (client not found)")
    else:
        assert_live_archives(client)
        print("live archives: PASS")

    print("freeborn create contract: PASS")


if __name__ == "__main__":
    main()
