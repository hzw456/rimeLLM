local AiClient = {}
local AiClient_mt = { __index = AiClient }

local utils = require("utils")

function AiClient.new(config_manager)
    local self = setmetatable({}, AiClient_mt)
    self.config = config_manager
    self.cache = {}
    self.cache_max_size = 50
    self.request_id = 0
    return self
end

function AiClient:init()
    self.cache_max_size = self.config:get("performance.cache_max_size", 50)
    utils.info("AI Client initialized with provider: " .. self.config:get_provider())
end

function AiClient:clear_cache()
    self.cache = {}
    utils.info("AI cache cleared")
end

function AiClient:get_cache_key(provider, endpoint, model, prompt)
    return provider .. "_" .. endpoint .. "_" .. model .. "_" .. utils.md5(prompt)
end

function AiClient:_check_cache(prompt)
    if not self.config:should_use_cache() then
        return nil
    end
    
    local provider = self.config:get_provider()
    local endpoint = self.config:get("endpoint", "")
    local model = self.config:get("model", "")
    local cache_key = self:get_cache_key(provider, endpoint, model, prompt)
    
    if self.cache[cache_key] then
        local cached = self.cache[cache_key]
        local now = utils.get_time_ms()
        if now - cached.timestamp < 300000 then
            utils.debug("Cache hit for: " .. string.sub(prompt, 1, 30) .. "...")
            return cached.response
        end
    end
    return nil
end

function AiClient:_add_to_cache(prompt, response)
    local provider = self.config:get_provider()
    local endpoint = self.config:get("endpoint", "")
    local model = self.config:get("model", "")
    local cache_key = self.get_cache_key(provider, endpoint, model, prompt)
    
    self.cache[cache_key] = {
        response = response,
        timestamp = utils.get_time_ms()
    }
    
    local count = 0
    for _ in pairs(self.cache) do
        count = count + 1
    end
    
    if count > self.cache_max_size then
        local oldest_key = nil
        local oldest_time = math.huge
        for k, v in pairs(self.cache) do
            if v.timestamp < oldest_time then
                oldest_time = v.timestamp
                oldest_key = k
            end
        end
        if oldest_key then
            self.cache[oldest_key] = nil
        end
    end
end

function AiClient:chat(system_prompt, user_prompt, callback)
    local provider = self.config:get_provider()
    
    local cached = self:_check_cache(user_prompt)
    if cached then
        if callback then
            callback({ success = true, response = cached })
        end
        return
    end
    
    self.request_id = self.request_id + 1
    local current_request = self.request_id
    
    local function on_response(resp)
        if self.request_id ~= current_request then
            return
        end
        
        if resp.success then
            self:_add_to_cache(user_prompt, resp.response)
            if callback then
                callback({ success = true, response = resp.response })
            end
        else
            utils.error("AI request failed: " .. tostring(resp.error))
            if callback then
                callback({ success = false, error = resp.error })
            end
        end
    end
    
    if provider == "openai" then
        self:_request_openai(system_prompt, user_prompt, on_response)
    elseif provider == "anthropic" then
        self:_request_anthropic(system_prompt, user_prompt, on_response)
    elseif provider == "ollama" then
        self:_request_ollama(system_prompt, user_prompt, on_response)
    else
        callback({ success = false, error = "Unknown provider: " .. provider })
    end
end

function AiClient:_request_openai(system_prompt, user_prompt, callback)
    local config = self.config:get_api_config()
    local timeout = self.config:get("performance.timeout_ms", 2000)
    
    local messages = {
        { role = "system", content = system_prompt },
        { role = "user", content = user_prompt }
    }
    
    local payload = {
        model = config.model,
        messages = messages,
        max_tokens = config.max_tokens,
        temperature = config.temperature
    }
    
    local headers = {
        "Content-Type: application/json",
        "Authorization: Bearer " .. config.api_key
    }
    
    self:_send_http_request(config.endpoint .. "/chat/completions", "POST", headers, payload, timeout, callback)
end

function AiClient:_request_anthropic(system_prompt, user_prompt, callback)
    local config = self.config:get_api_config()
    local timeout = self.config:get("performance.timeout_ms", 2000)
    
    local payload = {
        model = config.model,
        max_tokens = config.max_tokens,
        temperature = config.temperature,
        system = system_prompt,
        messages = {
            { role = "user", content = user_prompt }
        }
    }
    
    local headers = {
        "Content-Type: application/json",
        "x-api-key: " .. config.api_key,
        "anthropic-version: 2023-06-01"
    }
    
    self:_send_http_request("https://api.anthropic.com/v1/messages", "POST", headers, payload, timeout, callback)
end

function AiClient:_request_ollama(system_prompt, user_prompt, callback)
    local config = self.config:get_api_config()
    local timeout = self.config:get("performance.timeout_ms", 2000)
    
    local endpoint = config.endpoint
    if not utils.startswith(endpoint, "http") then
        endpoint = "http://" .. endpoint
    end
    
    local payload = {
        model = config.model,
        prompt = system_prompt .. "\n\nUser: " .. user_prompt,
        stream = false,
        options = {
            num_predict = config.max_tokens,
            temperature = config.temperature
        }
    }
    
    local headers = {
        "Content-Type: application/json"
    }
    
    self:_send_http_request(endpoint .. "/api/generate", "POST", headers, payload, timeout, callback)
end

function AiClient:_send_http_request(url, method, headers, payload, timeout, callback)
    self.request_id = self.request_id + 1
    local current_request = self.request_id
    
    local function done(success, response, error_msg)
        if self.request_id ~= current_request then
            return
        end
        
        if success then
            local parsed = self:_parse_response(response)
            if parsed then
                callback({ success = true, response = parsed })
            else
                callback({ success = false, error = "Failed to parse response" })
            end
        else
            callback({ success = false, error = error_msg or "HTTP request failed" })
        end
    end
    
    local json_payload = utils.json_encode(payload)
    local body = json_payload and json_payload:len() > 0 and json_payload or ""
    
    local all_headers = {}
    for _, h in ipairs(headers) do
        table.insert(all_headers, h)
    end
    
    local ok, response = pcall(function()
        return rime.http_post and rime.http_post(url, body, table.concat(all_headers, "\n"), timeout)
    end)
    
    if ok and response then
        done(true, response, nil)
    else
        ok, response = pcall(function()
            return rime.http_get and rime.http_get(url, table.concat(all_headers, "\n"), timeout)
        end)
        if ok and response then
            done(true, response, nil)
        else
            done(false, nil, "HTTP request failed: " .. tostring(response))
        end
    end
end

function AiClient:_parse_response(response)
    local json = utils.json_decode(response)
    if not json then
        return nil
    end
    
    local provider = self.config:get_provider()
    
    if provider == "openai" then
        if json.choices and json.choices[1] and json.choices[1].message then
            return json.choices[1].message.content
        end
    elseif provider == "anthropic" then
        if json.content and json.content[1] and json.content[1].text then
            return json.content[1].text
        end
    elseif provider == "ollama" then
        if json.response then
            return json.response
        end
    end
    
    return nil
end

return AiClient
