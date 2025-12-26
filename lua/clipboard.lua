local Clipboard = {}
local Clipboard_mt = { __index = Clipboard }

local utils = require("utils")

function Clipboard.new(config_manager)
    local self = setmetatable({}, Clipboard_mt)
    self.config = config_manager
    self.last_clipboard = nil
    self.last_update_time = 0
    return self
end

function Clipboard:init()
    utils.info("Clipboard module initialized")
end

function Clipboard:get_clipboard()
    local max_length = self.config:get("clipboard.max_length", 1000)
    local content = nil
    
    if rime and rime.get_clipboard then
        content = rime.get_clipboard()
    else
        utils.debug("Clipboard API not available")
        return nil
    end
    
    if not content or content == "" then
        utils.debug("Clipboard is empty")
        return nil
    end
    
    content = utils.trim(content)
    
    if #content > max_length then
        content = string.sub(content, 1, max_length)
        utils.debug("Clipboard content truncated to " .. tostring(max_length) .. " chars")
    end
    
    self.last_clipboard = content
    self.last_update_time = utils.get_time_ms()
    
    utils.debug("Clipboard fetched: " .. string.sub(content, 1, 50) .. "...")
    return content
end

function Clipboard:get_cached()
    if self.last_clipboard and self.last_clipboard ~= "" then
        local max_age = self.config:get("clipboard.cache_ms", 5000)
        local now = utils.get_time_ms()
        if now - self.last_update_time < max_age then
            return self.last_clipboard
        end
    end
    return nil
end

function Clipboard:clear_cache()
    self.last_clipboard = nil
    self.last_update_time = 0
    utils.debug("Clipboard cache cleared")
end

function Clipboard:is_available()
    if rime and rime.get_clipboard then
        return true
    end
    return false
end

function Clipboard:set_clipboard(text)
    if rime and rime.set_clipboard then
        rime.set_clipboard(text)
        utils.debug("Clipboard set: " .. string.sub(text, 1, 30) .. "...")
    else
        utils.debug("set_clipboard API not available")
    end
end

return Clipboard
