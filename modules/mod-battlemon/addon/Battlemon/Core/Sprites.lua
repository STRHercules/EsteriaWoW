Battlemon = Battlemon or {}

-- Both the classic and arena presentations share this exact 3D appearance catalog.
-- Keep the texture region as the layout/visibility anchor for existing UI controls.
function Battlemon.ShinyFolder(folder)
    return folder
end

function Battlemon.SetPokemonTexture(texture, folder, sprite, shiny)
    if not texture then return false end
    local choices = Battlemon.Models and Battlemon.Models[sprite or ""]
    local path = choices and choices[shiny and 1 or 0]
    texture:SetTexture(nil)
    if not path then
        if texture.battlemonModel then texture.battlemonModel:Hide() end
        texture.battlemonModelPath = nil
        return false
    end
    local model = texture.battlemonModel
    if not model then
        model = CreateFrame("PlayerModel", nil, texture:GetParent())
        model:SetAllPoints(texture)
        model:EnableMouse(false)
        texture.battlemonModel = model
        -- Texture regions have no OnHide script. These hooks prevent stale models
        -- in empty party slots and reused scrolling rows.
        hooksecurefunc(texture, "Hide", function() model:Hide() end)
        hooksecurefunc(texture, "Show", function()
            if texture.battlemonModelPath then model:Show() end
        end)
        hooksecurefunc(texture, "SetAlpha", function(_, alpha) model:SetAlpha(alpha) end)
    end
    if texture.battlemonModelPath ~= path then
        model:SetModel(path)
        model:SetModelScale(1)
        model:SetPosition(0, 0, 0)
        model:SetSequence(0)
        texture.battlemonModelPath = path
    end
    model:SetPosition(0, 0, texture.battlemonPreviewZ or 0)
    model:SetFacing(folder == "Back" and math.pi or 0.4)
    model:SetAlpha(texture:GetAlpha())
    if texture:IsShown() then model:Show() else model:Hide() end
    return true
end

function Battlemon.SetBattlerTextures(playerTex, enemyTex, player, enemy)
    if playerTex and player then
        Battlemon.SetPokemonTexture(playerTex, "Back", player.sprite, player.shiny)
    end
    if enemyTex and enemy then
        Battlemon.SetPokemonTexture(enemyTex, "Front", enemy.sprite, enemy.shiny)
    end
end
