--- **AceTimer-3.0** provides a central facility for registering timers.
-- AceTimer supports one-shot timers and repeating timers.
local MAJOR, MINOR = "AceTimer-3.0", 5
local AceTimer, oldminor = LibStub:NewLibrary(MAJOR, MINOR)
if not AceTimer then return end
AceTimer.hash = AceTimer.hash or {}
AceTimer.selfs = AceTimer.selfs or {}
AceTimer.frame = AceTimer.frame or CreateFrame("Frame", "AceTimer30Frame")
local assert, error, loadstring = assert, error, loadstring
local setmetatable, rawset, rawget = setmetatable, rawset, rawget
local select, pairs, type, next, tostring = select, pairs, type, next, tostring
local floor, max, min = math.floor, math.max, math.min
local tconcat = table.concat
local GetTime = GetTime
local timerCache = nil
local HZ = 11
local BUCKETS = 131
local hash = AceTimer.hash
for i=1,BUCKETS do hash[i] = hash[i] or false end
local xpcall = xpcall
local function errorhandler(err) return geterrorhandler()(err) end
local function CreateDispatcher(argCount)
	local code = [[
		local xpcall, eh = ...
		local method, ARGS
		local function call() return method(ARGS) end
		local function dispatch(func, ...)
			 method = func
			 if not method then return end
			 ARGS = ...
			 return xpcall(call, eh)
		end
		return dispatch
	]]
	local ARGS = {}
	for i = 1, argCount do ARGS[i] = "arg"..i end
	code = code:gsub("ARGS", tconcat(ARGS, ", "))
	return assert(loadstring(code, "safecall Dispatcher["..argCount.."]"))(xpcall, errorhandler)
end
local Dispatchers = setmetatable({}, {__index=function(self, argCount) local dispatcher = CreateDispatcher(argCount) rawset(self, argCount, dispatcher) return dispatcher end})
Dispatchers[0] = function(func) return xpcall(func, errorhandler) end
local function safecall(func, ...) return Dispatchers[select('#', ...)](func, ...) end
local lastint = floor(GetTime() * HZ)
local function OnUpdate()
	local now = GetTime()
	local nowint = floor(now * HZ)
	if nowint == lastint then return end
	local soon = now + 1
	for curint = (max(lastint, nowint - BUCKETS) + 1), nowint do
		local curbucket = (curint % BUCKETS)+1
		local nexttimer = hash[curbucket]
		hash[curbucket] = false
		while nexttimer do
			local timer = nexttimer
			nexttimer = timer.next
			local when = timer.when
			if when < soon then
				local callback = timer.callback
				if type(callback) == "string" then
					safecall(timer.object[callback], timer.object, timer.arg)
				elseif callback then
					safecall(callback, timer.arg)
				else
					timer.delay = nil
				end
				local delay = timer.delay
				if not delay then
					AceTimer.selfs[timer.object][tostring(timer)] = nil
					timerCache = timer
				else
					local newtime = when + delay
					if newtime < now then newtime = now + delay end
					timer.when = newtime
					local bucket = (floor(newtime * HZ) % BUCKETS) + 1
					timer.next = hash[bucket]
					hash[bucket] = timer
				end
			else
				timer.next = hash[curbucket]
				hash[curbucket] = timer
			end
		end
	end
	lastint = nowint
end
local function Reg(self, callback, delay, arg, repeating)
	if type(callback) ~= "string" and type(callback) ~= "function" then error(MAJOR..": bad callback", 3) end
	if type(callback) == "string" then
		if type(self)~="table" then error(MAJOR..": self must be a table.", 3) end
		if type(self[callback]) ~= "function" then error(MAJOR..": method not found on target object.", 3) end
	end
	if delay < (1 / (HZ - 1)) then delay = 1 / (HZ - 1) end
	local now = GetTime()
	local timer = timerCache or {}
	timerCache = nil
	timer.object = self
	timer.callback = callback
	timer.delay = (repeating and delay)
	timer.arg = arg
	timer.when = now + delay
	local bucket = (floor((now+delay)*HZ) % BUCKETS) + 1
	timer.next = hash[bucket]
	hash[bucket] = timer
	local handle = tostring(timer)
	local selftimers = AceTimer.selfs[self]
	if not selftimers then selftimers = {} AceTimer.selfs[self] = selftimers end
	selftimers[handle] = timer
	selftimers.__ops = (selftimers.__ops or 0) + 1
	return handle
end
function AceTimer:ScheduleTimer(callback, delay, arg) return Reg(self, callback, delay, arg) end
function AceTimer:ScheduleRepeatingTimer(callback, delay, arg) return Reg(self, callback, delay, arg, true) end
function AceTimer:CancelTimer(handle, silent)
	if not handle then return end
	if type(handle) ~= "string" then error(MAJOR..": CancelTimer(handle): 'handle' - expected a string", 2) end
	local selftimers = AceTimer.selfs[self]
	local timer = selftimers and selftimers[handle]
	if silent then
		if timer then timer.callback = nil timer.delay = nil end
		return not not timer
	else
		if not timer then geterrorhandler()(MAJOR..": no such timer registered") return false end
		if not timer.callback then geterrorhandler()(MAJOR..": timer already cancelled or expired") return false end
		timer.callback = nil
		timer.delay = nil
		return true
	end
end
function AceTimer:CancelAllTimers()
	local selftimers = AceTimer.selfs[self]
	if selftimers then
		for handle,v in pairs(selftimers) do if type(v) == "table" then AceTimer.CancelTimer(self, handle, true) end end
	end
end
function AceTimer:TimeLeft(handle)
	if not handle then return end
	if type(handle) ~= "string" then error(MAJOR..": TimeLeft(handle): 'handle' - expected a string", 2) end
	local selftimers = AceTimer.selfs[self]
	local timer = selftimers and selftimers[handle]
	if not timer then geterrorhandler()(MAJOR..": no such timer registered") return false end
	return timer.when - GetTime()
end
local lastCleaned = nil
local function OnEvent(this, event)
	if event~="PLAYER_REGEN_ENABLED" then return end
	local selfs = AceTimer.selfs
	local self = next(selfs, lastCleaned)
	if not self then self = next(selfs) end
	lastCleaned = self
	if not self then return end
	local list = selfs[self]
	if (list.__ops or 0) < 250 then return end
	local newlist = {}
	local n=0
	for k,v in pairs(list) do newlist[k] = v n=n+1 end
	newlist.__ops = 0
	if n>BUCKETS then DEFAULT_CHAT_FRAME:AddMessage(MAJOR..": Warning: The addon/module '"..tostring(self).."' has "..n.." live timers.") end
	selfs[self] = newlist
end
AceTimer.embeds = AceTimer.embeds or {}
local mixins = {"ScheduleTimer", "ScheduleRepeatingTimer", "CancelTimer", "CancelAllTimers", "TimeLeft"}
function AceTimer:Embed(target) AceTimer.embeds[target] = true for _,v in pairs(mixins) do target[v] = AceTimer[v] end return target end
function AceTimer:OnEmbedDisable( target ) target:CancelAllTimers() end
for addon in pairs(AceTimer.embeds) do AceTimer:Embed(addon) end
AceTimer.frame:SetScript("OnUpdate", OnUpdate)
AceTimer.frame:SetScript("OnEvent", OnEvent)
AceTimer.frame:RegisterEvent("PLAYER_REGEN_ENABLED")
