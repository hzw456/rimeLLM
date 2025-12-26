local rimeLLM = {}

local M = {}

function M.log(level, message)
    local prefix = {
        ["DEBUG"] = "[rimeLLM DEBUG]",
        ["INFO"] = "[rimeLLM INFO]",
        ["WARN"] = "[rimeLLM WARN]",
        ["ERROR"] = "[rimeLLM ERROR]"
    }
    rime.api:log(prefix[level] .. " " .. message)
end

function M.debug(message)
    M.log("DEBUG", message)
end

function M.info(message)
    M.log("INFO", message)
end

function M.warn(message)
    M.log("WARN", message)
end

function M.error(message)
    M.log("ERROR", message)
end

function M.split(s, delimiter)
    local result = {}
    if s == nil or s == "" then
        return result
    end
    local start = 1
    local delim_start, delim_end = string.find(s, delimiter, start)
    while delim_start do
        table.insert(result, string.sub(s, start, delim_start - 1))
        start = delim_end + 1
        delim_start, delim_end = string.find(s, delimiter, start)
    end
    table.insert(result, string.sub(s, start))
    return result
end

function M.trim(s)
    if s == nil then
        return nil
    end
    return string.gsub(s, "^%s*(.-)%s*$", "%1")
end

function M.startswith(s, prefix)
    if s == nil or prefix == nil then
        return false
    end
    return string.sub(s, 1, string.len(prefix)) == prefix
end

function M.endswith(s, suffix)
    if s == nil or suffix == nil then
        return false
    end
    return string.sub(s, -string.len(suffix)) == suffix
end

function M.table_merge(t1, t2)
    local result = {}
    if t1 then
        for k, v in pairs(t1) do
            result[k] = v
        end
    end
    if t2 then
        for k, v in pairs(t2) do
            result[k] = v
        end
    end
    return result
end

function M.deep_copy(obj)
    if type(obj) ~= "table" then
        return obj
    end
    local res = {}
    for k, v in pairs(obj) do
        res[k] = M.deep_copy(v)
    end
    return res
end

function M.get_time_ms()
    return math.floor(rime.get_time() * 1000)
end

function M.json_encode(obj)
    if obj == nil then
        return nil
    end

    local function encode(val)
        if type(val) == "nil" then
            return "null"
        elseif type(val) == "number" then
            return tostring(val)
        elseif type(val) == "string" then
            local escaped = val:gsub("\\", "\\\\")
            escaped = escaped:gsub("\"", "\\\"")
            escaped = escaped:gsub("\n", "\\n")
            escaped = escaped:gsub("\r", "\\r")
            escaped = escaped:gsub("\t", "\\t")
            return "\"" .. escaped .. "\""
        elseif type(val) == "boolean" then
            return val and "true" or "false"
        elseif type(val) == "table" then
            local is_array = true
            local count = 0
            for k, v in pairs(val) do
                if type(k) ~= "number" or k <= 0 or k ~= math.floor(k) then
                    is_array = false
                    break
                end
                count = count + 1
            end

            local parts = {}
            if is_array then
                for i = 1, count do
                    table.insert(parts, encode(val[i]))
                end
                return "[" .. table.concat(parts, ",") .. "]"
            else
                for k, v in pairs(val) do
                    table.insert(parts, encode(k) .. ":" .. encode(v))
                end
                return "{" .. table.concat(parts, ",") .. "}"
            end
        else
            return "null"
        end
    end

    return encode(obj)
end

function M.json_decode(str)
    if not str or str == "" then
        return nil
    end

    local function skip_spaces(s, i)
        while i <= #s and string.match(s, "%s", i) do
            i = i + 1
        end
        return i
    end

    local function parse_value(s, i)
        i = skip_spaces(s, i)
        if i > #s then
            return nil, i
        end

        local c = string.sub(s, i, i)

        if c == "{" then
            local obj = {}
            i = i + 1
            while i <= #s do
                i = skip_spaces(s, i)
                if string.sub(s, i, i) == "}" then
                    i = i + 1
                    return obj, i
                end

                local key, new_i = parse_value(s, i)
                if not key then
                    return nil, i
                end
                i = new_i
                i = skip_spaces(s, i)
                if string.sub(s, i, i) ~= ":" then
                    return nil, i
                end
                i = i + 1
                local value, new_i = parse_value(s, i)
                if value == nil then
                    return nil, i
                end
                obj[key] = value
                i = new_i
                i = skip_spaces(s, i)
                if string.sub(s, i, i) == "," then
                    i = i + 1
                end
            end
            return nil, i
        elseif c == "[" then
            local arr = {}
            i = i + 1
            while i <= #s do
                i = skip_spaces(s, i)
                if string.sub(s, i, i) == "]" then
                    i = i + 1
                    return arr, i
                end
                local value, new_i = parse_value(s, i)
                if value == nil then
                    return nil, i
                end
                table.insert(arr, value)
                i = new_i
                i = skip_spaces(s, i)
                if string.sub(s, i, i) == "," then
                    i = i + 1
                end
            end
            return nil, i
        elseif c == "\"" then
            local j = i + 1
            local result = ""
            while j <= #s do
                local ch = string.sub(s, j, j)
                if ch == "\\" and j < #s then
                    local next_ch = string.sub(s, j + 1, j + 1)
                    if next_ch == "n" then
                        result = result .. "\n"
                    elseif next_ch == "r" then
                        result = result .. "\r"
                    elseif next_ch == "t" then
                        result = result .. "\t"
                    elseif next_ch == "\\\"" then
                        result = result .. "\""
                    elseif next_ch == "\\" then
                        result = result .. "\\"
                    else
                        result = result .. next_ch
                    end
                    j = j + 2
                elseif ch == "\"" then
                    break
                else
                    result = result .. ch
                    j = j + 1
                end
            end
            return result, j + 1
        elseif c == "t" and string.sub(s, i, i + 3) == "true" then
            return true, i + 4
        elseif c == "f" and string.sub(s, i, i + 4) == "false" then
            return false, i + 5
        elseif c == "n" and string.sub(s, i, i + 3) == "null" then
            return nil, i + 4
        else
            local j = i
            while j <= #s and string.match(s, "[%d%.%-]") do
                j = j + 1
            end
            local num_str = string.sub(s, i, j - 1)
            if num_str and num_str ~= "" then
                local num = tonumber(num_str)
                if num then
                    return num, j
                end
            end
            return nil, i
        end
    end

    local result, pos = parse_value(str, 1)
    return result
end

return M
