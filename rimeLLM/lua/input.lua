local InputCapturer = {}
local InputCapturer_mt = { __index = InputCapturer }

local utils = require("utils")

function InputCapturer.new(config_manager)
    local self = setmetatable({}, InputCapturer_mt)
    self.config = config_manager
    self.composition_text = ""
    self.committed_text = ""
    self.surrounding_text = ""
    self.cursor_position = 0
    self.selection_start = 0
    self.selection_end = 0
    self.input_mode = "zh"
    self.context_buffer = {}
    self.max_buffer_size = 5
    self.composition_start_time = 0
    self.is_composing = false
    self.last_commit_time = 0
    self.current_schema = ""
    return self
end

function InputCapturer:init()
    self.max_buffer_size = self.config:get("performance.max_buffer_size", 5)
    utils.info("InputCapturer initialized")
end

function InputCapturer:reset()
    self.composition_text = ""
    self.cursor_position = 0
    self.selection_start = 0
    self.selection_end = 0
    self.is_composing = false
    utils.debug("InputCapturer reset")
end

function InputCapturer:on_key_event(key, event_type)
    local key_name = key.keycode or key.key or ""
    local modifier = key.shift and "Shift" or "" .. (key.ctrl and "Ctrl" or "")
    
    if event_type == "press" then
        utils.debug("Key pressed: " .. key_name .. " (modifiers: " .. modifier .. ")")
    end
end

function InputCapturer:on_composition_start(ctx)
    self.is_composing = true
    self.composition_start_time = utils.get_time_ms()
    self.composition_text = ""
    utils.debug("Composition started")
end

function InputCapturer:on_composition_update(ctx)
    if ctx and ctx.preedit then
        self.composition_text = ctx.preedit.text or ""
        self.cursor_position = ctx.preedit.cursor or 0
        if ctx.preedit.sel_start and ctx.preedit.sel_end then
            self.selection_start = ctx.preedit.sel_start
            self.selection_end = ctx.preedit.sel_end
        end
    end
    utils.debug("Composition update: " .. self.composition_text)
end

function InputCapturer:on_composition_end(ctx)
    if ctx and ctx.committed_text then
        self.committed_text = ctx.committed_text
        self:on_text_committed(self.committed_text)
    end
    
    local current_text = self.composition_text
    self:reset()
    self.last_commit_time = utils.get_time_ms()
    
    return current_text
end

function InputCapturer:on_text_committed(text)
    if not text or text == "" then
        return
    end
    
    utils.info("Text committed: " .. string.sub(text, 1, 50) .. "...")
    
    local context = self:_create_context(text)
    table.insert(self.context_buffer, context)
    
    while #self.context_buffer > self.max_buffer_size do
        table.remove(self.context_buffer, 1)
    end
    
    self:_notify_listeners("commit", context)
end

function InputCapturer:on_context_update(ctx)
    if ctx then
        if ctx.sentence then
            self.surrounding_text = ctx.sentence.text or ""
        end
        if ctx.cursor then
            self.cursor_position = ctx.cursor
        end
    end
end

function InputCapturer:on_schema_change(schema_id)
    self.current_schema = schema_id or ""
    utils.info("Schema changed to: " .. self.current_schema)
    self:detect_input_mode()
end

function InputCapturer:detect_input_mode()
    local schema = self.current_schema
    if schema == "" then
        return "unknown"
    end
    
    if schema:find("pinyin") or schema:find("shuangpin") then
        self.input_mode = "zh"
    elseif schema:find("wubi") or schema:find("cangjie") then
        self.input_mode = "zh"
    elseif schema:find("en") or schema:find("english") then
        self.input_mode = "en"
    else
        self.input_mode = "zh"
    end
    
    utils.debug("Input mode detected: " .. self.input_mode)
    return self.input_mode
end

function InputCapturer:_create_context(committed)
    local context = {
        raw_input = self.composition_text,
        composed_text = committed,
        cursor_position = self.cursor_position,
        selection_start = self.selection_start,
        selection_end = self.selection_end,
        input_mode = self.input_mode,
        surrounding_text = self.surrounding_text,
        timestamp = utils.get_time_ms(),
        schema = self.current_schema,
        buffer = self:_get_buffer_text()
    }
    return context
end

function InputCapturer:_get_buffer_text()
    local texts = {}
    for _, ctx in ipairs(self.context_buffer) do
        table.insert(texts, ctx.composed_text)
    end
    return table.concat(texts, " ")
end

function InputCapturer:_notify_listeners(event_type, context)
    for _, listener in ipairs(self.listeners or {}) do
        if listener[event_type] then
            pcall(listener[event_type], context)
        end
    end
end

function InputCapturer:add_listener(listener)
    if not self.listeners then
        self.listeners = {}
    end
    table.insert(self.listeners, listener)
end

function InputCapturer:get_latest_context()
    if #self.context_buffer > 0 then
        return self.context_buffer[#self.context_buffer]
    end
    return nil
end

function InputCapturer:get_recent_contexts(count)
    count = count or 3
    local result = {}
    local start = math.max(1, #self.context_buffer - count + 1)
    for i = start, #self.context_buffer do
        table.insert(result, self.context_buffer[i])
    end
    return result
end

function InputCapturer:get_composition()
    return {
        text = self.composition_text,
        cursor = self.cursor_position,
        is_composing = self.is_composing
    }
end

function InputCapturer:get_buffer_text(max_chars)
    max_chars = max_chars or self.config:get("performance.max_input_chars", 100)
    local buffer = self:_get_buffer_text()
    if #buffer > max_chars then
        return string.sub(buffer, -max_chars)
    end
    return buffer
end

function InputCapturer:should_trigger_ai(ctx)
    if not self.config:is_enabled() then
        return false, "disabled"
    end
    
    if not ctx or not ctx.composed_text or ctx.composed_text == "" then
        return false, "empty"
    end
    
    local max_chars = self.config:get("performance.max_input_chars", 100)
    if #ctx.composed_text > max_chars then
        return false, "too_long"
    end
    
    local min_chars = 3
    if #ctx.composed_text < min_chars then
        return false, "too_short"
    end
    
    return true, "ready"
end

function InputCapturer:clear_buffer()
    self.context_buffer = {}
    utils.info("Context buffer cleared")
end

return InputCapturer
