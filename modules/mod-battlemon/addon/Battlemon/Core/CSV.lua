Battlemon = Battlemon or {}

-- WoW cannot read files from disk. CSV text is embedded in Data/*CSV.lua as
-- numbered parts (see tools/export_addon_data.py) and parsed here.

local sub, find, concat, insert = string.sub, string.find, table.concat, table.insert

-- Splits one CSV line. Scans with string.find instead of walking characters so
-- a 300k payload does not turn into 300k string concatenations.
local function parseLine(line)
    local fields = {}
    local pos = 1
    local len = string.len(line)
    while true do
        if sub(line, pos, pos) == '"' then
            local buf = {}
            local i = pos + 1
            while true do
                local q = find(line, '"', i, true)
                if not q then
                    insert(buf, sub(line, i))
                    i = len + 1
                    break
                end
                if sub(line, q + 1, q + 1) == '"' then
                    insert(buf, sub(line, i, q))
                    i = q + 2
                else
                    insert(buf, sub(line, i, q - 1))
                    i = q + 1
                    break
                end
            end
            insert(fields, concat(buf))
            local comma = find(line, ",", i, true)
            if not comma then
                break
            end
            pos = comma + 1
        else
            local comma = find(line, ",", pos, true)
            if not comma then
                insert(fields, sub(line, pos))
                break
            end
            insert(fields, sub(line, pos, comma - 1))
            pos = comma + 1
        end
        if pos > len + 1 then
            break
        end
    end
    return fields
end

-- Accepts either a string or the numbered parts table emitted by the exporter.
local function payloadText(text)
    if type(text) == "table" then
        return concat(text)
    end
    return text
end

function Battlemon.ParseCSV(text)
    text = payloadText(text)
    if type(text) ~= "string" or text == "" then
        return {}
    end
    if find(text, "\r", 1, true) then
        text = string.gsub(text, "\r\n?", "\n")
    end
    local rows = {}
    local header
    for line in string.gmatch(text, "([^\n]+)") do
        local fields = parseLine(line)
        if not header then
            header = fields
        else
            local row = {}
            for i = 1, #header do
                local value = fields[i] or ""
                local num = tonumber(value)
                if num ~= nil and value ~= "" then
                    row[header[i]] = num
                else
                    row[header[i]] = value
                end
            end
            insert(rows, row)
        end
    end
    return rows
end
