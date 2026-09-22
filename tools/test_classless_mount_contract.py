from pathlib import Path


SOURCE = Path("modules/mod-classless-wildcard/src/ClasslessMgr.cpp")


def test_mounted_spells_are_excluded_before_classless_skill_registration():
    text = SOURCE.read_text(encoding="utf-8")
    guard = "if (IsMountedSpell(info))"
    mapping = "_spellSkillLine[sla->Spell]"

    assert "SPELL_AURA_MOUNTED" in text
    assert guard in text
    assert text.index(guard) < text.index(mapping)
    assert "_mountSkillLines" in text
    mount_block = text.split(guard, 1)[1].split("// Remember which tab", 1)[0]
    assert "_classSkillLines.insert" in mount_block
    assert "_mountSkillLines.count(line)" in text


def test_persistent_learn_reaches_temporary_spell_promotion():
    text = Path("src/server/game/Entities/Player/Player.cpp").read_text(encoding="utf-8")
    learn = text.split("void Player::learnSpell", 1)[1].split("uint8 Player::GetLearnSpellSpecMask", 1)[0]

    assert "PlayerSpellMap::iterator itr = m_spells.find(spellId);" in learn
    assert "itr == m_spells.end() || itr->second->State != PLAYERSPELL_TEMPORARY || temporary" in learn


def test_owned_mounts_create_the_mounts_skill_line_and_refresh_immediately():
    manager = SOURCE.read_text(encoding="utf-8")
    sync = manager.split("void ClasslessMgr::SyncSpellbookTabs", 1)[1]
    sync = sync.split("void ClasslessMgr::UpdateAbilityRanks", 1)[0]
    assert "if (hasMountOnLine)" in sync
    assert "want.insert(line);" in sync

    player = Path("modules/mod-classless-wildcard/src/ClasslessPlayerScript.cpp").read_text(encoding="utf-8")
    learn = player.split("void OnPlayerLearnSpell", 1)[1].split("// revert after the learn completes", 1)[0]
    assert "spellInfo->HasAura(SPELL_AURA_MOUNTED)" in learn
    assert "sClasslessMgr->SyncSpellbookTabs(player);" in learn


if __name__ == "__main__":
    test_mounted_spells_are_excluded_before_classless_skill_registration()
    test_persistent_learn_reaches_temporary_spell_promotion()
    test_owned_mounts_create_the_mounts_skill_line_and_refresh_immediately()
    print("classless mount contract: PASS")
