/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "CharacterDatabase.h"
#include "MySQLPreparedStatement.h"

void CharacterDatabaseConnection::DoPrepareStatements()
{
    if (!m_reconnecting)
        m_stmts.resize(MAX_CHARACTERDATABASE_STATEMENTS);

    PrepareStatement(CHAR_INS_ESTERIA_BACKPACK_APPEARANCE,
        "INSERT IGNORE INTO custom_unlocked_appearances (account_id, item_template_id) VALUES (?, ?)", CONNECTION_ASYNC);

    PrepareStatement(CHAR_DEL_QUEST_POOL_SAVE, "DELETE FROM pool_quest_save WHERE pool_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_QUEST_POOL_SAVE, "INSERT INTO pool_quest_save (pool_id, quest_id) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_NONEXISTENT_GUILD_BANK_ITEM, "DELETE FROM guild_bank_item WHERE guildid = ? AND TabId = ? AND SlotId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_EXPIRED_BANS, "UPDATE character_banned SET active = 0 WHERE unbandate <= UNIX_TIMESTAMP() AND unbandate <> bandate", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_DATA_BY_NAME, "SELECT guid, account, name, gender, race, class, level FROM characters WHERE deleteDate IS NULL AND name = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_DATA_BY_GUID, "SELECT guid, account, name, gender, race, class, level FROM characters WHERE deleteDate IS NULL AND guid = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_CHECK_NAME, "SELECT 1 FROM characters WHERE name = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_CHECK_GUID, "SELECT 1 FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_SUM_CHARS, "SELECT COUNT(guid) FROM characters WHERE account = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_CHAR_CREATE_INFO, "SELECT level, race, class FROM characters WHERE account = ? LIMIT 0, ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_BAN, "INSERT INTO character_banned VALUES (?, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()+?, ?, ?, 1)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHARACTER_BAN, "UPDATE character_banned SET active = 0 WHERE guid = ? AND active != 0", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHARACTER_BAN, "DELETE cb FROM character_banned cb INNER JOIN characters c ON c.guid = cb.guid WHERE c.account = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_BANINFO, "SELECT FROM_UNIXTIME(bandate, '%Y-%m-%d %H:%i:%s'), unbandate-bandate, active, unbandate, banreason, bannedby FROM character_banned WHERE guid = ? ORDER BY bandate ASC", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_GUID_BY_NAME_FILTER, "SELECT guid, name FROM characters WHERE name LIKE CONCAT('%%', ?, '%%')", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_BANINFO_LIST, "SELECT bandate, unbandate, bannedby, banreason FROM character_banned WHERE guid = ? ORDER BY unbandate", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_BANNED_NAME, "SELECT characters.name FROM characters, character_banned WHERE character_banned.guid = ? AND character_banned.guid = characters.guid", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ENUM, "SELECT c.guid, c.name, c.race, c.class, c.gender, c.skin, c.face, c.hairStyle, c.hairColor, c.facialStyle, c.level, c.zone, c.map, c.position_x, c.position_y, c.position_z, "
                     "gm.guildid, c.playerFlags, c.at_login, cp.entry, cp.modelid, cp.level, "
                     "c.equipmentCache, cb.guid, c.extra_flags, c.extraAppearance, c.teamId "
                     "FROM characters AS c LEFT JOIN character_pet AS cp ON c.guid = cp.owner "
                     "AND cp.slot = ? "
                     "LEFT JOIN guild_member AS gm ON c.guid = gm.guid "
                     "LEFT JOIN character_banned AS cb ON c.guid = cb.guid AND cb.active = 1 WHERE c.account = ? AND c.deleteInfos_Name IS NULL ORDER BY COALESCE(c.order, c.guid)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ENUM_DECLINED_NAME, "SELECT c.guid, c.name, c.race, c.class, c.gender, c.skin, c.face, c.hairStyle, c.hairColor, c.facialStyle, c.level, c.zone, c.map, "
                     "c.position_x, c.position_y, c.position_z, gm.guildid, c.playerFlags, c.at_login, cp.entry, cp.modelid, cp.level, c.equipmentCache, "
                     "cb.guid, c.extra_flags, cd.genitive, c.extraAppearance, c.teamId "
                     "FROM characters AS c LEFT JOIN character_pet AS cp ON c.guid = cp.owner "
                     "AND cp.slot = ? "
                     "LEFT JOIN character_declinedname AS cd ON c.guid = cd.guid LEFT JOIN guild_member AS gm ON c.guid = gm.guid "
                     "LEFT JOIN character_banned AS cb ON c.guid = cb.guid AND cb.active = 1 WHERE c.account = ? AND c.deleteInfos_Name IS NULL ORDER BY COALESCE(c.order, c.guid)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_FREE_NAME, "SELECT guid, name, at_login FROM characters WHERE guid = ? AND account = ? AND NOT EXISTS (SELECT NULL FROM characters WHERE name = ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ENUM_PERMANENT_AURAS, "SELECT a.guid, a.spell FROM character_aura AS a "
                     "JOIN characters AS c ON c.guid = a.guid WHERE c.account = ? "
                     "AND c.deleteInfos_Name IS NULL AND a.casterGuid = a.guid AND a.remainTime = -1 "
                     "ORDER BY a.guid, a.spell", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_ZONE, "SELECT zone FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHARACTER_NAME_DATA,
                     "SELECT race, class, gender, level, teamId FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_POSITION_XYZ, "SELECT map, position_x, position_y, position_z FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_POSITION, "SELECT position_x, position_y, position_z, orientation, map, taxi_path FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_DAILY, "DELETE FROM character_queststatus_daily", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_WEEKLY, "DELETE FROM character_queststatus_weekly", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_MONTHLY, "DELETE FROM character_queststatus_monthly", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_SEASONAL, "DELETE FROM character_queststatus_seasonal WHERE event = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_DAILY_CHAR, "DELETE FROM character_queststatus_daily WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_WEEKLY_CHAR, "DELETE FROM character_queststatus_weekly WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_MONTHLY_CHAR, "DELETE FROM character_queststatus_monthly WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_QUEST_STATUS_SEASONAL_CHAR, "DELETE FROM character_queststatus_seasonal WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_BATTLEGROUND_RANDOM, "DELETE FROM character_battleground_random", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_BATTLEGROUND_RANDOM, "INSERT INTO character_battleground_random (guid) VALUES (?)", CONNECTION_ASYNC);

    // Start LoginQueryHolder content
    PrepareStatement(CHAR_SEL_CHARACTER, "SELECT guid, account, name, race, class, gender, level, xp, money, skin, face, hairStyle, hairColor, facialStyle, bankSlots, restState, playerFlags, "
                     "position_x, position_y, position_z, map, orientation, taximask, cinematic, totaltime, leveltime, rest_bonus, logout_time, is_logout_resting, resettalents_cost, "
                     "resettalents_time, trans_x, trans_y, trans_z, trans_o, transguid, extra_flags, stable_slots, at_login, zone, online, death_expire_time, taxi_path, instance_mode_mask, "
                     "arenaPoints, totalHonorPoints, todayHonorPoints, yesterdayHonorPoints, totalKills, todayKills, yesterdayKills, chosenTitle, knownCurrencies, watchedFaction, drunk, "
                     "health, power1, power2, power3, power4, power5, power6, power7, instance_id, talentGroupsCount, activeTalentGroup, exploredZones, equipmentCache, ammoId, "
                     "knownTitles, actionBars, grantableLevels, innTriggerId, extraBonusTalentCount, "
                     "UNIX_TIMESTAMP(creation_date), "
                     "teamId, extraAppearance FROM characters WHERE guid = ?", CONNECTION_ASYNC);

    PrepareStatement(CHAR_UPD_EXTENDED_APPEARANCE,
        "UPDATE characters SET extraAppearance = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ENUM_BODY_SHAPE,
        "SELECT b.guid, b.data FROM character_body_shape AS b JOIN characters AS c ON c.guid = b.guid "
        "WHERE c.account = ? AND c.deleteInfos_Name IS NULL", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ENUM_RETAIL_LOOK,
        "SELECT l.guid, l.data, 0 FROM character_retail_look AS l JOIN characters AS c ON c.guid = l.guid "
        "WHERE c.account = ? AND c.deleteInfos_Name IS NULL "
        "UNION ALL SELECT f.guid, f.data, 1 FROM character_form_look AS f JOIN characters AS c ON c.guid = f.guid "
        "WHERE c.account = ? AND c.deleteInfos_Name IS NULL", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MOUNT_LOOKS,
        "SELECT display, choices FROM character_mount_look WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_MOUNT_LOOK,
        "REPLACE INTO character_mount_look (guid, display, choices) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_INCARNATIONS,
        "SELECT category, display FROM character_incarnation WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_INCARNATION,
        "REPLACE INTO character_incarnation (guid, category, display) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INCARNATION,
        "DELETE FROM character_incarnation WHERE guid = ? AND category = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_RETAIL_LOOK,
        "SELECT data FROM character_retail_look WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_RETAIL_LOOK,
        "REPLACE INTO character_retail_look (guid, data) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_RETAIL_LOOK,
        "DELETE FROM character_retail_look WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_FORM_LOOK,
        "SELECT data FROM character_form_look WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_FORM_LOOK,
        "REPLACE INTO character_form_look (guid, data) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_FORM_LOOK,
        "DELETE FROM character_form_look WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_BODY_SHAPE,
        "SELECT data FROM character_body_shape WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_BODY_SHAPE,
        "REPLACE INTO character_body_shape (guid, data) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_BODY_SHAPE,
        "DELETE FROM character_body_shape WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_PERK_PROFILE,
        "REPLACE INTO character_esteria_perk_profile (guid, trait) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PERK_PROFILE,
        "DELETE FROM character_esteria_perk_profile WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PERK_PROFILE,
        "SELECT trait, respecs FROM character_esteria_perk_profile WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_PERK_RESPECS,
        "INSERT INTO character_esteria_perk_profile (guid, respecs) VALUES (?, ?) "
        "ON DUPLICATE KEY UPDATE respecs = VALUES(respecs)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PERKS,
        "SELECT perk, `rank` FROM character_esteria_perks WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_PERK,
        "REPLACE INTO character_esteria_perks (guid, perk, `rank`) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PERKS,
        "DELETE FROM character_esteria_perks WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PERK_AUDIT,
        "INSERT INTO esteria_perk_audit (guid, time, action, perk, `rank`, level, spent, gold) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_PERK_TRAIT,
        "INSERT INTO character_esteria_perk_profile (guid, trait) VALUES (?, ?) "
        "ON DUPLICATE KEY UPDATE trait = VALUES(trait)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_TRAITS,
        "SELECT trait_id FROM character_esteria_trait_selection WHERE guid = ? ORDER BY trait_id", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_TRAIT,
        "INSERT INTO character_esteria_trait_selection (guid, trait_id, selected_at) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_TRAITS,
        "DELETE FROM character_esteria_trait_selection WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_TRAIT_STATE,
        "SELECT respecs FROM character_esteria_trait_state WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_TRAIT_STATE,
        "REPLACE INTO character_esteria_trait_state (guid, respecs, changed) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_TRAIT_STATE,
        "DELETE FROM character_esteria_trait_state WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_TRAIT_AUDIT,
        "INSERT INTO esteria_trait_audit (guid, time, action, `before`, `after`, gold) VALUES (?, ?, ?, ?, ?, ?)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_EYE_LIGHTNING,
        "UPDATE characters SET extraAppearance = (extraAppearance & 9223372036854775807) | ? WHERE guid = ?",
        CONNECTION_ASYNC);

    PrepareStatement(CHAR_SEL_CHARACTER_AURAS, "SELECT casterGuid, itemGuid, spell, effectMask, recalculateMask, stackCount, amount0, amount1, amount2, "
                     "base_amount0, base_amount1, base_amount2, maxDuration, remainTime, remainCharges FROM character_aura WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_SPELL, "SELECT spell, specMask FROM character_spell WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_QUESTSTATUS, "SELECT quest, status, explored, timer, mobcount1, mobcount2, mobcount3, mobcount4, "
                     "itemcount1, itemcount2, itemcount3, itemcount4, itemcount5, itemcount6, playercount FROM character_queststatus WHERE guid = ? AND status <> 0", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_DAILYQUESTSTATUS, "SELECT quest, time FROM character_queststatus_daily WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_WEEKLYQUESTSTATUS, "SELECT quest FROM character_queststatus_weekly WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_MONTHLYQUESTSTATUS, "SELECT quest FROM character_queststatus_monthly WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_SEASONALQUESTSTATUS, "SELECT quest, event FROM character_queststatus_seasonal WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_DAILYQUESTSTATUS, "INSERT INTO character_queststatus_daily (guid, quest, time) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_WEEKLYQUESTSTATUS, "INSERT INTO character_queststatus_weekly (guid, quest) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_MONTHLYQUESTSTATUS, "INSERT INTO character_queststatus_monthly (guid, quest) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_SEASONALQUESTSTATUS, "INSERT IGNORE INTO character_queststatus_seasonal (guid, quest, event) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_REPUTATION, "SELECT faction, standing, flags FROM character_reputation WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_INVENTORY, "SELECT creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text, bag, slot, "
                     "item, itemEntry FROM character_inventory ci JOIN item_instance ii ON ci.item = ii.guid WHERE ci.guid = ? ORDER BY bag, slot", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_ACTIONS, "SELECT a.button, a.action, a.type FROM character_action as a, characters as c WHERE a.guid = c.guid AND a.spec = c.activeTalentGroup AND a.guid = ? ORDER BY button", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_MAILCOUNT_UNREAD, "SELECT COUNT(id) FROM mail WHERE receiver = ? AND (checked & 1) = 0 AND deliver_time <= ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_MAILCOUNT_UNREAD_SYNCH, "SELECT COUNT(id) FROM mail WHERE receiver = ? AND (checked & 1) = 0 AND deliver_time <= ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MAIL_SERVER_CHARACTER, "SELECT mailId from mail_server_character WHERE guid = ? and mailId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_MAIL_SERVER_CHARACTER, "REPLACE INTO mail_server_character (guid, mailId) values (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_SOCIALLIST, "SELECT friend, flags, note FROM character_social JOIN characters ON characters.guid = character_social.friend WHERE character_social.guid = ? AND deleteinfos_name IS NULL LIMIT 255", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_HOMEBIND, "SELECT mapId, zoneId, posX, posY, posZ FROM character_homebind WHERE guid = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_CHARACTER_SPELLCOOLDOWNS, "SELECT spell, category, item, time, needSend FROM character_spell_cooldown WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_DECLINEDNAMES, "SELECT genitive, dative, accusative, instrumental, prepositional FROM character_declinedname WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_ACHIEVEMENTS, "SELECT achievement, date FROM character_achievement WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_CRITERIAPROGRESS, "SELECT criteria, counter, date FROM character_achievement_progress WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_EQUIPMENTSETS, "SELECT setguid, setindex, name, iconname, ignore_mask, item0, item1, item2, item3, item4, item5, item6, item7, item8, "
                     "item9, item10, item11, item12, item13, item14, item15, item16, item17, item18 FROM character_equipmentsets WHERE guid = ? ORDER BY setindex", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_ENTRY_POINT, "SELECT joinX, joinY, joinZ, joinO, joinMapId, taxiPath0, taxiPath1, mountSpell FROM character_entry_point WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_GLYPHS, "SELECT talentGroup, glyph1, glyph2, glyph3, glyph4, glyph5, glyph6 FROM character_glyphs WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_TALENTS, "SELECT spell, specMask FROM character_talent WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_SKILLS, "SELECT skill, value, max FROM character_skills WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_RANDOMBG, "SELECT guid FROM character_battleground_random WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_BANNED, "SELECT guid FROM character_banned WHERE guid = ? AND active = 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_QUESTSTATUSREW, "SELECT quest FROM character_queststatus_rewarded WHERE guid = ? AND active = 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ACCOUNT_INSTANCELOCKTIMES, "SELECT instanceId, releaseTime FROM account_instance_times WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_BREW_OF_THE_MONTH, "SELECT lastEventId FROM character_brew_of_the_month WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_BREW_OF_THE_MONTH, "REPLACE INTO character_brew_of_the_month (guid, lastEventId) VALUES (?, ?)", CONNECTION_ASYNC);
    // End LoginQueryHolder content

    PrepareStatement(CHAR_SEL_CHARACTER_ACTIONS_SPEC, "SELECT button, action, type FROM character_action WHERE guid = ? AND spec = ? ORDER BY button", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MAILITEMS, "SELECT creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text, item_guid, itemEntry, ii.owner_guid, m.id FROM mail_items mi INNER JOIN mail m ON mi.mail_id = m.id LEFT JOIN item_instance ii ON mi.item_guid = ii.guid WHERE m.receiver = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_SEL_AUCTION_ITEMS, "SELECT creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text, itemguid, itemEntry FROM auctionhouse ah JOIN item_instance ii ON ah.itemguid = ii.guid", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_AUCTIONS, "SELECT id, houseid, itemguid, itemEntry, count, itemowner, buyoutprice, time, buyguid, lastbid, startbid, deposit FROM auctionhouse ah INNER JOIN item_instance ii ON ii.guid = ah.itemguid", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_AUCTION, "INSERT INTO auctionhouse (id, houseid, itemguid, itemowner, buyoutprice, time, buyguid, lastbid, startbid, deposit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_AUCTION, "DELETE FROM auctionhouse WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_AUCTION_BID, "UPDATE auctionhouse SET buyguid = ?, lastbid = ? WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_MAIL, "INSERT INTO mail(id, messageType, stationery, mailTemplateId, sender, receiver, subject, body, has_items, expire_time, deliver_time, money, cod, checked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_MAIL_BY_ID, "DELETE FROM mail WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_MAIL_ITEM, "INSERT INTO mail_items(mail_id, item_guid, receiver) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_MAIL_ITEM, "DELETE FROM mail_items WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_MAIL_ITEM, "DELETE FROM mail_items WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_EXPIRED_MAIL, "SELECT id, messageType, sender, receiver, has_items, expire_time, stationery, checked, mailTemplateId FROM mail WHERE expire_time < ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_EXPIRED_MAIL_ITEMS, "SELECT item_guid, itemEntry, mail_id FROM mail_items mi INNER JOIN item_instance ii ON ii.guid = mi.item_guid LEFT JOIN mail mm ON mi.mail_id = mm.id WHERE mm.id IS NOT NULL AND mm.expire_time < ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_UPD_MAIL_RETURNED, "UPDATE mail SET sender = ?, receiver = ?, expire_time = ?, deliver_time = ?, cod = 0, checked = ? WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_MAIL_ITEM_RECEIVER, "UPDATE mail_items SET receiver = ? WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ITEM_OWNER, "UPDATE item_instance SET owner_guid = ? WHERE guid = ?", CONNECTION_ASYNC);

    PrepareStatement(CHAR_SEL_ITEM_REFUNDS, "SELECT player_guid, paidMoney, paidExtendedCost FROM item_refund_instance WHERE item_guid = ? AND player_guid = ? LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ITEM_BOP_TRADE, "SELECT allowedPlayers FROM item_soulbound_trade_data WHERE itemGuid = ? LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_ITEM_BOP_TRADE, "DELETE FROM item_soulbound_trade_data WHERE itemGuid = ? LIMIT 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ITEM_BOP_TRADE, "INSERT INTO item_soulbound_trade_data VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_INVENTORY_ITEM, "REPLACE INTO character_inventory (guid, bag, slot, item) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_ITEM_INSTANCE, "REPLACE INTO item_instance (itemEntry, owner_guid, creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text, guid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ITEM_INSTANCE, "UPDATE item_instance SET itemEntry = ?, owner_guid = ?, creatorGuid = ?, giftCreatorGuid = ?, count = ?, duration = ?, charges = ?, flags = ?, enchantments = ?, randomPropertyId = ?, durability = ?, playedTime = ?, text = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ITEM_INSTANCE_ON_LOAD, "UPDATE item_instance SET duration = ?, flags = ?, durability = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ITEM_COUNT, "UPDATE item_instance SET count = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ITEM_INSTANCE, "DELETE FROM item_instance WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ITEM_INSTANCE_BY_OWNER, "DELETE FROM item_instance WHERE owner_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GIFT_OWNER, "UPDATE character_gifts SET guid = ? WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GIFT, "DELETE FROM character_gifts WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_GIFT_BY_ITEM, "SELECT entry, flags FROM character_gifts WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ACCOUNT_BY_NAME, "SELECT account FROM characters WHERE name = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_ACCOUNT_INSTANCE_LOCK_TIMES, "DELETE FROM account_instance_times WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ACCOUNT_INSTANCE_LOCK_TIMES, "INSERT INTO account_instance_times (accountId, instanceId, releaseTime) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MATCH_MAKER_RATING, "SELECT matchMakerRating, maxMMR  FROM character_arena_stats WHERE guid = ? AND slot = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHARACTER_COUNT, "SELECT account, COUNT(guid) FROM characters WHERE account = ? GROUP BY account", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_NAME_BY_GUID, "UPDATE characters SET name = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_DECLINED_NAME, "DELETE FROM character_declinedname WHERE guid = ?", CONNECTION_ASYNC);

    // Guild handling
    // 0: uint32, 1: string, 2: uint32, 3: string, 4: string, 5: uint64, 6-10: uint32, 11: uint64
    PrepareStatement(CHAR_INS_GUILD, "INSERT INTO guild (guildid, name, leaderguid, info, motd, createdate, EmblemStyle, EmblemColor, BorderStyle, BorderColor, BackgroundColor, BankMoney) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD, "DELETE FROM guild WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    // 0: string, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_NAME, "UPDATE guild SET name = ? WHERE guildid = ?", CONNECTION_ASYNC);
    // 0: uint32, 1: uint32, 2: uint8, 4: string, 5: string
    PrepareStatement(CHAR_INS_GUILD_MEMBER, "INSERT INTO guild_member (guildid, guid, `rank`, pnote, offnote) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_MEMBER, "DELETE FROM guild_member WHERE guid = ?", CONNECTION_ASYNC); // 0: uint32
    PrepareStatement(CHAR_DEL_GUILD_MEMBERS, "DELETE FROM guild_member WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    PrepareStatement(CHAR_SEL_GUILD_MEMBER_EXTENDED, "SELECT g.guildid, g.name, gr.rname, gm.pnote, gm.offnote "
                     "FROM guild g JOIN guild_member gm ON g.guildid = gm.guildid "
                     "JOIN guild_rank gr ON g.guildid = gr.guildid AND gm.`rank` = gr.rid WHERE gm.guid = ?", CONNECTION_BOTH);
    // 0: uint32, 1: uint8, 3: string, 4: uint32, 5: uint32
    PrepareStatement(CHAR_INS_GUILD_RANK, "INSERT INTO guild_rank (guildid, rid, rname, rights, BankMoneyPerDay) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_RANKS, "DELETE FROM guild_rank WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    PrepareStatement(CHAR_DEL_GUILD_LOWEST_RANK, "DELETE FROM guild_rank WHERE guildid = ? AND rid >= ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8
    PrepareStatement(CHAR_INS_GUILD_BANK_TAB, "INSERT INTO guild_bank_tab (guildid, TabId) VALUES (?, ?)", CONNECTION_ASYNC); // 0: uint32, 1: uint8
    PrepareStatement(CHAR_DEL_GUILD_BANK_TAB, "DELETE FROM guild_bank_tab WHERE guildid = ? AND TabId = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8
    PrepareStatement(CHAR_DEL_GUILD_BANK_TABS, "DELETE FROM guild_bank_tab WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    // 0: uint32, 1: uint8, 2: uint8, 3: uint32, 4: uint32
    PrepareStatement(CHAR_INS_GUILD_BANK_ITEM, "INSERT INTO guild_bank_item (guildid, TabId, SlotId, item_guid) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_BANK_ITEM, "DELETE FROM guild_bank_item WHERE guildid = ? AND TabId = ? AND SlotId = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8, 2: uint8
    PrepareStatement(CHAR_DEL_GUILD_BANK_ITEMS, "DELETE FROM guild_bank_item WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    // 0: uint32, 1: uint8, 2: uint8, 3: uint8, 4: uint32
    PrepareStatement(CHAR_INS_GUILD_BANK_RIGHT, "INSERT INTO guild_bank_right (guildid, TabId, rid, gbright, SlotPerDay) VALUES (?, ?, ?, ?, ?) "
                     "ON DUPLICATE KEY UPDATE gbright = VALUES(gbright), SlotPerDay = VALUES(SlotPerDay)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_BANK_RIGHTS, "DELETE FROM guild_bank_right WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    PrepareStatement(CHAR_DEL_GUILD_BANK_RIGHTS_FOR_RANK, "DELETE FROM guild_bank_right WHERE guildid = ? AND rid = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8
    // 0-1: uint32, 2-3: uint8, 4-5: uint32, 6: uint16, 7: uint8, 8: uint64
    PrepareStatement(CHAR_INS_GUILD_BANK_EVENTLOG, "INSERT INTO guild_bank_eventlog (guildid, LogGuid, TabId, EventType, PlayerGuid, ItemOrMoney, ItemStackCount, DestTabId, TimeStamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_BANK_EVENTLOG, "DELETE FROM guild_bank_eventlog WHERE guildid = ? AND LogGuid = ? AND TabId = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint32, 2: uint8
    PrepareStatement(CHAR_DEL_GUILD_BANK_EVENTLOGS, "DELETE FROM guild_bank_eventlog WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    // 0-1: uint32, 2: uint8, 3-4: uint32, 5: uint8, 6: uint64
    PrepareStatement(CHAR_INS_GUILD_EVENTLOG, "INSERT INTO guild_eventlog (guildid, LogGuid, EventType, PlayerGuid1, PlayerGuid2, NewRank, TimeStamp) VALUES (?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_EVENTLOG, "DELETE FROM guild_eventlog WHERE guildid = ? AND LogGuid = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint32
    PrepareStatement(CHAR_DEL_GUILD_EVENTLOGS, "DELETE FROM guild_eventlog WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32
    PrepareStatement(CHAR_UPD_GUILD_MEMBER_PNOTE, "UPDATE guild_member SET pnote = ? WHERE guid = ?", CONNECTION_ASYNC); // 0: string, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_MEMBER_OFFNOTE, "UPDATE guild_member SET offnote = ? WHERE guid = ?", CONNECTION_ASYNC); // 0: string, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_MEMBER_RANK, "UPDATE guild_member SET `rank` = ? WHERE guid = ?", CONNECTION_ASYNC); // 0: uint8, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_MOTD, "UPDATE guild SET motd = ? WHERE guildid = ?", CONNECTION_ASYNC); // 0: string, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_INFO, "UPDATE guild SET info = ? WHERE guildid = ?", CONNECTION_ASYNC); // 0: string, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_LEADER, "UPDATE guild SET leaderguid = ? WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint32
    PrepareStatement(CHAR_UPD_GUILD_RANK_NAME, "UPDATE guild_rank SET rname = ? WHERE rid = ? AND guildid = ?", CONNECTION_ASYNC); // 0: string, 1: uint8, 2: uint32
    PrepareStatement(CHAR_UPD_GUILD_RANK_RIGHTS, "UPDATE guild_rank SET rights = ? WHERE rid = ? AND guildid = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8, 2: uint32
    // 0-5: uint32
    PrepareStatement(CHAR_UPD_GUILD_EMBLEM_INFO, "UPDATE guild SET EmblemStyle = ?, EmblemColor = ?, BorderStyle = ?, BorderColor = ?, BackgroundColor = ? WHERE guildid = ?", CONNECTION_ASYNC);
    // 0: string, 1: string, 2: uint32, 3: uint8
    PrepareStatement(CHAR_UPD_GUILD_BANK_TAB_INFO, "UPDATE guild_bank_tab SET TabName = ?, TabIcon = ? WHERE guildid = ? AND TabId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GUILD_BANK_MONEY, "UPDATE guild SET BankMoney = ? WHERE guildid = ?", CONNECTION_ASYNC); // 0: uint64, 1: uint32
    // 0: uint8, 1: uint32, 2: uint8, 3: uint32
    PrepareStatement(CHAR_UPD_GUILD_BANK_EVENTLOG_TAB, "UPDATE guild_bank_eventlog SET TabId = ? WHERE guildid = ? AND TabId = ? AND LogGuid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GUILD_RANK_BANK_MONEY, "UPDATE guild_rank SET BankMoneyPerDay = ? WHERE rid = ? AND guildid = ?", CONNECTION_ASYNC); // 0: uint32, 1: uint8, 2: uint32
    PrepareStatement(CHAR_UPD_GUILD_BANK_TAB_TEXT, "UPDATE guild_bank_tab SET TabText = ? WHERE guildid = ? AND TabId = ?", CONNECTION_ASYNC); // 0: string, 1: uint32, 2: uint8

    PrepareStatement(CHAR_INS_GUILD_MEMBER_WITHDRAW,
                     "INSERT INTO guild_member_withdraw (guid, tab0, tab1, tab2, tab3, tab4, tab5, money) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                     "ON DUPLICATE KEY UPDATE tab0 = VALUES (tab0), tab1 = VALUES (tab1), tab2 = VALUES (tab2), tab3 = VALUES (tab3), tab4 = VALUES (tab4), tab5 = VALUES (tab5)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_MEMBER_WITHDRAW, "TRUNCATE guild_member_withdraw", CONNECTION_ASYNC);

    // 0: uint32, 1: uint32, 2: uint32
    PrepareStatement(CHAR_SEL_CHAR_DATA_FOR_GUILD, "SELECT name, level, class, gender, zone, account FROM characters WHERE guid = ?", CONNECTION_SYNCH);

    // Chat channel handling
    PrepareStatement(CHAR_INS_CHANNEL, "INSERT INTO channels(channelId, name, team, announce, lastUsed) VALUES (?, ?, ?, ?, UNIX_TIMESTAMP())", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHANNEL, "UPDATE channels SET announce = ?, password = ?, lastUsed = UNIX_TIMESTAMP() WHERE channelId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHANNEL, "DELETE FROM channels WHERE name = ? AND team = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHANNEL_USAGE, "UPDATE channels SET lastUsed = UNIX_TIMESTAMP() WHERE channelId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_OLD_CHANNELS, "DELETE FROM channels WHERE lastUsed + ? < UNIX_TIMESTAMP()", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_OLD_CHANNELS_BANS, "DELETE cb.* FROM channels_bans cb LEFT JOIN channels cn ON cb.channelId=cn.channelId WHERE cn.channelId IS NULL OR cb.banTime <= UNIX_TIMESTAMP()", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHANNEL_BAN, "REPLACE INTO channels_bans VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHANNEL_BAN, "DELETE FROM channels_bans WHERE channelId = ? AND playerGUID = ?", CONNECTION_ASYNC);

    // Equipmentsets
    PrepareStatement(CHAR_UPD_EQUIP_SET, "UPDATE character_equipmentsets SET name=?, iconname=?, ignore_mask=?, item0=?, item1=?, item2=?, item3=?, "
                     "item4=?, item5=?, item6=?, item7=?, item8=?, item9=?, item10=?, item11=?, item12=?, item13=?, item14=?, item15=?, item16=?, "
                     "item17=?, item18=? WHERE guid=? AND setguid=? AND setindex=?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_EQUIP_SET, "INSERT INTO character_equipmentsets (guid, setguid, setindex, name, iconname, ignore_mask, item0, item1, item2, item3, "
                     "item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15, item16, item17, item18) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_EQUIP_SET, "DELETE FROM character_equipmentsets WHERE setguid=?", CONNECTION_ASYNC);

    // Auras
    PrepareStatement(CHAR_INS_AURA, "INSERT INTO character_aura (guid, casterGuid, itemGuid, spell, effectMask, recalculateMask, stackcount, amount0, amount1, amount2, base_amount0, base_amount1, base_amount2, maxDuration, remainTime, remainCharges) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);

    // Account data
    PrepareStatement(CHAR_SEL_ACCOUNT_DATA, "SELECT type, time, data FROM account_data WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_ACCOUNT_DATA, "REPLACE INTO account_data (accountId, type, time, data) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ACCOUNT_DATA, "DELETE FROM account_data WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PLAYER_ACCOUNT_DATA, "SELECT type, time, data FROM character_account_data WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_PLAYER_ACCOUNT_DATA, "REPLACE INTO character_account_data(guid, type, time, data) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PLAYER_ACCOUNT_DATA, "DELETE FROM character_account_data WHERE guid = ?", CONNECTION_ASYNC);

    // Tutorials
    PrepareStatement(CHAR_SEL_TUTORIALS, "SELECT tut0, tut1, tut2, tut3, tut4, tut5, tut6, tut7 FROM account_tutorial WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_HAS_TUTORIALS, "SELECT 1 FROM account_tutorial WHERE accountId = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_TUTORIALS, "INSERT INTO account_tutorial(tut0, tut1, tut2, tut3, tut4, tut5, tut6, tut7, accountId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_TUTORIALS, "UPDATE account_tutorial SET tut0 = ?, tut1 = ?, tut2 = ?, tut3 = ?, tut4 = ?, tut5 = ?, tut6 = ?, tut7 = ? WHERE accountId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_TUTORIALS, "DELETE FROM account_tutorial WHERE accountId = ?", CONNECTION_ASYNC);

    // Instance saves
    PrepareStatement(CHAR_INS_INSTANCE_SAVE, "INSERT INTO instance (id, map, resettime, difficulty, completedEncounters, data) VALUES (?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_INSTANCE_SAVE_DATA, "UPDATE instance SET data=? WHERE id=?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_INSTANCE_SAVE_ENCOUNTERMASK, "UPDATE instance SET completedEncounters=? WHERE id=?", CONNECTION_ASYNC);

    // Game event saves
    PrepareStatement(CHAR_DEL_GAME_EVENT_SAVE, "DELETE FROM game_event_save WHERE eventEntry = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_GAME_EVENT_SAVE, "INSERT INTO game_event_save (eventEntry, state, next_start) VALUES (?, ?, ?)", CONNECTION_ASYNC);

    // Game event condition saves
    PrepareStatement(CHAR_DEL_ALL_GAME_EVENT_CONDITION_SAVE, "DELETE FROM game_event_condition_save WHERE eventEntry = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GAME_EVENT_CONDITION_SAVE, "DELETE FROM game_event_condition_save WHERE eventEntry = ? AND condition_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_GAME_EVENT_CONDITION_SAVE, "INSERT INTO game_event_condition_save (eventEntry, condition_id, done) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_GAME_EVENT_CONDITION_SAVE_DATA, "SELECT eventEntry, condition_id, done FROM game_event_condition_save", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_GAME_EVENT_SAVE_DATA, "SELECT eventEntry, state, next_start FROM game_event_save", CONNECTION_SYNCH);

    // Petitions
    PrepareStatement(CHAR_DEL_ALL_PETITION_SIGNATURES, "DELETE FROM petition_sign WHERE playerguid = ?", CONNECTION_ASYNC);
    // petition_sign.type is not written by the sign insert (petition_id schema), join petition for the type filter
    PrepareStatement(CHAR_DEL_PETITION_SIGNATURE, "DELETE ps FROM petition_sign ps INNER JOIN petition p ON p.petition_id = ps.petition_id WHERE ps.playerguid = ? AND p.type = ?", CONNECTION_ASYNC);

    // Arena teams
    PrepareStatement(CHAR_INS_ARENA_TEAM, "INSERT INTO arena_team (arenaTeamId, name, captainGuid, type, rating, backgroundColor, emblemStyle, emblemColor, borderStyle, borderColor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ARENA_TEAM_MEMBER, "INSERT INTO arena_team_member (arenaTeamId, guid, personalRating) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ARENA_TEAM, "DELETE FROM arena_team WHERE arenaTeamId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ARENA_TEAM_MEMBERS, "DELETE FROM arena_team_member WHERE arenaTeamId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ARENA_TEAM_CAPTAIN, "UPDATE arena_team SET captainGuid = ? WHERE arenaTeamId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ARENA_TEAM_MEMBER, "DELETE FROM arena_team_member WHERE arenaTeamId = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ARENA_TEAM_STATS, "UPDATE arena_team SET rating = ?, weekGames = ?, weekWins = ?, seasonGames = ?, seasonWins = ?, `rank` = ? WHERE arenaTeamId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ARENA_TEAM_MEMBER, "UPDATE arena_team_member SET personalRating = ?, weekGames = ?, weekWins = ?, seasonGames = ?, seasonWins = ? WHERE arenaTeamId = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_CHARACTER_ARENA_STATS, "REPLACE INTO character_arena_stats (guid, slot, matchMakerRating, maxMMR) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PLAYER_ARENA_TEAMS, "SELECT arena_team_member.arenaTeamId FROM arena_team_member JOIN arena_team ON arena_team_member.arenaTeamId = arena_team.arenaTeamId WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_UPD_ARENA_TEAM_NAME, "UPDATE arena_team SET name = ? WHERE arenaTeamId = ?", CONNECTION_ASYNC);

    // Character battleground data
    PrepareStatement(CHAR_INS_PLAYER_ENTRY_POINT, "INSERT INTO character_entry_point (guid, joinX, joinY, joinZ, joinO, joinMapId, taxiPath0, taxiPath1, mountSpell) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PLAYER_ENTRY_POINT, "DELETE FROM character_entry_point WHERE guid = ?", CONNECTION_ASYNC);

    // Character homebind
    PrepareStatement(CHAR_INS_PLAYER_HOMEBIND, "INSERT INTO character_homebind (guid, mapId, zoneId, posX, posY, posZ) VALUES (?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_PLAYER_HOMEBIND, "UPDATE character_homebind SET mapId = ?, zoneId = ?, posX = ?, posY = ?, posZ = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PLAYER_HOMEBIND, "DELETE FROM character_homebind WHERE guid = ?", CONNECTION_ASYNC);

    // Corpse
    PrepareStatement(CHAR_SEL_CORPSES, "SELECT posX, posY, posZ, orientation, mapId, displayId, itemCache, bytes1, bytes2, guildId, flags, dynFlags, time, corpseType, instanceId, phaseMask, guid FROM corpse WHERE mapId = ? AND instanceId = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_CORPSE, "INSERT INTO corpse (guid, posX, posY, posZ, orientation, mapId, displayId, itemCache, bytes1, bytes2, guildId, flags, dynFlags, time, corpseType, instanceId, phaseMask) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CORPSE, "DELETE FROM corpse WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CORPSES_FROM_MAP, "DELETE FROM corpse WHERE mapId = ? AND instanceId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CORPSE_LOCATION, "SELECT mapId, posX, posY, posZ, orientation FROM corpse WHERE guid = ?", CONNECTION_ASYNC);

    // Creature respawn
    PrepareStatement(CHAR_SEL_CREATURE_RESPAWNS, "SELECT guid, respawnTime FROM creature_respawn WHERE mapId = ? AND instanceId = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_CREATURE_RESPAWN, "REPLACE INTO creature_respawn (guid, respawnTime, mapId, instanceId) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CREATURE_RESPAWN, "DELETE FROM creature_respawn WHERE guid = ? AND mapId = ? AND instanceId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CREATURE_RESPAWN_BY_INSTANCE, "DELETE FROM creature_respawn WHERE mapId = ? AND instanceId = ?", CONNECTION_ASYNC);

    // Gameobject respawn
    PrepareStatement(CHAR_SEL_GO_RESPAWNS, "SELECT guid, respawnTime FROM gameobject_respawn WHERE mapId = ? AND instanceId = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_GO_RESPAWN, "REPLACE INTO gameobject_respawn (guid, respawnTime, mapId, instanceId) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GO_RESPAWN, "DELETE FROM gameobject_respawn WHERE guid = ? AND mapId = ? AND instanceId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GO_RESPAWN_BY_INSTANCE, "DELETE FROM gameobject_respawn WHERE mapId = ? AND instanceId = ?", CONNECTION_ASYNC);

    // GM Tickets
    PrepareStatement(CHAR_SEL_GM_TICKETS, "SELECT id, type, playerGuid, name, description, createTime, mapId, posX, posY, posZ, lastModifiedTime, closedBy, assignedTo, comment, response, completed, escalated, viewed, needMoreHelp, resolvedBy FROM gm_ticket", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_GM_TICKET, "REPLACE INTO gm_ticket (id, type, playerGuid, name, description, createTime, mapId, posX, posY, posZ, lastModifiedTime, closedBy, assignedTo, comment, response, completed, escalated, viewed, needMoreHelp, resolvedBy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GM_TICKET, "DELETE FROM gm_ticket WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PLAYER_GM_TICKETS, "DELETE FROM gm_ticket WHERE playerGuid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_PLAYER_GM_TICKETS_ON_CHAR_DELETION, "UPDATE gm_ticket SET type = 2 WHERE playerGuid = ?", CONNECTION_ASYNC);

    // GM Survey/subsurvey/lag report
    PrepareStatement(CHAR_INS_GM_SURVEY, "INSERT INTO gm_survey (guid, surveyId, mainSurvey, comment, createTime) VALUES (?, ?, ?, ?, UNIX_TIMESTAMP(NOW()))", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_GM_SUBSURVEY, "INSERT INTO gm_subsurvey (surveyId, questionId, answer, answerComment) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_LAG_REPORT, "INSERT INTO lag_reports (guid, lagType, mapId, posX, posY, posZ, latency, createTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);

    // LFG Data
    PrepareStatement(CHAR_REP_LFG_DATA, "REPLACE INTO lfg_data (guid, dungeon, state) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_LFG_DATA, "DELETE FROM lfg_data WHERE guid = ?", CONNECTION_ASYNC);

    // Player saving
    PrepareStatement(CHAR_INS_CHARACTER, "INSERT INTO characters (guid, account, name, race, class, gender, level, xp, money, skin, face, hairStyle, hairColor, facialStyle, bankSlots, restState, playerFlags, "
                     "map, instance_id, instance_mode_mask, position_x, position_y, position_z, orientation, trans_x, trans_y, trans_z, trans_o, transguid, "
                     "taximask, cinematic, "
                     "totaltime, leveltime, rest_bonus, logout_time, is_logout_resting, resettalents_cost, resettalents_time, "
                     "extra_flags, stable_slots, at_login, zone, "
                     "death_expire_time, taxi_path, arenaPoints, totalHonorPoints, todayHonorPoints, yesterdayHonorPoints, totalKills, "
                     "todayKills, yesterdayKills, chosenTitle, knownCurrencies, watchedFaction, drunk, health, power1, power2, power3, "
                     "power4, power5, power6, power7, latency, talentGroupsCount, activeTalentGroup, exploredZones, equipmentCache, "
                     "ammoId, knownTitles, actionBars, grantableLevels, innTriggerId, "
                     "extraBonusTalentCount, teamId) VALUES "
                     "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,"
                     "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHARACTER, "UPDATE characters SET name=?,race=?,class=?,gender=?,level=?,xp=?,money=?,skin=?,face=?,hairStyle=?,hairColor=?,facialStyle=?,bankSlots=?,restState=?,playerFlags=?,"
                     "map=?,instance_id=?,instance_mode_mask=?,position_x=?,position_y=?,position_z=?,orientation=?,trans_x=?,trans_y=?,trans_z=?,trans_o=?,transguid=?,taximask=?,cinematic=?,totaltime=?,leveltime=?,rest_bonus=?,"
                     "logout_time=?,is_logout_resting=?,resettalents_cost=?,resettalents_time=?,extra_flags=?,stable_slots=?,at_login=?,zone=?,death_expire_time=?,taxi_path=?,"
                     "arenaPoints=?,totalHonorPoints=?,todayHonorPoints=?,yesterdayHonorPoints=?,totalKills=?,todayKills=?,yesterdayKills=?,chosenTitle=?,knownCurrencies=?,"
                     "watchedFaction=?,drunk=?,health=?,power1=?,power2=?,power3=?,power4=?,power5=?,power6=?,power7=?,latency=?,talentGroupsCount=?,activeTalentGroup=?,exploredZones=?,"
                     "equipmentCache=?,ammoId=?,knownTitles=?,actionBars=?,grantableLevels=?,innTriggerId=?,"
                     "extraBonusTalentCount=?,teamId=?,online=? WHERE guid=?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHARACTER_TEAM, "UPDATE characters SET teamId = ? WHERE guid = ?", CONNECTION_ASYNC);

    PrepareStatement(CHAR_UPD_ADD_AT_LOGIN_FLAG, "UPDATE characters SET at_login = at_login | ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_REM_AT_LOGIN_FLAG, "UPDATE characters set at_login = at_login & ~ ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ALL_AT_LOGIN_FLAGS, "UPDATE characters SET at_login = at_login | ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_BUG_REPORT, "INSERT INTO bugreport (type, content) VALUES(?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_SPAM_REPORT, "INSERT INTO spam_reports (SpamType, SpammerGuid, Unk1, MailIdOrMessageType, ChannelId, SecondsSinceMessage, Description, Time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_PETITION_NAME, "UPDATE petition SET name = ? WHERE petition_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PETITION_SIGNATURE, "INSERT INTO petition_sign (ownerguid, petition_id, playerguid, player_account) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ACCOUNT_ONLINE, "UPDATE characters SET online = 0 WHERE account = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_OFFLINE, "UPDATE characters SET online = 0 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_GROUP, "INSERT INTO `groups` (guid, leaderGuid, lootMethod, looterGuid, lootThreshold, icon1, icon2, icon3, icon4, icon5, icon6, icon7, icon8, groupType, difficulty, raidDifficulty, masterLooterGuid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_GROUP_MEMBER, "REPLACE INTO group_member (guid, memberGuid, memberFlags, subgroup, roles) VALUES(?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GROUP_MEMBER, "DELETE FROM group_member WHERE memberGuid = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_LEADER, "UPDATE `groups` SET leaderGuid = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_TYPE, "UPDATE `groups` SET groupType = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_MEMBER_SUBGROUP, "UPDATE group_member SET subgroup = ? WHERE memberGuid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_MEMBER_FLAG, "UPDATE group_member SET memberFlags = ? WHERE memberGuid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_DIFFICULTY, "UPDATE `groups` SET difficulty = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GROUP_RAID_DIFFICULTY, "UPDATE `groups` SET raidDifficulty = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ALL_GM_TICKETS, "TRUNCATE TABLE gm_ticket", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_SPELL_TALENTS, "DELETE FROM character_talent WHERE spell = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_SPELL_SPELLS, "DELETE FROM character_spell WHERE spell = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_DELETE_INFO, "UPDATE characters SET deleteInfos_Name = name, deleteInfos_Account = account, deleteDate = UNIX_TIMESTAMP(), name = '', account = 0 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_RESTORE_DELETE_INFO, "UPDATE characters SET name = ?, account = ?, deleteDate = NULL, deleteInfos_Name = NULL, deleteInfos_Account = NULL WHERE deleteDate IS NOT NULL AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ZONE, "UPDATE characters SET zone = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_LEVEL, "UPDATE characters SET level = ?, xp = 0 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_XP_ACCUMULATIVE, "UPDATE characters SET  xp = xp + ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_ACHIEV_PROGRESS_CRITERIA, "DELETE FROM character_achievement_progress WHERE criteria = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_ACHIEVMENT, "DELETE FROM character_achievement WHERE achievement = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ADDON, "INSERT INTO addons (name, crc) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INVALID_PET_SPELL, "DELETE FROM pet_spell WHERE spell = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GLOBAL_INSTANCE_RESETTIME, "UPDATE instance_reset SET resettime = ? WHERE mapid = ? AND difficulty = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_ONLINE, "UPDATE characters SET online = 1 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_NAME_AT_LOGIN, "UPDATE characters set name = ?, at_login = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_WORLDSTATE, "UPDATE worldstates SET value = ? WHERE entry = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLDSTATE, "INSERT INTO worldstates (entry, value) VALUES (?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INSTANCE_BY_INSTANCE, "DELETE FROM character_instance WHERE instance = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INSTANCE_BY_INSTANCE_NOT_EXTENDED, "DELETE FROM character_instance WHERE instance = ? AND extended = 0", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_INSTANCE_SET_NOT_EXTENDED, "UPDATE character_instance SET extended = 0 WHERE instance = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INSTANCE_BY_INSTANCE_GUID, "DELETE FROM character_instance WHERE guid = ? AND instance = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_INSTANCE, "UPDATE character_instance SET instance = ?, permanent = ?, extended = 0 WHERE guid = ? AND instance = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_INSTANCE_EXTENDED, "UPDATE character_instance SET extended = ? WHERE guid = ? AND instance = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_INSTANCE, "INSERT INTO character_instance (guid, instance, permanent, extended) VALUES (?, ?, ?, 0)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ARENA_LOG_FIGHT, "INSERT INTO log_arena_fights VALUES (?, NOW(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ARENA_LOG_MEMBERSTATS, "INSERT INTO log_arena_memberstats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GENDER_AND_APPEARANCE, "UPDATE characters SET gender = ?, skin = ?, face = ?, hairStyle = ?, hairColor = ?, facialStyle = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHARACTER_SKILL, "DELETE FROM character_skills WHERE guid = ? AND skill = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ADD_CHARACTER_SOCIAL_FLAGS, "UPDATE character_social SET flags = flags | ? WHERE guid = ? AND friend = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_REM_CHARACTER_SOCIAL_FLAGS, "UPDATE character_social SET flags = flags & ~ ? WHERE guid = ? AND friend = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHARACTER_SOCIAL, "REPLACE INTO character_social (guid, friend, flags) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHARACTER_SOCIAL, "DELETE FROM character_social WHERE guid = ? AND friend = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHARACTER_SOCIAL_NOTE, "UPDATE character_social SET note = ? WHERE guid = ? AND friend = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHARACTER_POSITION, "UPDATE characters SET position_x = ?, position_y = ?, position_z = ?, orientation = ?, map = ?, zone = ?, trans_x = 0, trans_y = 0, trans_z = 0, transguid = 0, taxi_path = '', cinematic = 1 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_AURA_FROZEN, "SELECT characters.name FROM characters LEFT JOIN character_aura ON (characters.guid = character_aura.guid) WHERE character_aura.spell = 9454", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHARACTER_ONLINE, "SELECT name, account, map, zone FROM characters WHERE online > 0", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_DEL_INFO_BY_GUID, "SELECT guid, deleteInfos_Name, deleteInfos_Account, deleteDate, level FROM characters WHERE deleteDate IS NOT NULL AND guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_DEL_INFO_BY_NAME, "SELECT guid, deleteInfos_Name, deleteInfos_Account, deleteDate, level FROM characters WHERE deleteDate IS NOT NULL AND deleteInfos_Name LIKE CONCAT('%%', ?, '%%') ORDER BY deleteDate DESC", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_DEL_INFO_BY_NAME_LIMIT, "SELECT guid, deleteInfos_Name, deleteInfos_Account, deleteDate, level FROM characters WHERE deleteDate IS NOT NULL AND deleteInfos_Name LIKE CONCAT('%%', ?, '%%') ORDER BY deleteDate DESC LIMIT 51", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_DEL_INFO, "SELECT guid, deleteInfos_Name, deleteInfos_Account, deleteDate, level FROM characters WHERE deleteDate IS NOT NULL ORDER BY deleteDate DESC LIMIT 51", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHARS_BY_ACCOUNT_ID, "SELECT guid, class, race FROM characters WHERE account = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ACCOUNT_INFO_CHARS, "SELECT guid, name, level, race, class, online FROM characters WHERE account = ? AND deleteDate IS NULL ORDER BY level DESC, name ASC", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_PINFO, "SELECT totaltime, level, money, account, race, class, map, zone, gender, health, playerFlags FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_PINFO_BANS, "SELECT unbandate, bandate = unbandate, bannedby, banreason FROM character_banned WHERE guid = ? AND active ORDER BY bandate ASC LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_PINFO_MAILS, "SELECT SUM(CASE WHEN (checked & 1) THEN 1 ELSE 0 END) AS 'readmail', COUNT(*) AS 'totalmail' FROM mail WHERE `receiver` = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_PINFO_XP, "SELECT a.xp, b.guid FROM characters a LEFT JOIN guild_member b ON a.guid = b.guid WHERE a.guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_HOMEBIND, "SELECT mapId, zoneId, posX, posY, posZ FROM character_homebind WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_GUID_NAME_BY_ACC, "SELECT guid, name FROM characters WHERE account = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_POOL_QUEST_SAVE, "SELECT quest_id FROM pool_quest_save WHERE pool_id = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHARACTER_AT_LOGIN, "SELECT at_login FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_CLASS_LVL_AT_LOGIN, "SELECT class, level, at_login, knownTitles FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_CUSTOMIZE_INFO, "SELECT name, race, class, gender, at_login FROM characters WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_RACE_OR_FACTION_CHANGE_INFOS,
                     "SELECT at_login, knownTitles, money, teamId FROM characters WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_AT_LOGIN_TITLES_MONEY, "SELECT at_login, knownTitles, money FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_COD_ITEM_MAIL, "SELECT id, messageType, mailTemplateId, sender, subject, body, money, has_items FROM mail WHERE receiver = ? AND has_items <> 0 AND cod <> 0", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_SOCIAL, "SELECT DISTINCT guid FROM character_social WHERE friend = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_OLD_CHARS, "SELECT guid, deleteInfos_Account FROM characters WHERE deleteDate IS NOT NULL AND deleteDate < ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ARENA_TEAM_ID_BY_PLAYER_GUID, "SELECT arena_team_member.arenateamid FROM arena_team_member JOIN arena_team ON arena_team_member.arenateamid = arena_team.arenateamid WHERE guid = ? AND type = ? LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MAIL, "SELECT id, messageType, sender, receiver, subject, body, expire_time, deliver_time, money, cod, checked, stationery, mailTemplateId, has_items FROM mail WHERE receiver = ? ORDER BY id DESC", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_NEXT_MAIL_DELIVERYTIME, "SELECT MIN(deliver_time) FROM mail WHERE receiver = ? AND deliver_time > ? AND (checked & 1) = 0 LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAR_AURA_FROZEN, "DELETE FROM character_aura WHERE spell = 9454 AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_INVENTORY_COUNT_ITEM, "SELECT COUNT(itemEntry) FROM item_instance ii "
        "WHERE itemEntry = ? AND (EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ii.guid) "
        "OR EXISTS(SELECT 1 FROM character_digital_storage_item ds WHERE ds.item = ii.guid))", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MAIL_COUNT_ITEM, "SELECT COUNT(itemEntry) FROM mail_items mi INNER JOIN item_instance ii ON ii.guid = mi.item_guid WHERE itemEntry = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_AUCTIONHOUSE_COUNT_ITEM, "SELECT COUNT(itemEntry) FROM auctionhouse ah INNER JOIN item_instance ii ON ii.guid = ah.itemguid WHERE itemEntry = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_GUILD_BANK_COUNT_ITEM, "SELECT COUNT(itemEntry) FROM guild_bank_item gbi INNER JOIN item_instance ii ON ii.guid = gbi.item_guid WHERE itemEntry = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_INVENTORY_ITEM_BY_ENTRY, "SELECT ci.item, cb.slot AS bag, ci.slot, ci.guid, c.account, c.name FROM characters c "
                     "INNER JOIN (SELECT guid, item, bag, slot FROM character_inventory UNION ALL "
                     "SELECT guid, item, 0, 255 FROM character_digital_storage_item) ci ON ci.guid = c.guid "
                     "INNER JOIN item_instance ii ON ii.guid = ci.item "
                     "LEFT JOIN character_inventory cb ON cb.item = ci.bag WHERE ii.itemEntry = ? LIMIT ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_INVENTORY_ITEM_BY_ENTRY_AND_OWNER, "SELECT ii.guid FROM item_instance ii "
        "WHERE ii.itemEntry = ? AND ii.owner_guid = ? "
        "AND (EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ii.guid) "
        "OR EXISTS(SELECT 1 FROM character_digital_storage_item ds WHERE ds.item = ii.guid))", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_INVENTORY_STACKS_BY_ENTRY_AND_OWNER, "SELECT ii.guid, ii.count FROM item_instance ii "
        "LEFT JOIN character_inventory cb ON cb.bag = ii.guid "
        "WHERE ii.itemEntry = ? AND ii.owner_guid = ? AND cb.item IS NULL "
        "AND (EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ii.guid) "
        "OR EXISTS(SELECT 1 FROM character_digital_storage_item ds WHERE ds.item = ii.guid))", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MAIL_ITEMS_BY_ENTRY, "SELECT mi.item_guid, m.sender, m.receiver, cs.account, cs.name, cr.account, cr.name "
                     "FROM mail m INNER JOIN mail_items mi ON mi.mail_id = m.id INNER JOIN item_instance ii ON ii.guid = mi.item_guid "
                     "INNER JOIN characters cs ON cs.guid = m.sender INNER JOIN characters cr ON cr.guid = m.receiver WHERE ii.itemEntry = ? LIMIT ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_AUCTIONHOUSE_ITEM_BY_ENTRY, "SELECT  ah.itemguid, ah.itemowner, c.account, c.name FROM auctionhouse ah INNER JOIN characters c ON c.guid = ah.itemowner INNER JOIN item_instance ii ON ii.guid = ah.itemguid WHERE ii.itemEntry = ? LIMIT ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_GUILD_BANK_ITEM_BY_ENTRY, "SELECT gi.item_guid, gi.guildid, g.name FROM guild_bank_item gi INNER JOIN guild g ON g.guildid = gi.guildid INNER JOIN item_instance ii ON ii.guid = gi.item_guid WHERE ii.itemEntry = ? LIMIT ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENT, "DELETE FROM character_achievement WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENT_PROGRESS, "DELETE FROM character_achievement_progress WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_ACHIEVEMENT, "INSERT INTO character_achievement (guid, achievement, date) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENT_PROGRESS_BY_CRITERIA, "DELETE FROM character_achievement_progress WHERE guid = ? AND criteria = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_ACHIEVEMENT_PROGRESS, "INSERT INTO character_achievement_progress (guid, criteria, counter, date) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_ACHIEVEMENT_OFFLINE_UPDATES, "INSERT INTO character_achievement_offline_updates (guid, update_type, arg1, arg2, arg3) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_ACHIEVEMENT_OFFLINE_UPDATES, "SELECT update_type, arg1, arg2, arg3 FROM character_achievement_offline_updates WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENT_OFFLINE_UPDATES, "DELETE FROM character_achievement_offline_updates WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_REPUTATION_BY_FACTION, "DELETE FROM character_reputation WHERE guid = ? AND faction = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_REPUTATION_BY_FACTION, "INSERT INTO character_reputation (guid, faction, standing, flags) VALUES (?, ?, ? , ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_ARENA_POINTS, "UPDATE characters SET arenaPoints = (arenaPoints + ?) WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ITEM_REFUND_INSTANCE, "DELETE FROM item_refund_instance WHERE item_guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ITEM_REFUND_INSTANCE, "INSERT INTO item_refund_instance (item_guid, player_guid, paidMoney, paidExtendedCost) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GROUP, "DELETE FROM `groups` WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GROUP_MEMBER_ALL, "DELETE FROM group_member WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_GIFT, "INSERT INTO character_gifts (guid, item_guid, entry, flags) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_INSTANCE_BY_INSTANCE, "DELETE FROM instance WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_MAIL_ITEM_BY_ID, "DELETE FROM mail_items WHERE mail_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PETITION, "INSERT INTO petition (petition_id, ownerguid, petitionguid, name, type) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PETITION_BY_ID, "DELETE FROM petition WHERE petition_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PETITION_SIGNATURE_BY_ID, "DELETE FROM petition_sign WHERE petition_id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_DECLINED_NAME, "DELETE FROM character_declinedname WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_DECLINED_NAME, "INSERT INTO character_declinedname (guid, genitive, dative, accusative, instrumental, prepositional) VALUES (?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_RACE, "UPDATE characters SET race = ?, teamId = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SKILL_LANGUAGES, "DELETE FROM character_skills WHERE skill IN (98, 113, 759, 111, 313, 109, 115, 315, 673, 137) AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_SKILL_LANGUAGE, "INSERT INTO `character_skills` (guid, skill, value, max) VALUES (?, ?, 300, 300)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_TAXI_PATH, "UPDATE characters SET taxi_path = '' WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_TAXIMASK, "UPDATE characters SET taximask = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_QUESTSTATUS, "DELETE FROM character_queststatus WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SOCIAL_BY_GUID, "DELETE FROM character_social WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SOCIAL_BY_FRIEND, "DELETE FROM character_social WHERE friend = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENT_BY_ACHIEVEMENT, "DELETE FROM character_achievement WHERE achievement = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_ACHIEVEMENT, "UPDATE character_achievement SET achievement = ? WHERE achievement = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_INVENTORY_FACTION_CHANGE, "UPDATE item_instance ii SET ii.itemEntry = ? "
        "WHERE ii.itemEntry = ? AND ii.owner_guid = ? "
        "AND (EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ii.guid) "
        "OR EXISTS(SELECT 1 FROM character_digital_storage_item ds WHERE ds.item = ii.guid))", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SPELL_BY_SPELL, "DELETE FROM character_spell WHERE guid = ? AND spell = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_SPELL_FACTION_CHANGE, "UPDATE character_spell SET spell = ? WHERE spell = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_REP_BY_FACTION, "SELECT standing FROM character_reputation WHERE faction = ? AND guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAR_REP_BY_FACTION, "DELETE FROM character_reputation WHERE faction = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_REP_FACTION_CHANGE, "UPDATE character_reputation SET faction = ?, standing = ? WHERE faction = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_TITLES_FACTION_CHANGE, "UPDATE characters SET knownTitles = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_RES_CHAR_TITLES_FACTION_CHANGE, "UPDATE characters SET chosenTitle = 0 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SPELL_COOLDOWN, "DELETE FROM character_spell_cooldown WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHARACTER, "DELETE FROM characters WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACTION, "DELETE FROM character_action WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_AURA, "DELETE FROM character_aura WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_GIFT, "DELETE FROM character_gifts WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INSTANCE, "DELETE FROM character_instance WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INVENTORY, "DELETE FROM character_inventory WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_QUESTSTATUS_REWARDED, "DELETE FROM character_queststatus_rewarded WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_REPUTATION, "DELETE FROM character_reputation WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SPELL, "DELETE FROM character_spell WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_MAIL, "DELETE FROM mail WHERE receiver = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_MAIL_ITEMS, "DELETE FROM mail_items WHERE receiver = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACHIEVEMENTS, "DELETE FROM character_achievement WHERE guid = ? AND achievement NOT BETWEEN '456' AND '467' AND achievement NOT BETWEEN '1400' AND '1427' AND achievement NOT IN(1463, 3117, 3259)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_EQUIPMENTSETS, "DELETE FROM character_equipmentsets WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_EVENTLOG_BY_PLAYER, "DELETE FROM guild_eventlog WHERE PlayerGuid1 = ? OR PlayerGuid2 = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_GUILD_BANK_EVENTLOG_BY_PLAYER, "DELETE FROM guild_bank_eventlog WHERE PlayerGuid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_GLYPHS, "DELETE FROM character_glyphs WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_TALENT, "DELETE FROM character_talent WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SKILLS, "DELETE FROM character_skills WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_HONOR_POINTS, "UPDATE characters SET totalHonorPoints = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_HONOR_POINTS_ACCUMULATIVE, "UPDATE characters SET totalHonorPoints = totalHonorPoints + ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_ARENA_POINTS, "UPDATE characters SET arenaPoints = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_ARENA_POINTS_ACCUMULATIVE, "UPDATE characters SET arenaPoints = arenaPoints + ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_ALL_HONOR_POINTS, "UPDATE characters SET totalHonorPoints = 0", CONNECTION_SYNCH);
    PrepareStatement(CHAR_UPD_ALL_ARENA_POINTS, "UPDATE characters SET arenaPoints = 0", CONNECTION_SYNCH);
    PrepareStatement(CHAR_UDP_CHAR_MONEY, "UPDATE characters SET money = ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_MONEY_ACCUMULATIVE, "UPDATE characters SET money = money + ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_BOUNTY,
        "INSERT INTO character_world_pvp_bounty (sponsor_guid, id, sponsor_account, target_guid, amount) "
        "VALUES (?, ?, ?, ?, ?)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTY_LAST_ID,
        "SELECT CAST(COALESCE(MAX(id), 0) AS UNSIGNED) FROM character_world_pvp_bounty WHERE sponsor_guid = ?",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTIES_BY_SPONSOR,
        "SELECT id, target_guid, amount FROM character_world_pvp_bounty WHERE sponsor_guid = ? "
        "AND sponsor_account = ? AND state = 1 AND expires_at > UTC_TIMESTAMP() AND id > ? ORDER BY id LIMIT 20",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTY_BY_ID,
        "SELECT amount, target_guid FROM character_world_pvp_bounty WHERE sponsor_guid = ? AND id = ? "
        "AND sponsor_account = ? AND state = 1 AND expires_at > UTC_TIMESTAMP()",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTY_STATE,
        "SELECT CAST(COALESCE((SELECT state FROM character_world_pvp_bounty WHERE sponsor_guid = ? "
        "AND id = ? AND sponsor_account = ?), -1) AS SIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_FUND_WORLD_PVP_BOUNTY,
        "UPDATE characters c JOIN character_world_pvp_bounty b ON b.sponsor_guid = c.guid "
        "JOIN characters t ON t.guid = b.target_guid AND t.account <> c.account AND t.deleteDate IS NULL "
        "SET c.money = ?, b.state = 1, b.expires_at = UTC_TIMESTAMP() + INTERVAL 7 DAY "
        "WHERE b.sponsor_guid = ? AND b.id = ? AND b.sponsor_account = ? "
        "AND c.account = b.sponsor_account AND c.deleteDate IS NULL AND b.state = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_REFUND_WORLD_PVP_BOUNTY,
        "UPDATE characters c JOIN character_world_pvp_bounty b ON b.sponsor_guid = c.guid "
        "SET c.money = ?, b.state = 2 WHERE b.sponsor_guid = ? AND b.id = ? AND b.sponsor_account = ? "
        "AND c.account = b.sponsor_account AND c.deleteDate IS NULL AND b.state = 1 AND b.expires_at > UTC_TIMESTAMP()",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_CLAIM_WORLD_PVP_BOUNTIES,
        "UPDATE character_world_pvp_bounty b "
        "JOIN characters v ON v.guid = b.target_guid AND v.account = ? AND v.deleteDate IS NULL "
        "JOIN characters h ON h.guid = ? AND h.account = ? AND h.account <> v.account AND h.deleteDate IS NULL "
        "LEFT JOIN character_world_pvp_bounty own ON own.target_guid = v.guid AND own.sponsor_account = h.account "
        "AND own.state = 1 AND own.expires_at > UTC_TIMESTAMP() "
        "LEFT JOIN character_world_pvp_bounty recent ON recent.hunter_account = h.account "
        "AND recent.target_account = v.account AND recent.claimed_at >= UTC_TIMESTAMP() - INTERVAL 1 HOUR "
        "LEFT JOIN character_world_pvp_bounty reverse_recent ON reverse_recent.hunter_account = v.account "
        "AND reverse_recent.target_account = h.account "
        "AND reverse_recent.claimed_at >= UTC_TIMESTAMP() - INTERVAL 1 HOUR "
        "SET b.state = 3, b.hunter_guid = h.guid, b.hunter_account = h.account, "
        "b.target_account = v.account, b.claimed_at = UTC_TIMESTAMP() "
        "WHERE b.target_guid = ? AND b.state = 1 AND b.sponsor_account <> v.account "
        "AND b.expires_at > UTC_TIMESTAMP() AND (b.sponsor_guid <> 0 OR ?) "
        "AND own.id IS NULL AND recent.id IS NULL AND reverse_recent.id IS NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_CLOSE_WORLD_PVP_BOUNTIES_ON_DEATH,
        "UPDATE character_world_pvp_bounty SET state = IF(sponsor_guid = 0, 5, 6) "
        "WHERE target_guid = ? AND state = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_RESET_WORLD_PVP_MURDERS_ON_DEATH,
        "UPDATE character_world_pvp_bounty_murder SET counts_for_bounty = 0 WHERE offender_guid = ?",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_REFUND_QUEUE,
        "SELECT b.sponsor_guid, b.id, b.amount, b.sponsor_account FROM character_world_pvp_bounty b "
        "JOIN characters c ON c.guid = b.sponsor_guid AND c.account = b.sponsor_account AND c.deleteDate IS NULL "
        "WHERE b.sponsor_guid <> 0 AND (b.state = 6 OR (b.state = 1 AND b.expires_at <= UTC_TIMESTAMP())) "
        "ORDER BY b.expires_at, b.sponsor_guid, b.id LIMIT 20",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_CREDIT_WORLD_PVP_REFUND_WALLET,
        "UPDATE character_world_pvp_bounty b "
        "JOIN characters c ON c.guid = b.sponsor_guid AND c.account = b.sponsor_account AND c.deleteDate IS NULL "
        "SET c.money = ?, b.state = 2 WHERE b.sponsor_guid = ? AND b.id = ? AND b.sponsor_account = ? "
        "AND (b.state = 6 OR (b.state = 1 AND b.expires_at <= UTC_TIMESTAMP()))",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_RESERVE_WORLD_PVP_REFUND_MAIL,
        "UPDATE character_world_pvp_bounty b "
        "JOIN characters c ON c.guid = b.sponsor_guid AND c.account = b.sponsor_account AND c.deleteDate IS NULL "
        "SET b.state = 2, b.refund_mail_id = ? WHERE b.sponsor_guid = ? AND b.id = ? "
        "AND (b.state = 6 OR (b.state = 1 AND b.expires_at <= UTC_TIMESTAMP()))",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_REFUND_MAIL,
        "INSERT INTO mail (id, messageType, stationery, mailTemplateId, sender, receiver, subject, body, "
        "has_items, expire_time, deliver_time, money, cod, checked) "
        "SELECT b.refund_mail_id, ?, ?, 0, ?, b.sponsor_guid, ?, '', 0, ?, ?, b.amount, 0, ? "
        "FROM character_world_pvp_bounty b WHERE b.sponsor_guid = ? AND b.id = ? AND b.refund_mail_id = ?",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_REFUND_MAIL,
        "SELECT id FROM mail WHERE id = ? AND receiver = ?",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_CLAIMS,
        "SELECT sponsor_guid, id, target_guid, amount FROM character_world_pvp_bounty "
        "WHERE hunter_guid = ? AND hunter_account = ? AND state = 3 ORDER BY sponsor_guid, id LIMIT 20",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_NEXT_CLAIM,
        "SELECT sponsor_guid, id FROM character_world_pvp_bounty "
        "WHERE hunter_guid = ? AND hunter_account = ? AND state = 3 AND amount <= ? "
        "ORDER BY claimed_at, sponsor_guid, id LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_CLAIM_AMOUNT,
        "SELECT amount FROM character_world_pvp_bounty WHERE sponsor_guid = ? AND id = ? "
        "AND hunter_guid = ? AND hunter_account = ? AND state = 3",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_REDEEM_WORLD_PVP_CLAIM,
        "UPDATE character_world_pvp_bounty b JOIN characters c ON c.guid = b.hunter_guid "
        "SET c.money = ?, b.state = 4 WHERE b.sponsor_guid = ? AND b.id = ? AND b.hunter_guid = ? "
        "AND b.hunter_account = ? AND c.account = b.hunter_account AND c.deleteDate IS NULL AND b.state = 3",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_CLAIM_STATE,
        "SELECT CAST(COALESCE((SELECT state FROM character_world_pvp_bounty WHERE sponsor_guid = ? "
        "AND id = ? AND hunter_guid = ? AND hunter_account = ?), -1) AS SIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTY_TARGETS,
        "SELECT CAST(b.target_guid AS UNSIGNED), CAST(b.sponsor_account AS UNSIGNED), "
        "CAST(COALESCE(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', b.expires_at), 0) AS UNSIGNED), "
        "CAST(SUM(b.amount) AS UNSIGNED) "
        "FROM character_world_pvp_bounty b JOIN characters v ON v.guid = b.target_guid "
        "AND v.account <> b.sponsor_account AND v.deleteDate IS NULL WHERE b.state = 1 "
        "AND (b.expires_at IS NULL OR b.expires_at > UTC_TIMESTAMP()) "
        "GROUP BY b.target_guid, b.sponsor_account, b.expires_at "
        "UNION ALL SELECT 0, 0, 0, 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_REC_WORLD_PVP_BOUNTY_MURDER,
        "INSERT INTO character_world_pvp_bounty_murder (offender_account, victim_account, offender_guid, occurred_at) "
        "VALUES (?, ?, ?, UTC_TIMESTAMP()) ON DUPLICATE KEY UPDATE "
        "offender_guid = IF(occurred_at <= UTC_TIMESTAMP() - INTERVAL 1 DAY, ?, offender_guid), "
        "counts_for_bounty = IF(occurred_at <= UTC_TIMESTAMP() - INTERVAL 1 DAY, 1, counts_for_bounty), "
        "occurred_at = IF(occurred_at <= UTC_TIMESTAMP() - INTERVAL 1 DAY, UTC_TIMESTAMP(), occurred_at)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_EXPIRE_WORLD_PVP_AUTOMATIC_BOUNTY,
        "UPDATE character_world_pvp_bounty SET state = 5 "
        "WHERE sponsor_guid = 0 AND target_guid = ? AND state = 1 AND expires_at <= UTC_TIMESTAMP()",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPSERT_WORLD_PVP_AUTOMATIC_BOUNTY,
        "INSERT INTO character_world_pvp_bounty "
        "(sponsor_guid, id, sponsor_account, target_guid, amount, state, expires_at) "
        "SELECT 0, UUID_SHORT(), 0, reward.target_guid, reward.amount, 1, reward.expires_at "
        "FROM (SELECT m.offender_guid AS target_guid, "
        "LEAST(2500000, (CAST(COUNT(*) AS SIGNED) - 2) * 250000) AS amount, "
        "MAX(m.occurred_at) + INTERVAL 1 DAY AS expires_at FROM character_world_pvp_bounty_murder m "
        "WHERE m.offender_guid = ? AND m.counts_for_bounty = 1 AND m.occurred_at > UTC_TIMESTAMP() - INTERVAL 1 DAY "
        "AND NOT EXISTS (SELECT 1 FROM character_world_pvp_bounty prior WHERE prior.target_guid = m.offender_guid "
        "AND prior.sponsor_guid = 0 AND prior.claimed_at >= m.occurred_at) "
        "GROUP BY m.offender_guid HAVING COUNT(*) >= 3) reward "
        "ON DUPLICATE KEY UPDATE character_world_pvp_bounty.amount = GREATEST(character_world_pvp_bounty.amount, "
        "reward.amount), character_world_pvp_bounty.expires_at = GREATEST(character_world_pvp_bounty.expires_at, "
        "reward.expires_at)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_BOUNTY_BOARD,
        "SELECT c.name, CAST(SUM(IF(b.sponsor_guid = 0, b.amount, 0)) AS UNSIGNED) AS automatic_gold, "
        "CAST(SUM(IF(b.sponsor_guid <> 0, b.amount, 0)) AS UNSIGNED) AS player_gold "
        "FROM character_world_pvp_bounty b JOIN characters c ON c.guid = b.target_guid "
        "AND c.deleteDate IS NULL AND c.account <> b.sponsor_account "
        "WHERE b.state = 1 AND (b.expires_at IS NULL OR b.expires_at > UTC_TIMESTAMP()) "
        "GROUP BY c.guid, c.name ORDER BY SUM(b.amount) DESC, c.guid LIMIT 20",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_PICKPOCKET,
        "INSERT INTO character_world_pvp_pickpocket "
        "(thief_account, victim_account, nonce, thief_guid, victim_guid, amount, "
        "item_guid, item_count, mail_id, attempted_at) "
        "SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, UTC_TIMESTAMP() FROM DUAL "
        "WHERE NOT EXISTS (SELECT 1 FROM character_world_pvp_pickpocket WHERE thief_account = ? "
        "AND victim_account = ? AND attempted_at > UTC_TIMESTAMP() - INTERVAL 10 MINUTE)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SETTLE_WORLD_PVP_PICKPOCKET,
        "UPDATE character_world_pvp_pickpocket r "
        "JOIN characters t ON t.guid = r.thief_guid AND t.account = r.thief_account AND t.deleteDate IS NULL "
        "JOIN characters v ON v.guid = r.victim_guid AND v.account = r.victim_account AND v.deleteDate IS NULL "
        "LEFT JOIN character_inventory ci ON ci.item = r.item_guid AND ci.guid = v.guid "
        "LEFT JOIN item_instance i ON i.guid = ci.item AND i.owner_guid = v.guid AND i.count = r.item_count "
        "SET t.money = IF(r.amount > 0, ?, t.money), v.money = IF(r.amount > 0, ?, v.money), "
        "t.playerFlags = t.playerFlags | ?, r.settled = 1, i.owner_guid = t.guid "
        "WHERE r.thief_account = ? AND r.victim_account = ? AND r.nonce = ? AND r.settled = 0 AND r.amount = ? "
        "AND (r.item_guid = 0 OR i.guid IS NOT NULL)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_PICKPOCKET_RESULT,
        "SELECT CAST(COALESCE(IF(r.settled = 1 AND r.item_guid > 0 AND NOT EXISTS("
        "SELECT 1 FROM item_instance i JOIN mail_items mi ON mi.item_guid = i.guid "
        "JOIN mail m ON m.id = mi.mail_id AND m.receiver = mi.receiver "
        "WHERE i.guid = r.item_guid AND i.owner_guid = r.thief_guid AND i.count = r.item_count "
        "AND mi.receiver = r.thief_guid AND m.id = r.mail_id "
        "AND NOT EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = r.item_guid)), 2, r.settled), "
        "IF(EXISTS(SELECT 1 FROM character_world_pvp_pickpocket recent "
        "WHERE recent.thief_account = request.thief_account AND recent.victim_account = request.victim_account "
        "AND recent.attempted_at > UTC_TIMESTAMP() - INTERVAL 10 MINUTE), -1, -2)) AS SIGNED), "
        "CAST(COALESCE(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', r.attempted_at + INTERVAL 5 MINUTE), 0) "
        "AS UNSIGNED) FROM (SELECT CAST(? AS UNSIGNED) AS thief_account, CAST(? AS UNSIGNED) AS victim_account, "
        "CAST(? AS UNSIGNED) AS nonce) request LEFT JOIN character_world_pvp_pickpocket r "
        "ON r.thief_account = request.thief_account AND r.victim_account = request.victim_account "
        "AND r.nonce = request.nonce",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_PICKPOCKET_EXPOSURE,
        "SELECT CAST(COALESCE(MAX(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', attempted_at + INTERVAL 5 MINUTE)), "
        "0) AS UNSIGNED) FROM character_world_pvp_pickpocket WHERE thief_guid = ? AND thief_account = ? "
        "AND settled = 1 AND attempted_at > UTC_TIMESTAMP() - INTERVAL 5 MINUTE",
        CONNECTION_BOTH);
    PrepareStatement(CHAR_INS_WILDERNESS_POUCH,
        "INSERT INTO character_wilderness_pouch "
        "(id, owner_guid, owner_account, map_id, phase_mask, x, y, z, copper, xp_loss, owner_until, auction_at) "
        "SELECT ?, guid, account, ?, ?, ?, ?, ?, ?, ?, UTC_TIMESTAMP(6) + INTERVAL 2 MINUTE, "
        "UTC_TIMESTAMP(6) + INTERVAL 15 MINUTE FROM characters "
        "WHERE guid = ? AND account = ? AND deleteDate IS NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_FUND_WILDERNESS_POUCH,
        "UPDATE character_wilderness_pouch p JOIN characters c "
        "ON c.guid = p.owner_guid AND c.account = p.owner_account AND c.deleteDate IS NULL "
        "SET c.money = IF(p.copper > 0, ?, c.money), c.xp = IF(p.xp_loss > 0, ?, c.xp), p.funded = 1 "
        "WHERE p.id = ? AND p.funded = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WILDERNESS_POUCH_FUNDING,
        "SELECT CAST(COALESCE(p.funded, 0) = 1 AND (p.item_guid IS NULL OR ("
        "EXISTS(SELECT 1 FROM item_instance i WHERE i.guid = p.item_guid AND i.owner_guid = 0) "
        "AND NOT EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = p.item_guid))) AS UNSIGNED), "
        "CAST(COALESCE(CEIL(TIMESTAMPDIFF(MICROSECOND, UTC_TIMESTAMP(6), p.auction_at) / 1000000), 0) AS SIGNED) "
        "FROM (SELECT CAST(? AS UNSIGNED) AS id, CAST(? AS UNSIGNED) AS guid, "
        "CAST(? AS UNSIGNED) AS account) request LEFT JOIN character_wilderness_pouch p "
        "ON p.id = request.id AND p.owner_guid = request.guid AND p.owner_account = request.account",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_NEARBY_WILDERNESS_POUCHES,
        "SELECT id, copper, phase_mask, x, y, z, CAST(COALESCE(item_guid, 0) AS UNSIGNED), item_entry, "
        "CAST(COALESCE((SELECT i.count FROM item_instance i WHERE i.guid = p.item_guid AND i.owner_guid = 0), 0) "
        "AS UNSIGNED) FROM character_wilderness_pouch p "
        "WHERE funded = 1 AND claimant_guid = 0 AND (copper > 0 OR item_guid IS NOT NULL) "
        "AND auction_at > UTC_TIMESTAMP(6) AND map_id = ? "
        "AND x BETWEEN ? AND ? AND y BETWEEN ? AND ? AND z BETWEEN ? AND ? "
        "AND ((owner_guid = ? AND owner_account = ?) "
        "OR (? = 1 AND owner_only_item = 0 AND owner_until <= UTC_TIMESTAMP(6))) "
        "AND (? = 0 OR id = ?) "
        "ORDER BY owner_until DESC, id LIMIT 20",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_CLAIM_WILDERNESS_POUCH,
        "UPDATE character_wilderness_pouch p JOIN characters c "
        "ON c.guid = ? AND c.account = ? AND c.deleteDate IS NULL "
        "LEFT JOIN item_instance i ON i.guid = p.item_guid AND i.owner_guid = 0 "
        "SET c.money = ? + p.copper, p.claimant_guid = c.guid, p.claim_nonce = ? "
        "WHERE p.id = ? AND p.funded = 1 AND p.claimant_guid = 0 AND p.copper <= ? "
        "AND p.item_guid <=> NULLIF(?, 0) AND (p.copper > 0 OR i.guid IS NOT NULL) "
        "AND p.auction_at > UTC_TIMESTAMP(6) "
        "AND ((p.owner_guid = c.guid AND p.owner_account = c.account) "
        "OR (? = 1 AND p.owner_only_item = 0 AND p.owner_until <= UTC_TIMESTAMP(6)))",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WILDERNESS_POUCH_CLAIM,
        "SELECT CAST(COALESCE((SELECT IF(p.item_guid IS NULL OR EXISTS("
        "SELECT 1 FROM item_instance i JOIN mail_items mi ON mi.item_guid = i.guid "
        "WHERE i.guid = p.item_guid AND i.owner_guid = p.claimant_guid AND mi.receiver = p.claimant_guid), 1, 2) "
        "FROM character_wilderness_pouch p WHERE p.id = ? AND p.claimant_guid = ? AND p.claim_nonce = ?), 0) "
        "AS UNSIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WILDERNESS_POUCHES_IN_GRID,
        "SELECT id, phase_mask, x, y, z, "
        "CAST(CEIL(TIMESTAMPDIFF(MICROSECOND, UTC_TIMESTAMP(6), auction_at) / 1000000) AS SIGNED) "
        "FROM character_wilderness_pouch "
        "WHERE map_id = ? AND funded = 1 AND claimant_guid = 0 AND (copper > 0 OR item_guid IS NOT NULL) "
        "AND auction_at > UTC_TIMESTAMP(6) "
        "AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WILDERNESS_AUCTION_POUCHES,
        "SELECT p.id, p.copper, CAST(p.owner_guid = buyer.guid AND p.owner_account = buyer.account AS UNSIGNED) "
        "AS is_owner, CAST(COALESCE(p.item_guid, 0) AS UNSIGNED), p.item_entry, p.item_value, "
        "CAST(COALESCE((SELECT i.count FROM item_instance i WHERE i.guid = p.item_guid AND i.owner_guid = 0), 0) "
        "AS UNSIGNED) "
        "FROM character_wilderness_pouch p "
        "CROSS JOIN (SELECT CAST(? AS UNSIGNED) AS guid, CAST(? AS UNSIGNED) AS account) buyer "
        "WHERE p.funded = 1 AND p.claimant_guid = 0 AND (p.copper > 0 OR p.item_guid IS NOT NULL) "
        "AND p.auction_at <= UTC_TIMESTAMP(6) "
        "AND ((p.owner_guid = buyer.guid AND p.owner_account = buyer.account) "
        "OR (p.owner_only_item = 0 AND p.auction_at <= UTC_TIMESTAMP(6) - INTERVAL 1 DAY)) AND (? = 0 OR p.id = ?) "
        "ORDER BY is_owner DESC, p.auction_at, p.id LIMIT 20",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_BUY_WILDERNESS_AUCTION_POUCH,
        "UPDATE character_wilderness_pouch p JOIN characters c "
        "ON c.guid = ? AND c.account = ? AND c.deleteDate IS NULL "
        "LEFT JOIN item_instance i ON i.guid = p.item_guid AND i.owner_guid = 0 "
        "SET c.money = ?, p.claimant_guid = c.guid, p.claim_nonce = ?, p.claim_fee = ? "
        "WHERE p.id = ? AND p.funded = 1 AND p.claimant_guid = 0 AND p.copper = ? "
        "AND p.item_guid <=> NULLIF(?, 0) AND (p.copper > 0 OR i.guid IS NOT NULL) "
        "AND p.auction_at <= UTC_TIMESTAMP(6) AND ((p.owner_guid = c.guid AND p.owner_account = c.account) "
        "OR (p.owner_only_item = 0 AND p.auction_at <= UTC_TIMESTAMP(6) - INTERVAL 1 DAY))",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WILDERNESS_GEAR_POUCH,
        "INSERT INTO character_wilderness_pouch "
        "(id, owner_guid, owner_account, map_id, phase_mask, x, y, z, copper, owner_until, auction_at, "
        "item_guid, item_entry, item_value, owner_only_item) "
        "SELECT ?, c.guid, c.account, ?, ?, ?, ?, ?, 0, UTC_TIMESTAMP(6) + INTERVAL 2 MINUTE, "
        "UTC_TIMESTAMP(6) + INTERVAL 15 MINUTE, i.guid, i.itemEntry, ?, ? FROM characters c "
        "JOIN character_inventory ci ON ci.guid = c.guid "
        "JOIN item_instance i ON i.guid = ci.item AND i.owner_guid = c.guid "
        "WHERE c.guid = ? AND c.account = ? AND c.deleteDate IS NULL AND i.guid = ? AND i.itemEntry = ? "
        "AND i.count = ? AND i.count > 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_FUND_WILDERNESS_GEAR_POUCH,
        "UPDATE character_wilderness_pouch p JOIN item_instance i ON i.guid = p.item_guid AND i.owner_guid = p.owner_guid "
        "SET i.owner_guid = 0, p.funded = 1 WHERE p.id = ? AND p.funded = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DETACH_WILDERNESS_GEAR,
        "DELETE ci FROM character_inventory ci JOIN character_wilderness_pouch p "
        "ON p.item_guid = ci.item AND p.owner_guid = ci.guid WHERE p.id = ? AND p.funded = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WILDERNESS_GEAR,
        "SELECT creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, "
        "randomPropertyId, durability, playedTime, text FROM item_instance WHERE guid = ? AND itemEntry = ? "
        "AND owner_guid = ?",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_WILDERNESS_GEAR_MAIL,
        "INSERT INTO mail (id, messageType, stationery, mailTemplateId, sender, receiver, subject, body, "
        "has_items, expire_time, deliver_time, money, cod, checked) "
        "SELECT ?, ?, ?, 0, ?, p.claimant_guid, ?, '', 1, ?, ?, 0, 0, ? FROM character_wilderness_pouch p "
        "WHERE p.id = ? AND p.claimant_guid = ? AND p.claim_nonce = ? AND p.item_guid IS NOT NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WILDERNESS_GEAR_MAIL_ITEM,
        "INSERT INTO mail_items (mail_id, item_guid, receiver) "
        "SELECT ?, p.item_guid, p.claimant_guid FROM character_wilderness_pouch p "
        "WHERE p.id = ? AND p.claimant_guid = ? AND p.claim_nonce = ? AND p.item_guid IS NOT NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_TRANSFER_WILDERNESS_GEAR,
        "UPDATE item_instance i JOIN character_wilderness_pouch p ON p.item_guid = i.guid "
        "SET i.owner_guid = p.claimant_guid WHERE p.id = ? AND p.claimant_guid = ? "
        "AND p.claim_nonce = ? AND i.owner_guid = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_PICKPOCKET_MAIL,
        "INSERT INTO mail (id, messageType, stationery, mailTemplateId, sender, receiver, subject, body, "
        "has_items, expire_time, deliver_time, money, cod, checked) "
        "SELECT ?, ?, ?, 0, ?, r.thief_guid, ?, '', 1, ?, ?, 0, 0, ? "
        "FROM character_world_pvp_pickpocket r "
        "WHERE r.thief_account = ? AND r.victim_account = ? AND r.nonce = ? "
        "AND r.mail_id = ? AND r.settled = 1 AND r.item_guid > 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_PICKPOCKET_MAIL_ITEM,
        "INSERT INTO mail_items (mail_id, item_guid, receiver) "
        "SELECT r.mail_id, r.item_guid, r.thief_guid FROM character_world_pvp_pickpocket r "
        "WHERE r.thief_account = ? AND r.victim_account = ? AND r.nonce = ? "
        "AND r.settled = 1 AND r.item_guid > 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DETACH_WORLD_PVP_PICKPOCKET_ITEM,
        "DELETE ci FROM character_inventory ci JOIN character_world_pvp_pickpocket r "
        "ON r.item_guid = ci.item AND r.victim_guid = ci.guid "
        "WHERE r.thief_account = ? AND r.victim_account = ? AND r.nonce = ? AND r.settled = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_RECEIPT,
        "INSERT INTO character_world_pvp_ear "
        "(item_guid, mail_id, killer_guid, victim_guid, account_low, account_high, awarded_at) "
        "SELECT ?, NULL, k.guid, v.guid, LEAST(k.account, v.account), GREATEST(k.account, v.account), UTC_TIMESTAMP(6) "
        "FROM characters k JOIN characters v ON v.guid = ? AND v.account = ? AND v.deleteDate IS NULL "
        "WHERE k.guid = ? AND k.account = ? AND k.deleteDate IS NULL AND k.guid <> v.guid AND k.account <> v.account "
        "AND NOT EXISTS(SELECT 1 FROM character_world_pvp_ear e "
        "WHERE e.account_low = LEAST(k.account, v.account) AND e.account_high = GREATEST(k.account, v.account) "
        "AND e.awarded_at > UTC_TIMESTAMP(6) - INTERVAL 1 DAY)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_UNAWARDED_WORLD_PVP_EAR,
        "DELETE i FROM item_instance i LEFT JOIN character_world_pvp_ear e "
        "ON e.item_guid = i.guid AND e.killer_guid = i.owner_guid "
        "WHERE i.guid = ? AND i.itemEntry = ? AND i.owner_guid = ? AND e.item_guid IS NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_INVENTORY,
        "INSERT INTO character_inventory (guid, bag, slot, item) "
        "SELECT e.killer_guid, ?, ?, e.item_guid FROM character_world_pvp_ear e "
        "WHERE e.item_guid = ? AND e.killer_guid = ?",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_EAR_RECEIPT,
        "SELECT CAST(COALESCE((SELECT IF(i.guid IS NOT NULL AND ci.item IS NOT NULL, 1, 2) "
        "FROM character_world_pvp_ear e "
        "LEFT JOIN item_instance i ON i.guid = e.item_guid AND i.owner_guid = e.killer_guid AND i.itemEntry = ? "
        "LEFT JOIN character_inventory ci ON ci.item = e.item_guid AND ci.guid = e.killer_guid "
        "AND ci.bag = ? AND ci.slot = ? WHERE e.item_guid = ? AND e.killer_guid = ?), 0) AS UNSIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_WORLD_PVP_UNSPENT_EARS,
        "SELECT item_guid FROM character_world_pvp_ear "
        "WHERE killer_guid = ? AND spent_reward_guid = 0 AND fence_paid_copper = 0 "
        "ORDER BY awarded_at, item_guid",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_PURCHASE,
        "INSERT INTO character_world_pvp_ear_purchase (reward_guid, mail_id, buyer_guid, reward_entry, ear_cost) "
        "SELECT ?, NULLIF(?, 0), c.guid, ?, ? FROM characters c "
        "WHERE c.guid = ? AND c.account = ? AND c.deleteDate IS NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_RESERVE_WORLD_PVP_EAR_PURCHASE_COST,
        "UPDATE character_world_pvp_ear e "
        "JOIN character_world_pvp_ear_purchase p ON p.buyer_guid = e.killer_guid "
        "JOIN character_inventory ci ON ci.item = e.item_guid AND ci.guid = p.buyer_guid "
        "JOIN item_instance i ON i.guid = e.item_guid AND i.owner_guid = p.buyer_guid "
        "SET e.spent_reward_guid = p.reward_guid "
        "WHERE p.reward_guid = ? AND e.item_guid = ? AND i.itemEntry = ? AND i.count = 1 "
        "AND p.funded = 0 AND e.spent_reward_guid = 0 AND e.fence_paid_copper = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_FUND_WORLD_PVP_EAR_PURCHASE,
        "UPDATE character_world_pvp_ear_purchase p SET p.funded = 1 "
        "WHERE p.reward_guid = ? AND p.funded = 0 AND p.ear_cost = ("
        "SELECT COUNT(*) FROM character_world_pvp_ear e WHERE e.spent_reward_guid = p.reward_guid)",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_RELEASE_WORLD_PVP_EAR_PURCHASE_COST,
        "UPDATE character_world_pvp_ear e JOIN character_world_pvp_ear_purchase p ON p.reward_guid = e.spent_reward_guid "
        "SET e.spent_reward_guid = 0 WHERE p.reward_guid = ? AND p.funded = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DELETE_WORLD_PVP_EAR_PURCHASE_COST,
        "DELETE ci, i FROM character_world_pvp_ear_purchase p "
        "JOIN character_world_pvp_ear e ON e.spent_reward_guid = p.reward_guid AND e.killer_guid = p.buyer_guid "
        "JOIN character_inventory ci ON ci.item = e.item_guid AND ci.guid = p.buyer_guid "
        "JOIN item_instance i ON i.guid = e.item_guid AND i.owner_guid = p.buyer_guid "
        "WHERE p.reward_guid = ? AND p.funded = 1 AND i.itemEntry = ? AND i.count = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_UNFUNDED_WORLD_PVP_EAR_REWARD,
        "DELETE i FROM item_instance i LEFT JOIN character_world_pvp_ear_purchase p "
        "ON p.reward_guid = i.guid AND p.buyer_guid = i.owner_guid AND p.reward_entry = i.itemEntry AND p.funded = 1 "
        "WHERE i.guid = ? AND i.itemEntry = ? AND i.owner_guid = ? AND p.reward_guid IS NULL",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_MAIL,
        "INSERT INTO mail (id, messageType, stationery, mailTemplateId, sender, receiver, subject, body, "
        "has_items, expire_time, deliver_time, money, cod, checked) "
        "SELECT ?, ?, ?, 0, ?, p.buyer_guid, ?, '', 1, ?, ?, 0, 0, ? FROM character_world_pvp_ear_purchase p "
        "WHERE p.reward_guid = ? AND p.mail_id = ? AND p.funded = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_MAIL_ITEM,
        "INSERT INTO mail_items (mail_id, item_guid, receiver) "
        "SELECT p.mail_id, p.reward_guid, p.buyer_guid FROM character_world_pvp_ear_purchase p "
        "WHERE p.reward_guid = ? AND p.mail_id = ? AND p.funded = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_INVENTORY,
        "INSERT INTO character_inventory (guid, bag, slot, item) "
        "SELECT p.buyer_guid, ?, ?, p.reward_guid FROM character_world_pvp_ear_purchase p "
        "WHERE p.reward_guid = ? AND p.mail_id IS NULL AND p.funded = 1",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_EAR_PURCHASE,
        "SELECT CAST(COALESCE((SELECT IF(p.funded = 0, 0, IF(EXISTS("
        "SELECT 1 FROM item_instance i "
        "WHERE i.guid = p.reward_guid AND i.owner_guid = p.buyer_guid AND i.itemEntry = p.reward_entry "
        "AND IF(p.mail_id IS NULL, EXISTS(SELECT 1 FROM character_inventory ci "
        "WHERE ci.item = i.guid AND ci.guid = p.buyer_guid AND ci.bag = ? AND ci.slot = ?), "
        "EXISTS(SELECT 1 FROM mail_items mi JOIN mail m ON m.id = mi.mail_id AND m.receiver = mi.receiver "
        "WHERE mi.item_guid = i.guid AND m.id = p.mail_id AND m.receiver = p.buyer_guid))) AND p.ear_cost = ("
        "SELECT COUNT(*) FROM character_world_pvp_ear e "
        "LEFT JOIN character_inventory ci ON ci.item = e.item_guid "
        "LEFT JOIN item_instance i ON i.guid = e.item_guid "
        "WHERE e.spent_reward_guid = p.reward_guid AND ci.item IS NULL AND i.guid IS NULL), 1, 2)) "
        "FROM character_world_pvp_ear_purchase p "
        "WHERE p.reward_guid = ? AND p.mail_id <=> NULLIF(?, 0) AND p.buyer_guid = ?), 0) "
        "AS UNSIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_SELL_WORLD_PVP_EAR_TO_FENCE,
        "UPDATE character_world_pvp_ear e JOIN characters c ON c.guid = e.killer_guid "
        "JOIN character_inventory ci ON ci.item = e.item_guid AND ci.guid = c.guid "
        "JOIN item_instance i ON i.guid = e.item_guid AND i.owner_guid = c.guid "
        "SET e.fence_paid_copper = ?, c.money = ? "
        "WHERE e.item_guid = ? AND c.guid = ? AND c.account = ? AND c.deleteDate IS NULL "
        "AND c.money = ? AND i.itemEntry = ? AND i.count = 1 "
        "AND e.spent_reward_guid = 0 AND e.fence_paid_copper = 0",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_WORLD_PVP_FENCE_EAR,
        "DELETE ci, i FROM character_world_pvp_ear e "
        "JOIN character_inventory ci ON ci.item = e.item_guid AND ci.guid = e.killer_guid "
        "JOIN item_instance i ON i.guid = e.item_guid AND i.owner_guid = e.killer_guid "
        "WHERE e.item_guid = ? AND e.killer_guid = ? AND e.fence_paid_copper = ? AND i.itemEntry = ?",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_WORLD_PVP_FENCE_SALE,
        "SELECT CAST(COALESCE((SELECT IF(e.fence_paid_copper = 0, 0, "
        "IF(e.fence_paid_copper = ? AND c.money = ? AND ci.item IS NULL AND i.guid IS NULL, 1, 2)) "
        "FROM character_world_pvp_ear e JOIN characters c ON c.guid = e.killer_guid "
        "LEFT JOIN character_inventory ci ON ci.item = e.item_guid "
        "LEFT JOIN item_instance i ON i.guid = e.item_guid "
        "WHERE e.item_guid = ? AND e.killer_guid = ? AND c.account = ? AND c.deleteDate IS NULL), 0) AS UNSIGNED)",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_UPD_CHAR_REMOVE_GHOST, "UPDATE characters SET playerFlags = (playerFlags & (~16)) WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_ACTION, "INSERT INTO character_action (guid, spec, button, action, type) VALUES (?, ?, ?, ?, ?)"
                     "ON DUPLICATE KEY UPDATE action = VALUES(action), type = VALUES(type)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_ACTION, "UPDATE character_action SET action = ?, type = ? WHERE guid = ? AND button = ? AND spec = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACTION_BY_BUTTON_SPEC, "DELETE FROM character_action WHERE guid = ? AND button = ? AND spec = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INVENTORY_BY_ITEM, "DELETE FROM character_inventory WHERE item = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_INVENTORY_BY_BAG_SLOT, "DELETE FROM character_inventory WHERE bag = ? AND slot = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_MAIL, "UPDATE mail SET has_items = ?, expire_time = ?, deliver_time = ?, money = ?, cod = ?, checked = ? WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_CHAR_QUESTSTATUS, "REPLACE INTO character_queststatus (guid, quest, status, explored, timer, mobcount1, mobcount2, mobcount3, mobcount4, itemcount1, itemcount2, itemcount3, itemcount4, itemcount5, itemcount6, playercount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_QUESTSTATUS_BY_QUEST, "DELETE FROM character_queststatus WHERE guid = ? AND quest = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_QUESTSTATUS_REWARDED, "INSERT IGNORE INTO character_queststatus_rewarded (guid, quest, active) VALUES (?, ?, 1)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_QUESTSTATUS_REWARDED_BY_QUEST, "DELETE FROM character_queststatus_rewarded WHERE guid = ? AND quest = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_QUESTSTATUS_REWARDED_FACTION_CHANGE, "UPDATE character_queststatus_rewarded SET quest = ? WHERE quest = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_QUESTSTATUS_REWARDED_ACTIVE, "UPDATE character_queststatus_rewarded SET active = 1 WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_QUESTSTATUS_REWARDED_ACTIVE_BY_QUEST, "UPDATE character_queststatus_rewarded SET active = 0 WHERE quest = ? AND guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_QUESTSTATUS_BY_QUEST, "SELECT status FROM character_queststatus WHERE guid = ? AND quest = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_QUESTSTATUS_SEASONAL_BY_QUEST, "SELECT 1 FROM character_queststatus_seasonal WHERE guid = ? AND quest = ? AND event = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAR_QUESTSTATUS_REWARDED_BY_QUEST, "SELECT 1 FROM character_queststatus_rewarded WHERE guid = ? AND quest = ? AND active = 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAR_SKILL_BY_SKILL, "DELETE FROM character_skills WHERE guid = ? AND skill = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_SKILLS, "INSERT INTO character_skills (guid, skill, value, max) VALUES (?, ?, ?, ?)"
                     "ON DUPLICATE KEY UPDATE value = VALUES(value), max = VALUES(max)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UDP_CHAR_SKILLS, "UPDATE character_skills SET value = ?, max = ? WHERE guid = ? AND skill = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_SPELL, "INSERT INTO character_spell (guid, spell, specMask) VALUES (?, ?, ?)"
                     "ON DUPLICATE KEY UPDATE specMask = VALUES(specMask)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_STATS, "DELETE FROM character_stats WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_STATS, "INSERT INTO character_stats (guid, maxhealth, maxpower1, maxpower2, maxpower3, maxpower4, maxpower5, maxpower6, maxpower7, strength, agility, stamina, intellect, spirit, "
                     "armor, resHoly, resFire, resNature, resFrost, resShadow, resArcane, blockPct, dodgePct, parryPct, critPct, rangedCritPct, spellCritPct, attackPower, rangedAttackPower, "
                     "spellPower, resilience) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_STATS, "SELECT maxhealth, strength, agility, stamina, intellect, spirit, armor, attackPower, spellPower, resilience FROM character_stats WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_PETITION_BY_OWNER, "DELETE FROM petition WHERE ownerguid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PETITION_SIGNATURE_BY_OWNER, "DELETE FROM petition_sign WHERE ownerguid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PETITION_BY_OWNER_AND_TYPE, "DELETE FROM petition WHERE ownerguid = ? AND type = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PETITION_SIGNATURE_BY_OWNER_AND_TYPE, "DELETE ps FROM petition_sign ps INNER JOIN petition p ON p.petition_id = ps.petition_id WHERE ps.ownerguid = ? AND p.type = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_GLYPHS, "INSERT INTO character_glyphs VALUES(?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_TALENT_BY_SPELL, "DELETE FROM character_talent WHERE guid = ? AND spell = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_CHAR_TALENT, "INSERT INTO character_talent (guid, spell, specMask) VALUES (?, ?, ?)"
                     "ON DUPLICATE KEY UPDATE specMask = VALUES(specMask)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_ACTION_EXCEPT_SPEC, "DELETE FROM character_action WHERE spec<>? AND guid = ?", CONNECTION_ASYNC);

    // Items that hold loot or money
    PrepareStatement(CHAR_SEL_ITEMCONTAINER_ITEMS, "SELECT containerGUID, itemid, item_index, count, randomPropertyId, randomSuffix, follow_loot_rules, freeforall, is_blocked, is_counted, is_underthreshold, needs_quest, conditionLootId FROM item_loot_storage", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_ITEMCONTAINER_SINGLE_ITEM, "DELETE FROM item_loot_storage WHERE containerGUID = ? AND itemid = ? AND count = ? AND item_index = ? LIMIT 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_ITEMCONTAINER_SINGLE_ITEM, "INSERT INTO item_loot_storage (containerGUID, itemid, item_index, count, randomPropertyId, randomSuffix, follow_loot_rules, freeforall, is_blocked, is_counted, is_underthreshold, needs_quest, conditionLootId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ITEMCONTAINER_CONTAINER, "DELETE FROM item_loot_storage WHERE containerGUID = ?", CONNECTION_ASYNC);

    // Calendar
    PrepareStatement(CHAR_REP_CALENDAR_EVENT, "REPLACE INTO calendar_events (id, creator, title, description, type, dungeon, eventtime, flags, time2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CALENDAR_EVENT, "DELETE FROM calendar_events WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_CALENDAR_INVITE, "REPLACE INTO calendar_invites (id, event, invitee, sender, status, statustime, `rank`, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CALENDAR_INVITE, "DELETE FROM calendar_invites WHERE id = ?", CONNECTION_ASYNC);

    // Pet
    PrepareStatement(CHAR_SEL_CHAR_PET_IDS, "SELECT id FROM character_pet WHERE owner = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAR_PET_DECLINEDNAME_BY_OWNER, "DELETE FROM character_pet_declinedname WHERE owner = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_PET_DECLINEDNAME, "DELETE FROM character_pet_declinedname WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_ADD_CHAR_PET_DECLINEDNAME, "INSERT INTO character_pet_declinedname (id, owner, genitive, dative, accusative, instrumental, prepositional) VALUES (?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PET_DECLINED_NAME, "SELECT genitive, dative, accusative, instrumental, prepositional FROM character_pet_declinedname WHERE owner = ? AND id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PET_AURA, "SELECT casterGuid, spell, effectMask, recalculateMask, stackCount, amount0, amount1, amount2, base_amount0, base_amount1, base_amount2, maxDuration, remainTime, remainCharges FROM pet_aura WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PET_SPELL, "SELECT spell, active FROM pet_spell WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PET_SPELL_COOLDOWN, "SELECT spell, category, time FROM pet_spell_cooldown WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PET_AURAS, "DELETE FROM pet_aura WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PET_SPELLS, "DELETE FROM pet_spell WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_PET_SPELL_COOLDOWNS, "DELETE FROM pet_spell_cooldown WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PET_SPELL_COOLDOWN, "INSERT INTO pet_spell_cooldown (guid, spell, category, time) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PET_SPELL, "INSERT INTO pet_spell (guid, spell, active) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PET_AURA, "INSERT INTO pet_aura (guid, casterGuid, spell, effectMask, recalculateMask, stackCount, amount0, amount1, amount2, "
                     "base_amount0, base_amount1, base_amount2, maxDuration, remainTime, remainCharges) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_CHAR_PETS, "SELECT id, entry, modelid, level, exp, Reactstate, slot, name, renamed, curhealth, curmana, curhappiness, abdata, savetime, CreatedBySpell, PetType FROM character_pet WHERE owner = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_PET_BY_OWNER, "DELETE FROM character_pet WHERE owner = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_PET_NAME, "UPDATE character_pet SET name = ?, renamed = 1 WHERE owner = ? AND id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_CHAR_PET_SLOT_BY_ID, "UPDATE character_pet SET slot = ? WHERE owner = ? AND id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_PET_BY_ID, "DELETE FROM character_pet WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_PET_BY_SLOT, "DELETE FROM character_pet WHERE owner = ? AND (slot = ? OR slot > ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_CHAR_PET, "REPLACE INTO character_pet (id, entry, owner, modelid, CreatedBySpell, PetType, level, exp, Reactstate, name, renamed, slot, curhealth, curmana, curhappiness, savetime, abdata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);

    // PvPstats
    PrepareStatement(CHAR_SEL_PVPSTATS_MAXID, "SELECT MAX(id) FROM pvpstats_battlegrounds", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_PVPSTATS_BATTLEGROUND, "INSERT INTO pvpstats_battlegrounds (id, winner_faction, bracket_id, type, date) VALUES (?, ?, ?, ?, NOW())", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PVPSTATS_PLAYER, "INSERT INTO pvpstats_players (battleground_id, character_guid, winner, score_killing_blows, score_deaths, score_honorable_kills, score_bonus_honor, score_damage_done, score_healing_done, attr_1, attr_2, attr_3, attr_4, attr_5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_PVPSTATS_FACTIONS_OVERALL, "SELECT winner_faction, COUNT(*) AS count FROM pvpstats_battlegrounds WHERE DATEDIFF(NOW(), date) < 7 GROUP BY winner_faction ORDER BY winner_faction ASC", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_PVPSTATS_BRACKET_MONTH, "SELECT character_guid, COUNT(character_guid) AS count, characters.name as character_name FROM pvpstats_players INNER JOIN pvpstats_battlegrounds ON pvpstats_players.battleground_id = pvpstats_battlegrounds.id AND bracket_id = ? AND MONTH(date) = MONTH(NOW()) AND YEAR(date) = YEAR(NOW()) INNER JOIN characters ON pvpstats_players.character_guid = characters.guid AND characters.deleteDate IS NULL WHERE pvpstats_players.winner = 1 GROUP BY character_guid ORDER BY count(character_guid) DESC LIMIT 0, ?", CONNECTION_SYNCH);

    // Deserter tracker
    PrepareStatement(CHAR_INS_DESERTER_TRACK, "INSERT INTO battleground_deserters (guid, type, datetime) VALUES (?, ?, NOW())", CONNECTION_ASYNC);

    // QuestTracker
    PrepareStatement(CHAR_INS_QUEST_TRACK, "INSERT INTO quest_tracker (id, character_guid, quest_accept_time, core_hash, core_revision) VALUES (?, ?, NOW(), ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_QUEST_TRACK_GM_COMPLETE, "UPDATE quest_tracker SET completed_by_gm = 1 WHERE id = ? AND character_guid = ? ORDER BY quest_accept_time DESC LIMIT 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_QUEST_TRACK_COMPLETE_TIME, "UPDATE quest_tracker SET quest_complete_time = NOW() WHERE id = ? AND character_guid = ? ORDER BY quest_accept_time DESC LIMIT 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_QUEST_TRACK_ABANDON_TIME, "UPDATE quest_tracker SET quest_abandon_time = NOW() WHERE id = ? AND character_guid = ? ORDER BY quest_accept_time DESC LIMIT 1", CONNECTION_ASYNC);

    // Recovery Item
    PrepareStatement(CHAR_INS_RECOVERY_ITEM, "INSERT INTO recovery_item (Guid, ItemEntry, Count, DeleteDate) VALUES (?, ?, ?, UNIX_TIMESTAMP())", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_RECOVERY_ITEM, "SELECT id, itemEntry, Count, Guid FROM recovery_item WHERE id = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_RECOVERY_ITEM_LIST, "SELECT id, itemEntry, Count FROM recovery_item WHERE Guid = ? ORDER BY id DESC", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_RECOVERY_ITEM, "DELETE FROM recovery_item WHERE Guid = ? AND ItemEntry = ? AND Count = ? ORDER BY Id DESC LIMIT 1", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_RECOVERY_ITEM_BY_RECOVERY_ID, "DELETE FROM recovery_item WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_RECOVERY_ITEM_OLD_ITEMS, "SELECT Guid, ItemEntry FROM recovery_item WHERE DeleteDate IS NOT NULL AND DeleteDate < ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_RECOVERY_ITEM_BY_GUID, "DELETE FROM recovery_item WHERE Guid = ?", CONNECTION_ASYNC);

    PrepareStatement(CHAR_SEL_HONORPOINTS, "SELECT totalHonorPoints FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ARENAPOINTS, "SELECT arenaPoints FROM characters WHERE guid = ?", CONNECTION_SYNCH);

    // Character names
    PrepareStatement(CHAR_INS_RESERVED_PLAYER_NAME, "INSERT IGNORE INTO reserved_name (name) VALUES (?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_PROFANITY_PLAYER_NAME, "INSERT IGNORE INTO profanity_name (name) VALUES (?)", CONNECTION_ASYNC);

    // Chat filter
    PrepareStatement(CHAR_SEL_CHAT_FILTER, "SELECT ID, Word FROM chat_filter ORDER BY ID", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_CHAT_FILTER_WORD, "SELECT ID FROM chat_filter WHERE Word = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_CHAT_FILTER_WORD, "INSERT INTO chat_filter (Word) VALUES (?)", CONNECTION_SYNCH);
    PrepareStatement(CHAR_DEL_CHAT_FILTER_WORD, "DELETE FROM chat_filter WHERE Word = ?", CONNECTION_SYNCH);

    // Character settings
    PrepareStatement(CHAR_SEL_CHAR_SETTINGS, "SELECT source, data FROM character_settings WHERE guid = ?", CONNECTION_BOTH);
    PrepareStatement(CHAR_REP_CHAR_SETTINGS, "REPLACE INTO character_settings (guid, source, data) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_CHAR_SETTINGS, "DELETE FROM character_settings WHERE guid = ?", CONNECTION_ASYNC);

    // Instance saved data. Stores the states of gameobjects in instances to be loaded on server start
    PrepareStatement(CHAR_SELECT_INSTANCE_SAVED_DATA, "SELECT guid, state FROM instance_saved_go_state_data WHERE id = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INSERT_INSTANCE_SAVED_DATA, "INSERT INTO instance_saved_go_state_data (id, guid, state) VALUES (?, ?, ?)"
        "ON DUPLICATE KEY UPDATE state = VALUES(state)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DELETE_INSTANCE_SAVED_DATA, "DELETE FROM instance_saved_go_state_data WHERE id = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SANITIZE_INSTANCE_SAVED_DATA, "DELETE FROM instance_saved_go_state_data WHERE id NOT IN (SELECT instance.id FROM instance)", CONNECTION_ASYNC);

    // world_state
    PrepareStatement(CHAR_SEL_WORLD_STATE, "SELECT Id, Data FROM world_state", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_WORLD_STATE, "REPLACE INTO world_state (Id, Data) VALUES(?, ?)", CONNECTION_ASYNC);

    PrepareStatement(CHAR_SEL_DIGITAL_STORAGE,
        "SELECT capacity, revision FROM character_digital_storage WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_DIGITAL_ITEMS,
        "SELECT ii.creatorGuid, ii.giftCreatorGuid, ii.count, ii.duration, ii.charges, ii.flags, ii.enchantments, "
        "ii.randomPropertyId, ii.durability, ii.playedTime, ii.text, ds.item, ii.itemEntry, ds.favorite, ii.owner_guid, "
        "(EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ds.item) "
        "OR EXISTS(SELECT 1 FROM mail_items mi WHERE mi.item_guid = ds.item) "
        "OR EXISTS(SELECT 1 FROM auctionhouse ah WHERE ah.itemguid = ds.item) "
        "OR EXISTS(SELECT 1 FROM guild_bank_item gb WHERE gb.item_guid = ds.item)), ds.tag, ds.split "
        "FROM character_digital_storage_item ds LEFT JOIN item_instance ii ON ii.guid = ds.item WHERE ds.guid = ?",
        CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_DIGITAL_STORAGE,
        "REPLACE INTO character_digital_storage (guid, capacity, revision) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_DIGITAL_ITEM,
        "REPLACE INTO character_digital_storage_item (guid, item, favorite, tag, split) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_DIGITAL_ITEM,
        "DELETE FROM character_digital_storage_item WHERE guid = ? AND item = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_DIGITAL_STORAGE_OWNER,
        "DELETE FROM character_digital_storage WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_DIGITAL_ITEMS_OWNER,
        "DELETE FROM character_digital_storage_item WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_DIGITAL_ITEM_BY_GUID,
        "DELETE FROM character_digital_storage_item WHERE item = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_UPD_GUILD_BANK_TAB_SLOTS, "UPDATE guild_bank_tab SET slots = ? WHERE guildid = ? AND TabId = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_ACCOUNT_BANK,
        "SELECT capacity, revision, unlocked FROM account_bank WHERE account = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_ACCOUNT_BANK_ITEMS,
        "SELECT ii.creatorGuid, ii.giftCreatorGuid, ii.count, ii.duration, ii.charges, ii.flags, ii.enchantments, "
        "ii.randomPropertyId, ii.durability, ii.playedTime, ii.text, ab.item, ii.itemEntry, ab.favorite, ii.owner_guid, "
        "(EXISTS(SELECT 1 FROM character_inventory ci WHERE ci.item = ab.item) "
        "OR EXISTS(SELECT 1 FROM mail_items mi WHERE mi.item_guid = ab.item) "
        "OR EXISTS(SELECT 1 FROM auctionhouse ah WHERE ah.itemguid = ab.item) "
        "OR EXISTS(SELECT 1 FROM guild_bank_item gb WHERE gb.item_guid = ab.item) "
        "OR EXISTS(SELECT 1 FROM character_digital_storage_item ds WHERE ds.item = ab.item)), ab.tag, ab.split "
        "FROM account_bank_item ab LEFT JOIN item_instance ii ON ii.guid = ab.item WHERE ab.account = ?",
        CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_ACCOUNT_BANK,
        "REPLACE INTO account_bank (account, capacity, revision, unlocked) VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_REP_ACCOUNT_BANK_ITEM,
        "REPLACE INTO account_bank_item (account, item, favorite, tag, split) VALUES (?, ?, ?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_DEL_ACCOUNT_BANK_ITEM,
        "DELETE FROM account_bank_item WHERE account = ? AND item = ?", CONNECTION_ASYNC);

#ifdef MOD_MANASTORM_ENDLESS
    // mod-manastorm-endless (SQL as in CoA)
    PrepareStatement(CHAR_SEL_MANASTORM_LOADOUT, "SELECT slot, spell FROM ascension_manastorm_loadout WHERE guid = ? UNION ALL SELECT 255, 0", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_MANASTORM_LOADOUT, "REPLACE INTO ascension_manastorm_loadout (guid, slot, spell) VALUES (?, ?, ?)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MANASTORM_XP_LEVEL, "SELECT level, playerFlags FROM characters WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MANASTORM_FLOOR_XP, "SELECT base_xp FROM character_manastorm_pending_experience WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_ADD_MANASTORM_FLOOR_XP, "INSERT INTO character_manastorm_pending_experience (guid, base_xp) VALUES (?, ?) "
        "ON DUPLICATE KEY UPDATE base_xp = base_xp + VALUES(base_xp)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_CLAIM_MANASTORM_FLOOR_XP, "UPDATE character_manastorm_pending_experience SET base_xp = base_xp - ? WHERE guid = ?", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MANASTORM_FIRST_CLEAR, "SELECT COUNT(*) FROM character_manastorm_completed_depth "
        "WHERE guid = ? AND mode = ? AND track = ? AND depth = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_SEL_MANASTORM_COMPLETION_REWARD, "SELECT remainder_bp, earned FROM character_manastorm_completion_reward_state "
        "WHERE guid = ? AND mode = ? AND track = ? AND reward_key = ? LIMIT 1", CONNECTION_SYNCH);
    PrepareStatement(CHAR_REP_MANASTORM_COMPLETION_REWARD, "INSERT INTO character_manastorm_completion_reward_state "
        "(guid, mode, track, reward_key, remainder_bp, earned) VALUES (?, ?, ?, ?, ?, ?) "
        "ON DUPLICATE KEY UPDATE remainder_bp = VALUES(remainder_bp), earned = VALUES(earned)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_SEL_MANASTORM_WEEKLY_CACHE, "SELECT COALESCE(MAX(reset_at), 0), COALESCE(MAX(caches_received), 0) "
        "FROM manastorm_weekly_cache_lockout WHERE guid = ?", CONNECTION_SYNCH);
    PrepareStatement(CHAR_INS_MANASTORM_WEEKLY_CACHE, "INSERT INTO manastorm_weekly_cache_lockout (guid, reset_at, caches_received) "
        "VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE reset_at = IF(reset_at = ? AND caches_received = ?, VALUES(reset_at), 0), "
        "caches_received = VALUES(caches_received)", CONNECTION_ASYNC);
    PrepareStatement(CHAR_INS_MANASTORM_STAGE_RECEIPT, "INSERT INTO character_manastorm_stage_receipt (guid, run_seed, run_id, depth) "
        "VALUES (?, ?, ?, ?)", CONNECTION_ASYNC);
#endif

    // CHAR_NO_OP_PROVIDE_REALM_CONTEXT is a no-op query that accepts a single parameter: the realm ID.
    // This query is used specifically in cross-realm scenarios when the database transaction
    // lacks sufficient context to determine which realm's database the query should target.
    // By providing the realm ID explicitly, this ensures that mysql reverse proxy will use
    // correct realm database for the transaction.
    PrepareStatement(CHAR_NO_OP_PROVIDE_REALM_CONTEXT, "SELECT ? AS no_op", CONNECTION_ASYNC);
}

CharacterDatabaseConnection::CharacterDatabaseConnection(MySQLConnectionInfo& connInfo) : MySQLConnection(connInfo)
{
}

CharacterDatabaseConnection::CharacterDatabaseConnection(ProducerConsumerQueue<SQLOperation*>* q, MySQLConnectionInfo& connInfo) : MySQLConnection(q, connInfo)
{
}

CharacterDatabaseConnection::~CharacterDatabaseConnection()
{
}
