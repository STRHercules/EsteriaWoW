-- Esteria style kit (wowdecomp)
-- The creator's look in one place: palette, font and the solid/text/border helpers drawn from WHITE8X8. Shared by
-- the creator skin, the Body page and the in-game Esteria UI, so glue and game stay identical. A global table, not
-- locals: the creator chunk is near Lua's 200-locals-per-function limit.
EsteriaStyle = EsteriaStyle or {};
do
    local ES = EsteriaStyle;
    ES.GOLD = { 0.91, 0.77, 0.42 };
    ES.GOLD_DIM = { 0.54, 0.43, 0.18 };
    ES.INK = { 0.03, 0.04, 0.055 };
    ES.TEXT = { 0.88, 0.86, 0.80 };
    ES.MUTED = { 0.60, 0.59, 0.55 };
    ES.GOOD = { 0.55, 0.85, 0.50 };
    ES.BAD = { 0.95, 0.42, 0.36 };
    ES.FONT = "Fonts\\FRIZQT__.TTF";
    ES.WHITE = "Interface\\Buttons\\WHITE8X8";

    function ES.Solid(parent, layer, color, a)
        local tex = parent:CreateTexture(nil, layer or "ARTWORK");
        tex:SetTexture(ES.WHITE);
        tex:SetVertexColor(color[1], color[2], color[3], a or 1);
        return tex;
    end

    function ES.Text(parent, size, color, layer, font)
        -- Glue and the game name their font templates differently; checked per call so load order can't matter.
        local template = GlueFontHighlightSmall and "GlueFontHighlightSmall" or "GameFontHighlightSmall";
        local fs = parent:CreateFontString(nil, layer or "OVERLAY", template);
        fs:SetFont(font or ES.FONT, size);
        fs:SetTextColor(color[1], color[2], color[3]);
        fs:SetShadowOffset(1, -1);
        fs:SetShadowColor(0, 0, 0, 0.8);
        return fs;
    end

    -- A 1px line on each side of the frame; returns the four lines for Tint.
    function ES.Border(frame, color, a)
        local lines = {};
        for _, side in ipairs({ { "TOPLEFT", "TOPRIGHT" }, { "BOTTOMLEFT", "BOTTOMRIGHT" }, { "TOPLEFT", "BOTTOMLEFT" },
                                { "TOPRIGHT", "BOTTOMRIGHT" } }) do
            local line = ES.Solid(frame, "BORDER", color, a);
            line:SetPoint(side[1], frame, side[1], 0, 0);
            line:SetPoint(side[2], frame, side[2], 0, 0);
            if side[1] == "TOPLEFT" and side[2] == "BOTTOMLEFT" or side[1] == "TOPRIGHT" then line:SetWidth(1); else line:SetHeight(1); end
            lines[#lines + 1] = line;
        end
        return lines;
    end

    function ES.Tint(lines, color, a)
        for _, line in ipairs(lines) do line:SetVertexColor(color[1], color[2], color[3], a); end
    end

    -- Cubic ease-out: fast start, soft landing.
    function ES.Ease(t) return 1 - (1 - t) ^ 3; end

    -- Tweens: apply(p) runs with p eased from 0 to 1 over `duration` seconds after `delay`. A tween started under a
    -- key that is still running replaces it. apply(0) runs at once so the start state shows during the delay.
    -- With ES.reduceMotion set, apply(1) runs at once instead.
    local tweens, driver = {}, nil;
    function ES.Tween(key, duration, delay, apply)
        if ES.reduceMotion then
            tweens[key] = nil;
            apply(1);
            return;
        end
        tweens[key] = { t = -(delay or 0), d = math.max(duration, 0.001), apply = apply };
        apply(0);
        if not driver then
            driver = CreateFrame("Frame");
            driver:SetScript("OnUpdate", function(_, elapsed)
                for k, tween in pairs(tweens) do
                    tween.t = tween.t + elapsed;
                    if tween.t >= 0 then
                        local p = math.min(1, tween.t / tween.d);
                        -- A failing tween is dropped instead of erroring every frame.
                        if not pcall(tween.apply, ES.Ease(p)) or p >= 1 then
                            if tweens[k] == tween then tweens[k] = nil; end
                        end
                    end
                end
            end);
        end
    end
end
