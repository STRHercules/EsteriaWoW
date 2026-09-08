CREATE TABLE IF NOT EXISTS `character_nemesis_monthly_kills` (
    `month_key` int unsigned NOT NULL COMMENT 'UTC month bucket in YYYYMM format',
    `character_guid` int unsigned NOT NULL COMMENT 'Character guid that landed the killing blow',
    `account_id` int unsigned NOT NULL DEFAULT 0 COMMENT 'Owning account id for convenience in web queries',
    `character_name` varchar(12) NOT NULL COMMENT 'Character name snapshot for simple leaderboard rendering',
    `kill_count` int unsigned NOT NULL DEFAULT 0 COMMENT 'Total nemeses killed during the month',
    `revenge_kill_count` int unsigned NOT NULL DEFAULT 0 COMMENT 'Kills against the killer\'s own nemeses during the month',
    `bounty_kill_count` int unsigned NOT NULL DEFAULT 0 COMMENT 'Kills against other players\' nemeses during the month',
    `highest_rank_killed` tinyint unsigned NOT NULL DEFAULT 0 COMMENT 'Highest nemesis rank killed during the month',
    `last_kill_at` int unsigned NOT NULL DEFAULT 0 COMMENT 'Last kill time as unix timestamp',
    PRIMARY KEY (`month_key`, `character_guid`),
    KEY `idx_character_nemesis_monthly_kills_account` (`account_id`),
    KEY `idx_character_nemesis_monthly_kills_rank` (`month_key`, `highest_rank_killed`),
    KEY `idx_character_nemesis_monthly_kills_last_kill` (`month_key`, `last_kill_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
