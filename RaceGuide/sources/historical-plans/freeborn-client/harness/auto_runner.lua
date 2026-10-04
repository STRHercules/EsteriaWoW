-- The automatic path: a login asks the server, and the server's reply records the emblem.
-- This is the whole point of the feature -- no player input at all.

local frame = LAST_FRAME;

print("badges before: " .. BadgeReport());
frame.scripts.OnEvent(frame, "PLAYER_ENTERING_WORLD", true, false);
print("sent on login: " .. ((#SENT > 0) and table.concat(SENT, " | ") or "(nothing)"));
print("badges after login: " .. BadgeReport());

SENT = {};
frame.scripts.OnEvent(frame, "CHAT_MSG_ADDON", "FREEBORN", "team\t3");
print("badges after Freeborn reply: " .. BadgeReport());

-- A reply that says the character is NOT Freeborn must record nothing.
SafeSet(BADGES[1], "System Default");
frame.scripts.OnEvent(frame, "CHAT_MSG_ADDON", "FREEBORN", "team\t1");
print("badges after Horde reply: " .. BadgeReport());

-- A chat message must never be mistaken for the reply now.
frame.scripts.OnEvent(frame, "CHAT_MSG_SYSTEM", "|cff00ccff[Freeborn]|r persistent team Freeborn.");
print("badges after a chat line: " .. BadgeReport());
