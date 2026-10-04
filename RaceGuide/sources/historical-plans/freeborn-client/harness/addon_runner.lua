-- Drives the shipped FreebornClaim addon: the /freeborn report and the login claim.

print("== ADDON MODE=" .. MODE .. " pending=" .. tostring(CVARS["freebornPending"]) ..
    " probe=" .. tostring(CVARS["freebornProbe"]) .. " player=" .. tostring(PLAYER_NAME) .. " ==");

print("--- /freeborn ---");
SlashCmdList["FREEBORN"]();

print("--- login (PLAYER_ENTERING_WORLD, isInitialLogin=true) ---");
local frame = LAST_FRAME;
frame.scripts.OnEvent(frame, "PLAYER_ENTERING_WORLD", true);
print("sent: " .. ((#SENT > 0) and table.concat(SENT, " | ") or "(nothing)"));
print("freebornPending is now '" .. tostring(CVARS["freebornPending"]) .. "'");

print("--- login again (must not claim twice) ---");
SENT = {};
frame.scripts.OnEvent(frame, "PLAYER_ENTERING_WORLD", true);
print("sent: " .. ((#SENT > 0) and table.concat(SENT, " | ") or "(nothing)"));

local left = {};
for name in pairs(CVARS) do
    left[#left + 1] = name .. "=" .. tostring(CVARS[name]);
end
table.sort(left);
print("cvars after: " .. table.concat(left, ", "));

print("== done ==");
