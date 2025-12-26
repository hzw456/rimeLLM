local ConfigManager = {}
local ConfigManager_mt = { __index = ConfigManager }

local utils = require("utils")

function ConfigManager.new()
    local self = setmetatable({}, ConfigManager_mt)
    self.config = nil
    self.config_path = nil
    self.last_mtime = 0
    self.default_config = {
        enabled = true,
        provider = "openai",
        api_key = "",
        endpoint = "https://api.openai.com/v1",
        model = "gpt-3.5-turbo",
        max_tokens = 256,
        temperature = 0.7,
        features = {
            correction = true,
            translation = false,
            expansion = false
        },
        display = {
            mode = "candidate",
            max_suggestions = 3,
            inline_highlight_color = "gray"
        },
        key_bindings = {
            accept = "Tab",
            reject = "Escape",
            trigger = "Ctrl+Shift+a"
        },
        performance = {
            debounce_ms = 300,
            timeout_ms = 2000,
            max_input_chars = 100,
            cache_enabled = true,
            cache_max_size = 50
        },
        logging = {
            level = "INFO",
            enabled = true
        },
        clipboard = {
            enabled = true,
            trigger_pattern = "cb",
            optimize_enabled = true,
            max_length = 1000,
            cache_ms = 5000
        }
    }
    return self
end

function ConfigManager:load(config_path)
    self.config_path = config_path or self:_get_config_path()
    utils.info("Loading config from: " .. tostring(self.config_path))
    
    local file = io.open(self.config_path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        self:_parse_yaml(content)
        self:_validate_config()
        utils.info("Config loaded successfully")
        return true
    else
        utils.warn("Config file not found, using defaults")
        self.config = self.default_config
        return false
    end
end

function ConfigManager:_get_config_path()
    local user_data_dir = rime.get_user_data_dir()
    if user_data_dir then
        return user_data_dir .. "/rimeLLM.yaml"
    end
    return nil
end

function ConfigManager:_parse_yaml(content)
    local config = {}
    local current_section = nil
    local current_subsection = nil
    
    for line in string.gmatch(content, "[^\r\n]+") do
        local trimmed = utils.trim(line)
        
        if trimmed == "" or utils.startswith(trimmed, "#") then
        else
            local indent = #line - #trimmed
            local key_value = utils.split(trimmed, ":")
            
            if #key_value >= 2 then
                local key = utils.trim(key_value[1])
                local value = utils.trim(table.concat(key_value, ":", 2))
                
                if indent == 0 then
                    if value == "" or value == "true" or value == "false" then
                        current_section = key
                        if value == "" then
                            config[key] = {}
                            current_subsection = nil
                        elseif value == "true" then
                            config[key] = true
                            current_section = nil
                        elseif value == "false" then
                            config[key] = false
                            current_section = nil
                        end
                    else
                        config[key] = self:_parse_value(value)
                        current_section = nil
                        current_subsection = nil
                    end
                elseif indent == 2 and current_section then
                    if value == "" or value == "true" or value == "false" then
                        current_subsection = key
                        if value == "" then
                            config[current_section][key] = {}
                        elseif value == "true" then
                            config[current_section][key] = true
                            current_subsection = nil
                        elseif value == "false" then
                            config[current_section][key] = false
                            current_subsection = nil
                        end
                    else
                        config[current_section][key] = self:_parse_value(value)
                        current_subsection = nil
                    end
                elseif indent == 4 and current_section and current_subsection then
                    config[current_section][current_subsection][key] = self:_parse_value(value)
                end
            end
        end
    end
    
    self.config = self:_merge_with_defaults(config)
end

function ConfigManager:_parse_value(value)
    if value == "true" then
        return true
    elseif value == "false" then
        return false
    elseif tonumber(value) then
        return tonumber(value)
    else
        return value
    end
end

function ConfigManager:_merge_with_defaults(config)
    local merged = self.default_config
    
    if config then
        if config.enabled ~= nil then
            merged.enabled = config.enabled
        end
        if config.provider then merged.provider = config.provider end
        if config.api_key then merged.api_key = config.api_key end
        if config.endpoint then merged.endpoint = config.endpoint end
        if config.model then merged.model = config.model end
        if config.max_tokens then merged.max_tokens = config.max_tokens end
        if config.temperature then merged.temperature = config.temperature end
        
        if config.features then
            if config.features.correction ~= nil then
                merged.features.correction = config.features.correction
            end
            if config.features.translation ~= nil then
                merged.features.translation = config.features.translation
            end
            if config.features.expansion ~= nil then
                merged.features.expansion = config.features.expansion
            end
        end
        
        if config.display then
            if config.display.mode then merged.display.mode = config.display.mode end
            if config.display.max_suggestions then
                merged.display.max_suggestions = config.display.max_suggestions
            end
        end
        
        if config.key_bindings then
            if config.key_bindings.accept then
                merged.key_bindings.accept = config.key_bindings.accept
            end
            if config.key_bindings.reject then
                merged.key_bindings.reject = config.key_bindings.reject
            end
            if config.key_bindings.trigger then
                merged.key_bindings.trigger = config.key_bindings.trigger
            end
        end
        
        if config.performance then
            if config.performance.debounce_ms then
                merged.performance.debounce_ms = config.performance.debounce_ms
            end
            if config.performance.timeout_ms then
                merged.performance.timeout_ms = config.performance.timeout_ms
            end
            if config.performance.cache_enabled ~= nil then
                merged.performance.cache_enabled = config.performance.cache_enabled
            end
        end
        
        if config.clipboard then
            if config.clipboard.enabled ~= nil then
                merged.clipboard.enabled = config.clipboard.enabled
            end
            if config.clipboard.trigger_pattern then
                merged.clipboard.trigger_pattern = config.clipboard.trigger_pattern
            end
            if config.clipboard.optimize_enabled ~= nil then
                merged.clipboard.optimize_enabled = config.clipboard.optimize_enabled
            end
            if config.clipboard.max_length then
                merged.clipboard.max_length = config.clipboard.max_length
            end
        end
    end
    
    return merged
end

function ConfigManager:_validate_config()
    if not self.config then
        self.config = self.default_config
        return
    end
    
    if self.config.provider ~= "openai" 
       and self.config.provider ~= "anthropic" 
       and self.config.provider ~= "ollama" then
        utils.warn("Invalid provider: " .. tostring(self.config.provider) .. ", using openai")
        self.config.provider = "openai"
    end
    
    if self.config.display then
        if self.config.display.mode ~= "inline" and self.config.display.mode ~= "candidate" then
            utils.warn("Invalid display mode, using candidate")
            self.config.display.mode = "candidate"
        end
    end
end

function ConfigManager:get(key, default)
    if not self.config then
        return default
    end
    
    local keys = utils.split(key, ".")
    local value = self.config
    
    for _, k in ipairs(keys) do
        if type(value) == "table" and value[k] ~= nil then
            value = value[k]
        else
            return default
        end
    end
    
    return value
end

function ConfigManager:is_enabled()
    return self:get("enabled", false)
end

function ConfigManager:get_provider()
    return self:get("provider", "openai")
end

function ConfigManager:get_api_config()
    return {
        provider = self:get_provider(),
        api_key = self:get("api_key", ""),
        endpoint = self:get("endpoint", ""),
        model = self:get("model", ""),
        max_tokens = self:get("max_tokens", 256),
        temperature = self:get("temperature", 0.7)
    }
end

function ConfigManager:is_feature_enabled(feature)
    return self:get("features." .. feature, false)
end

function ConfigManager:get_display_mode()
    return self:get("display.mode", "candidate")
end

function ConfigManager:should_use_cache()
    return self:get("performance.cache_enabled", true)
end

function ConfigManager:reload()
    local file = io.open(self.config_path, "r")
    if file then
        local mtime = file:stat("modification")
        file:close()
        
        if mtime and mtime > self.last_mtime then
            self.last_mtime = mtime
            self:load(self.config_path)
            utils.info("Config reloaded")
            return true
        end
    end
    return false
end

function ConfigManager:create_default_config()
    local config_content = [[# rimeLLM Configuration
# Copy this file to your Rime user directory and modify as needed

rimeLLM:
  enabled: true
  
  # AI Provider: openai, anthropic, ollama
  provider: openai
  
  # API Configuration
  api_key: sk-your-api-key-here
  endpoint: https://api.openai.com/v1
  model: gpt-3.5-turbo
  
  # Response settings
  max_tokens: 256
  temperature: 0.7
  
  features:
    correction: true   # Auto-correct input
    translation: false # Enable translation
    expansion: false   # Enable text expansion
  
  display:
    # Display mode: inline, candidate
    mode: candidate
    max_suggestions: 3
  
  key_bindings:
    accept: Tab       # Accept suggestion
    reject: Escape    # Reject suggestion
    trigger: Ctrl+Shift+a  # Trigger AI manually
  
  performance:
    debounce_ms: 300
    timeout_ms: 2000
    cache_enabled: true
    max_input_chars: 100
]]
    
    local file = io.open(self.config_path, "w")
    if file then
        file:write(config_content)
        file:close()
        utils.info("Default config created at: " .. self.config_path)
        return true
    else
        utils.error("Failed to create default config")
        return false
    end
end

return ConfigManager
