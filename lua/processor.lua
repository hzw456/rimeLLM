local TextProcessor = {}
local TextProcessor_mt = { __index = TextProcessor }

local utils = require("utils")

function TextProcessor.new(config_manager, ai_client)
    local self = setmetatable({}, TextProcessor_mt)
    self.config = config_manager
    self.ai_client = ai_client
    self.pending_requests = {}
    self.debounce_timers = {}
    return self
end

function TextProcessor:init()
    utils.info("TextProcessor initialized")
end

function TextProcessor:process_text(context, feature, callback)
    if not context or not context.composed_text then
        if callback then
            callback({ success = false, error = "Invalid context" })
        end
        return
    end
    
    local text = context.composed_text
    local should_process, reason = self:_should_process(text, feature)
    
    if not should_process then
        utils.debug("Skipping processing: " .. reason)
        if callback then
            callback({ success = false, error = reason })
        end
        return
    end
    
    local prompt = self:_build_prompt(text, feature, context)
    
    self.ai_client:chat(nil, prompt, function(response)
        if response.success then
            local suggestion = self:_parse_suggestion(response.response, feature)
            if callback then
                callback({ success = true, suggestion = suggestion, original = text })
            end
        else
            if callback then
                callback({ success = false, error = response.error })
            end
        end
    end)
end

function TextProcessor:correct(text, callback)
    self:process_text({ composed_text = text }, "correction", callback)
end

function TextProcessor:translate(text, source_lang, target_lang, callback)
    local context = {
        composed_text = text,
        source_lang = source_lang or "auto",
        target_lang = target_lang or "en"
    }
    self:process_text(context, "translation", callback)
end

function TextProcessor:expand(text, ratio, callback)
    local context = {
        composed_text = text,
        expansion_ratio = ratio or 2.0
    }
    self:process_text(context, "expansion", callback)
end

function TextProcessor:_should_process(text, feature)
    if not self.config:is_feature_enabled(feature) then
        return false, "feature_disabled"
    end
    
    local min_length = 10
    if #text <= min_length then
        return false, "too_short"
    end
    
    local max_length = self.config:get("performance.max_input_chars", 100)
    if #text > max_length then
        return false, "too_long"
    end
    
    return true, "ready"
end

function TextProcessor:_build_prompt(text, feature, context)
    local prompts = {
        correction = string.format([[You are a Chinese text corrector. Correct any spelling, grammar, or typing errors in the following text. Keep the correction minimal and only fix obvious errors. Return ONLY the corrected text, no explanation.

Text: %s
Corrected:]], text),
        
        translation = string.format([[Translate the following text from %s to %s. Keep the translation natural and accurate. Return ONLY the translated text, no explanation.

Text: %s
Translation:]], 
            context.source_lang or "auto", 
            context.target_lang or "en", 
            text),
        
        expansion = string.format([[Expand the following text to make it more detailed and comprehensive. Keep the same meaning and style. Target length: ~%dx original. Return ONLY the expanded text, no explanation.

Text: %s
Expanded:]], 
            context.expansion_ratio or 2, 
            text)
    }
    
    return prompts[feature] or prompts.correction
end

function TextProcessor:_parse_suggestion(response, feature)
    if not response or response == "" then
        return nil
    end
    
    local text = utils.trim(response)
    
    text = text:gsub("^Corrected:%s*", "")
    text = text:gsub("^Translation:%s*", "")
    text = text:gsub("^Expanded:%s*", "")
    
    text = text:gsub("^[\"']", "")
    text = text:gsub("[\"']$", "")
    
    return text
end

function TextProcessor:cancel_pending_requests()
    for id, _ in pairs(self.pending_requests) do
        self.pending_requests[id] = nil
    end
    utils.debug("Pending requests cancelled")
end

function TextProcessor:get_pending_count()
    local count = 0
    for _, _ in pairs(self.pending_requests) do
        count = count + 1
    end
    return count
end

return TextProcessor
