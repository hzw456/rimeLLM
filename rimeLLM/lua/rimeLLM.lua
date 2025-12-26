local rimeLLM = {}

local config_manager = nil
local ai_client = nil
local input_capturer = nil
local text_processor = nil
local suggestion_display = nil
local initialized = false
local enabled = false
local last_trigger_time = 0
local DEBOUNCE_MS = 300

function rimeLLM.init()
    if initialized then
        return
    end
    
    local utils = require("utils")
    utils.info("Initializing rimeLLM...")
    
    config_manager = require("config").new()
    local config_path = nil
    if rime and rime.get_user_data_dir then
        config_path = rime.get_user_data_dir() .. "/rimeLLM.yaml"
    end
    config_manager:load(config_path)
    
    enabled = config_manager:is_enabled()
    if not enabled then
        utils.info("rimeLLM is disabled")
        return
    end
    
    DEBOUNCE_MS = config_manager:get("performance.debounce_ms", 300)
    
    ai_client = require("ai_client").new(config_manager)
    ai_client:init()
    
    input_capturer = require("input").new(config_manager)
    input_capturer:init()
    input_capturer:add_listener({
        commit = function(context)
            rimeLLM:on_text_committed(context)
        end
    })
    
    text_processor = require("processor").new(config_manager, ai_client)
    text_processor:init()
    
    suggestion_display = require("display").new(config_manager)
    suggestion_display:init()
    
    initialized = true
    utils.info("rimeLLM initialized successfully")
end

function rimeLLM.on_key_event(key, event_type)
    if not enabled or not initialized then
        return
    end
    
    local utils = require("utils")
    
    if event_type == "press" then
        local key_name = key.keycode or key.key or ""
        local accept_key = config_manager:get("key_bindings.accept", "Tab")
        local reject_key = config_manager:get("key_bindings.reject", "Escape")
        local trigger_key = config_manager:get("key_bindings.trigger", "Ctrl+Shift+a")
        
        if key_name == accept_key then
            if suggestion_display:is_visible_p() then
                local suggestion = suggestion_display:accept_first()
                if suggestion then
                    rimeLLM:insert_text(suggestion.text)
                end
                return true
            end
        elseif key_name == reject_key then
            if suggestion_display:is_visible_p() then
                suggestion_display:reject()
                return true
            end
        elseif key_name == trigger_key then
            local context = input_capturer:get_latest_context()
            if context then
                local should_trigger, reason = input_capturer:should_trigger_ai(context)
                if should_trigger then
                    rimeLLM:trigger_ai_processing(context)
                end
            end
            return true
        end
    end
    
    input_capturer:on_key_event(key, event_type)
    
    return false
end

function rimeLLM.on_composition_start(ctx)
    if not enabled or not initialized then
        return
    end
    input_capturer:on_composition_start(ctx)
end

function rimeLLM.on_composition_update(ctx)
    if not enabled or not initialized then
        return
    end
    input_capturer:on_composition_update(ctx)
end

function rimeLLM.on_composition_end(ctx)
    if not enabled or not initialized then
        return ""
    end
    local committed = input_capturer:on_composition_end(ctx)
    return committed
end

function rimeLLM.on_text_committed(context)
    if not enabled or not initialized then
        return
    end
    
    local should_trigger, reason = input_capturer:should_trigger_ai(context)
    if not should_trigger then
        return
    end
    
    local now = require("utils").get_time_ms()
    if now - last_trigger_time < DEBOUNCE_MS then
        return
    end
    last_trigger_time = now
    
    rimeLLM:trigger_ai_processing(context)
end

function rimeLLM.on_context_update(ctx)
    if not enabled or not initialized then
        return
    end
    input_capturer:on_context_update(ctx)
end

function rimeLLM.on_schema_change(schema_id)
    if not enabled or not initialized then
        return
    end
    input_capturer:on_schema_change(schema_id)
end

function rimeLLM.trigger_ai_processing(context)
    local utils = require("utils")
    utils.debug("Triggering AI processing for: " .. string.sub(context.composed_text, 1, 30) .. "...")
    
    local features = {}
    if config_manager:is_feature_enabled("correction") then
        table.insert(features, "correction")
    end
    if config_manager:is_feature_enabled("translation") then
        table.insert(features, "translation")
    end
    if config_manager:is_feature_enabled("expansion") then
        table.insert(features, "expansion")
    end
    
    if #features == 0 then
        utils.debug("No features enabled")
        return
    end
    
    local first_feature = features[1]
    
    text_processor:process_text(context, first_feature, function(result)
        if result.success and result.suggestion then
            suggestion_display:show_suggestions({ result.suggestion }, first_feature)
        else
            utils.debug("Processing failed: " .. tostring(result.error))
        end
    end)
end

function rimeLLM.insert_text(text)
    if rime and rime.api and rime.api.commit then
        rime.api:commit(text)
    end
end

function rimeLLM.on_candidate_select(index)
    if not enabled or not initialized then
        return
    end
    
    if suggestion_display:is_visible_p() then
        local suggestion = suggestion_display:accept_suggestion(index)
        if suggestion then
            rimeLLM:insert_text(suggestion.text)
        end
    end
end

function rimeLLM.reload()
    if config_manager then
        config_manager:reload()
        enabled = config_manager:is_enabled()
        
        if suggestion_display then
            suggestion_display:refresh()
        end
        
        local utils = require("utils")
        utils.info("rimeLLM reloaded, enabled: " .. tostring(enabled))
    end
end

function rimeLLM.shutdown()
    local utils = require("utils")
    utils.info("Shutting down rimeLLM...")
    
    if suggestion_display then
        suggestion_display:clear()
    end
    
    if text_processor then
        text_processor:cancel_pending_requests()
    end
    
    initialized = false
    enabled = false
    utils.info("rimeLLM shutdown complete")
end

function rimeLLM.get_version()
    return "1.0.0"
end

function rimeLLM.is_enabled()
    return enabled and initialized
end

function rimeLLM.get_status()
    return {
        version = rimeLLM.get_version(),
        enabled = rimeLLM.is_enabled(),
        initialized = initialized,
        provider = config_manager and config_manager:get_provider() or "unknown",
        display_mode = config_manager and config_manager:get_display_mode() or "unknown"
    }
end

return rimeLLM
