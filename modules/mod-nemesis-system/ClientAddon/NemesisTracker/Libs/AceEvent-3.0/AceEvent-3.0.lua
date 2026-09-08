--- AceEvent-3.0 provides event registration and secure dispatching.
-- All dispatching is done using **CallbackHandler-1.0**. AceEvent is a simple wrapper around
-- CallbackHandler, and dispatches all game events or addon message to the registrees.
--
-- **AceEvent-3.0** can be embeded into your addon, either explicitly by calling AceEvent:Embed(MyAddon) or by 
-- specifying it as an embeded library in your AceAddon. All functions will be available on your addon object
-- and can be accessed directly, without having to explicitly call AceEvent itself.\\
-- It is recommended to embed AceEvent, otherwise you'll have to specify a custom `self` on all calls you
-- make into AceEvent.
-- @class file
-- @name AceEvent-3.0
-- @release $Id: AceEvent-3.0.lua 877 2009-11-02 15:56:50Z nevcairiel $
local MAJOR, MINOR = "AceEvent-3.0", 3
local AceEvent = LibStub:NewLibrary(MAJOR, MINOR)

if not AceEvent then return end

local pairs = pairs
local CallbackHandler = LibStub:GetLibrary("CallbackHandler-1.0")

AceEvent.frame = AceEvent.frame or CreateFrame("Frame", "AceEvent30Frame")
AceEvent.embeds = AceEvent.embeds or {}

if not AceEvent.events then
	AceEvent.events = CallbackHandler:New(AceEvent,
		"RegisterEvent", "UnregisterEvent", "UnregisterAllEvents")
end

function AceEvent.events:OnUsed(target, eventname)
	AceEvent.frame:RegisterEvent(eventname)
end

function AceEvent.events:OnUnused(target, eventname)
	AceEvent.frame:UnregisterEvent(eventname)
end

if not AceEvent.messages then
	AceEvent.messages = CallbackHandler:New(AceEvent,
		"RegisterMessage", "UnregisterMessage", "UnregisterAllMessages"
	)
	AceEvent.SendMessage = AceEvent.messages.Fire
end

local mixins = {
	"RegisterEvent", "UnregisterEvent",
	"RegisterMessage", "UnregisterMessage",
	"SendMessage",
	"UnregisterAllEvents", "UnregisterAllMessages",
}

function AceEvent:Embed(target)
	for k, v in pairs(mixins) do
		target[v] = self[v]
	end
	self.embeds[target] = true
	return target
end

function AceEvent:OnEmbedDisable(target)
	target:UnregisterAllEvents()
	target:UnregisterAllMessages()
end

local events = AceEvent.events
AceEvent.frame:SetScript("OnEvent", function(this, event, ...)
	events:Fire(event, ...)
end)

for target, v in pairs(AceEvent.embeds) do
	AceEvent:Embed(target)
end
