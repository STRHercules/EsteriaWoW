--[[ ECS_Anim.lua ---------------------------------------------------------------
    Esteria Character Select - reusable animation framework (spec 7, 32).

    3.3.5a has NO AnimationGroup, so glue hand-rolls fades. GlueParent already owns
    one driver for GLUE SCREEN fades (GlueFrameFadeUpdate over FADEFRAMES); ECS
    must not fight it. This module therefore:
      * owns exactly ONE OnUpdate for all roster tweens
      * never touches a property GlueFrameFade owns, so the two cannot conflict
      * HIDES its driver whenever no tween is active, so idle cost is zero
        (a hidden frame does not receive OnUpdate in this client)

    Tweens are value-based against an abstract target with a setter function, not
    frame-specific, so the whole thing is unit-testable with plain tables and no
    client at all.

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Anim = ECS.Anim or {};

local A = ECS.Anim;
local C = ECS.Const;

-- ---------------------------------------------------------------- easing
A.Easings = {
    linear = function(t) return t; end,
    quadIn = function(t) return t * t; end,
    quadOut = function(t) return 1 - (1 - t) * (1 - t); end,
    quadInOut = function(t)
        if ( t < 0.5 ) then return 2 * t * t; end
        local u = 1 - t;
        return 1 - 2 * u * u;
    end,
    cubicOut = function(t)
        local u = 1 - t;
        return 1 - u * u * u;
    end,
    -- slight overshoot, for selection "pop"
    backOut = function(t)
        local s = 1.70158;
        local u = t - 1;
        return 1 + (s + 1) * u * u * u + s * u * u;
    end,
};

function A.Ease(name, t)
    local fn = A.Easings[name] or A.Easings.linear;
    return fn(t);
end

-- ---------------------------------------------------------------- pool
-- spec 32: reuse tween tables rather than allocating per hover event.
A.active = A.active or {};   -- array of live tweens
A.pool   = A.pool or {};     -- recycled tween tables
A.lookup = A.lookup or {};   -- target -> { key -> tween }

local function Acquire()
    local tween = table.remove(A.pool);
    if ( not tween ) then
        tween = {};
    end
    return tween;
end

local function Release(tween)
    tween.target = nil;
    tween.setter = nil;
    tween.onDone = nil;
    tween.onUpdate = nil;
    tween.from = nil;
    tween.to = nil;
    tween.easing = nil;
    tween.key = nil;
    tween.elapsed = nil;
    tween.duration = nil;
    A.pool[#A.pool + 1] = tween;
end

local function Detach(tween)
    local byKey = A.lookup[tween.target];
    if ( byKey and byKey[tween.key] == tween ) then
        byKey[tween.key] = nil;
        if ( not next(byKey) ) then
            A.lookup[tween.target] = nil;
        end
    end
    for index = #A.active, 1, -1 do
        if ( A.active[index] == tween ) then
            table.remove(A.active, index);
            break;
        end
    end
end

-- ---------------------------------------------------------------- driver
-- Created lazily and only in a real client. In tests it stays nil and the caller
-- drives Update() manually, which is exactly what makes this testable.
function A.EnsureDriver()
    if ( A.driver ) then
        return A.driver;
    end
    if ( type(CreateFrame) ~= "function" ) then
        return nil;
    end
    -- Deliberately NOT parented to the character-select screen, unlike the visible
    -- chrome (see ECS_UI.PreferredParent). A hidden parent stops OnUpdate, and a
    -- tween interrupted by a screen switch would then never advance - leaving the
    -- driver shown, this flag set and the tween's onDone callback (which the
    -- deletion path uses to restore the roster) unfired. Parentless, the driver
    -- always runs a tween to completion and hides itself afterwards. It is
    -- invisible and takes no mouse input, so it cannot leak across screens the way
    -- a search box parented to UIParent could.
    local ok, frame = pcall(CreateFrame, "Frame", "ECSAnimDriver");
    if ( not ok or not frame ) then
        return nil;
    end
    frame:Hide();
    frame:SetScript("OnUpdate", function(_, elapsed)
        A.Update(elapsed);
    end);
    A.driver = frame;
    return frame;
end

local function SyncDriver()
    local driver = A.driver;
    if ( not driver ) then
        return;
    end
    if ( #A.active > 0 ) then
        if ( not driver:IsShown() ) then
            driver:Show();
        end
    elseif ( driver:IsShown() ) then
        driver:Hide();   -- stops OnUpdate entirely: zero idle cost
    end
end

-- ---------------------------------------------------------------- core
-- Start (or replace) a tween on one (target,key) pair. Replacing rather than
-- stacking is what keeps a fast hover-in/out from fighting itself.
--
-- spec: { key, setter, from, to, duration, easing, onDone, onUpdate }
function A.Run(target, spec)
    if ( not target or type(spec) ~= "table" or type(spec.setter) ~= "function" ) then
        return nil;
    end

    local key = spec.key or "value";
    local duration = spec.duration or C.FADE_DURATION;
    if ( type(duration) ~= "number" or duration < 0 ) then
        duration = C.FADE_DURATION;
    end

    A.Cancel(target, key);

    local tween = Acquire();
    tween.target   = target;
    tween.key      = key;
    tween.setter   = spec.setter;
    tween.from     = spec.from or 0;
    tween.to       = spec.to or 0;
    tween.elapsed  = 0;
    tween.duration = duration;
    tween.easing   = spec.easing or "quadOut";
    tween.onDone   = spec.onDone;
    tween.onUpdate = spec.onUpdate;

    A.active[#A.active + 1] = tween;
    local byKey = A.lookup[target];
    if ( not byKey ) then
        byKey = {};
        A.lookup[target] = byKey;
    end
    byKey[key] = tween;

    -- zero-duration tweens settle immediately rather than waiting a frame
    if ( duration <= C.ANIM_EPSILON ) then
        tween.setter(target, tween.to);
        Detach(tween);
        Release(tween);
        if ( spec.onDone ) then
            pcall(spec.onDone, target);
        end
        return nil;
    end

    A.EnsureDriver();
    SyncDriver();
    return tween;
end

-- Advance every live tween. Returns the number still active.
function A.Update(elapsed)
    if ( type(elapsed) ~= "number" or elapsed ~= elapsed ) then
        elapsed = 0;
    end
    -- clamp so a long hitch (loading screen, alt-tab) cannot teleport a tween
    if ( elapsed > C.ANIM_MAX_DT ) then
        elapsed = C.ANIM_MAX_DT;
    end
    if ( elapsed < 0 ) then
        elapsed = 0;
    end

    local finished = nil;
    for index = 1, #A.active do
        local tween = A.active[index];
        if ( tween ) then
            tween.elapsed = tween.elapsed + elapsed;

            local progress = 1;
            if ( tween.duration > 0 ) then
                progress = tween.elapsed / tween.duration;
                if ( progress > 1 ) then progress = 1; end
                if ( progress < 0 ) then progress = 0; end
            end

            local eased = A.Ease(tween.easing, progress);
            local value = tween.from + (tween.to - tween.from) * eased;

            if ( tween.setter ) then
                pcall(tween.setter, tween.target, value);
            end
            if ( tween.onUpdate ) then
                pcall(tween.onUpdate, tween.target, value, progress);
            end

            if ( progress >= 1 ) then
                finished = finished or {};
                finished[#finished + 1] = tween;
            end
        end
    end

    if ( finished ) then
        for index = 1, #finished do
            local tween = finished[index];
            -- snapshot before detach: Detach mutates the lookup tables
            local target, onDone = tween.target, tween.onDone;
            Detach(tween);
            Release(tween);
            if ( onDone ) then
                pcall(onDone, target);
            end
        end
    end

    SyncDriver();
    return #A.active;
end

-- Stop a tween WITHOUT firing onDone (used when a new tween replaces it).
function A.Cancel(target, key)
    local byKey = A.lookup[target];
    if ( not byKey ) then
        return false;
    end
    local tween = byKey[key];
    if ( not tween ) then
        return false;
    end
    Detach(tween);
    Release(tween);
    SyncDriver();
    return true;
end

function A.CancelAll(target)
    local byKey = A.lookup[target];
    if ( not byKey ) then
        return false;
    end
    local keys = {};
    for key in pairs(byKey) do
        keys[#keys + 1] = key;
    end
    for index = 1, #keys do
        A.Cancel(target, keys[index]);
    end
    return true;
end

function A.IsRunning(target, key)
    local byKey = A.lookup[target];
    if ( not byKey ) then
        return false;
    end
    if ( key ) then
        return byKey[key] ~= nil;
    end
    return next(byKey) ~= nil;
end

function A.ActiveCount()
    return #A.active;
end

-- Test/reset hook: drop every tween without firing callbacks.
function A.Reset()
    for index = #A.active, 1, -1 do
        local tween = A.active[index];
        A.active[index] = nil;
        Release(tween);
    end
    A.active = {};
    A.lookup = {};
    SyncDriver();
end

-- ---------------------------------------------------------------- conveniences
-- These only build a spec; they never touch a frame directly, so they are safe to
-- reference in tests and remain the single place animation timings are chosen.
function A.Fade(target, to, from, duration, onDone)
    return A.Run(target, {
        key      = "alpha",
        setter   = function(t, value) if ( t.SetAlpha ) then t:SetAlpha(value); end end,
        from     = from,
        to       = to,
        duration = duration or C.FADE_DURATION,
        easing   = "quadOut",
        onDone   = onDone,
    });
end

function A.Scale(target, to, from, duration, onDone)
    return A.Run(target, {
        key      = "scale",
        setter   = function(t, value)
            if ( t.SetECSScale ) then t:SetECSScale(value); end
        end,
        from     = from,
        to       = to,
        duration = duration or C.SELECTION_DURATION,
        easing   = "backOut",
        onDone   = onDone,
    });
end
