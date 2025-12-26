local SuggestionDisplay = {}
local SuggestionDisplay_mt = { __index = SuggestionDisplay }

local utils = require("utils")

SuggestionDisplay.DISPLAY_INLINE = "inline"
SuggestionDisplay.DISPLAY_CANDIDATE = "candidate"

function SuggestionDisplay.new(config_manager)
    local self = setmetatable({}, SuggestionDisplay_mt)
    self.config = config_manager
    self.current_suggestions = {}
    self.displayed_suggestion = nil
    self.suggestion_id = 0
    self.suggestion_queue = {}
    self.display_mode = SuggestionDisplay.DISPLAY_CANDIDATE
    self.is_visible = false
    self.pending_suggestion = nil
    return self
end

function SuggestionDisplay:init()
    self.display_mode = self.config:get_display_mode()
    utils.info("SuggestionDisplay initialized with mode: " .. self.display_mode)
end

function SuggestionDisplay:show_suggestions(suggestions, suggestion_type)
    if not suggestions or #suggestions == 0 then
        self:clear()
        return
    end
    
    self.suggestion_id = self.suggestion_id + 1
    local current_id = self.suggestion_id
    
    self.current_suggestions = {}
    for i, text in ipairs(suggestions) do
        table.insert(self.current_suggestions, {
            id = i,
            text = text,
            type = suggestion_type or "correction"
        })
    end
    
    local mode = self.config:get_display_mode()
    
    if mode == SuggestionDisplay.DISPLAY_INLINE then
        self:_show_inline()
    else
        self:_show_candidates()
    end
end

function SuggestionDisplay:_show_inline()
    if #self.current_suggestions == 0 then
        return
    end
    
    local suggestion = self.current_suggestions[1]
    self.displayed_suggestion = suggestion
    
    local inline_text = " " .. suggestion.text
    
    self:_display_inline_text(inline_text)
    self.is_visible = true
    utils.debug("Inline suggestion shown: " .. suggestion.text)
end

function SuggestionDisplay:_show_candidates()
    if #self.current_suggestions == 0 then
        return
    end
    
    local max_show = self.config:get("display.max_suggestions", 3)
    local to_show = math.min(#self.current_suggestions, max_show)
    
    local candidates = {}
    for i = 1, to_show do
        local s = self.current_suggestions[i]
        local prefix = tostring(i) .. ". "
        table.insert(candidates, {
            id = s.id,
            text = s.text,
            prefix = prefix
        })
    end
    
    self:_display_candidates(candidates)
    self.is_visible = true
    utils.debug("Candidates shown: " .. tostring(#candidates))
end

function SuggestionDisplay:_display_inline_text(text)
    if rime and rime.api and rime.api.display then
        rime.api:display({
            type = "inline",
            text = text,
            length = #text,
            highlight = true
        })
    else
        utils.debug("Cannot display inline: API not available")
    end
end

function SuggestionDisplay:_display_candidates(candidates)
    if rime and rime.api and rime.api.display then
        rime.api:display({
            type = "candidates",
            candidates = candidates,
            select_keys = "1234567890"
        })
    else
        utils.debug("Cannot display candidates: API not available")
    end
end

function SuggestionDisplay:accept_suggestion(index)
    if not self.current_suggestions or #self.current_suggestions == 0 then
        return nil
    end
    
    local idx = index or 1
    if idx < 1 or idx > #self.current_suggestions then
        return nil
    end
    
    local suggestion = self.current_suggestions[idx]
    self:clear()
    
    utils.debug("Suggestion accepted: " .. suggestion.text)
    return suggestion
end

function SuggestionDisplay:accept_first()
    return self:accept_suggestion(1)
end

function SuggestionDisplay:reject()
    self:clear()
    utils.debug("Suggestion rejected")
end

function SuggestionDisplay:clear()
    self.current_suggestions = {}
    self.displayed_suggestion = nil
    self.is_visible = false
    
    if rime and rime.api and rime.api.display then
        rime.api:display({
            type = "clear"
        })
    end
end

function SuggestionDisplay:is_visible_p()
    return self.is_visible
end

function SuggestionDisplay:get_current_suggestions()
    return self.current_suggestions
end

function SuggestionDisplay:queue_suggestion(suggestion)
    table.insert(self.suggestion_queue, suggestion)
    self:_process_queue()
end

function SuggestionDisplay:_process_queue()
    if #self.suggestion_queue == 0 then
        return
    end
    
    local latest = self.suggestion_queue[#self.suggestion_queue]
    self.suggestion_queue = {}
    
    if latest then
        self:show_suggestions({ latest.text }, latest.type)
    end
end

function SuggestionDisplay:show_transient(text)
    if not text or text == "" then
        return
    end
    
    if rime and rime.api and rime.api.tooltip then
        rime.api:tooltip({
            text = text,
            duration = 2000
        })
    else
        utils.debug("Transient text: " .. text)
    end
end

function SuggestionDisplay:update_display_mode(mode)
    if mode == SuggestionDisplay.DISPLAY_INLINE or mode == SuggestionDisplay.DISPLAY_CANDIDATE then
        self.display_mode = mode
        utils.info("Display mode changed to: " .. mode)
        if self.is_visible then
            self:show_suggestions(self.current_suggestions)
        end
    end
end

function SuggestionDisplay:get_accept_key()
    return self.config:get("key_bindings.accept", "Tab")
end

function SuggestionDisplay:get_reject_key()
    return self.config:get("key_bindings.reject", "Escape")
end

function SuggestionDisplay:refresh()
    if self.is_visible then
        self:show_suggestions(self.current_suggestions)
    end
end

return SuggestionDisplay
