-- Extra stubs for running the shipped FreebornClaim addon under the same harness.

SENT = {};

DEFAULT_CHAT_FRAME = {};
function DEFAULT_CHAT_FRAME:AddMessage(message)
    print("CHAT| " .. tostring(message));
end

PLAYER_NAME = PLAYER_NAME or "Dobby";
function UnitName(unit)
    return PLAYER_NAME;
end

SlashCmdList = {};

SendAddonMessage = function(prefix, body, kind, target)
    SENT[#SENT + 1] = tostring(prefix) .. "/" .. tostring(body) .. "/" .. tostring(kind);
end;
