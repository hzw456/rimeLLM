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

return M
