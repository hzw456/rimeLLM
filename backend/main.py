from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import json
import os

app = FastAPI(
    title="AI 剪切板后端服务",
    description="智能输入增强工具后端 API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = os.path.expanduser("~/.config/ai-clipboard/config.json")

class ProviderConfig(BaseModel):
    type: str
    apiKey: str
    endpoint: Optional[str] = None
    model: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    direction: str = "zh-en"

class CorrectionRequest(BaseModel):
    text: str

class ExpansionRequest(BaseModel):
    text: str
    ratio: float = 2.0

def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"providers": [], "default_provider": "", "features": {}}

def save_config(config: Dict):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/api/v1/config")
async def get_config():
    return load_config()

@app.post("/api/v1/config")
async def save_config_endpoint(config: Dict):
    save_config(config)
    return {"success": True}

@app.post("/api/v1/providers/test")
async def test_provider(provider: ProviderConfig):
    import httpx
    
    try:
        if provider.type == "openai":
            endpoint = provider.endpoint or "https://api.openai.com/v1/chat/completions"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {provider.apiKey}"},
                    json={
                        "model": provider.model or "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {"success": True, "message": "连接成功"}
                else:
                    return {"success": False, "error": response.json().get("error", {}).get("message", "Unknown error")}
                    
        elif provider.type == "anthropic":
            endpoint = provider.endpoint or "https://api.anthropic.com/v1/messages"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {provider.apiKey}",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": provider.model or "claude-sonnet-4-20250514",
                        "max_tokens": 5,
                        "messages": [{"role": "user", "content": "Hello"}]
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {"success": True, "message": "连接成功"}
                else:
                    return {"success": False, "error": response.json().get("error", {}).get("message", "Unknown error")}
                    
        elif provider.type == "local":
            endpoint = provider.endpoint or "http://localhost:11434/v1/chat/completions"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    json={
                        "model": provider.model or "llama3",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {"success": True, "message": "连接成功"}
                else:
                    return {"success": False, "error": "Local model not available"}
                    
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Unknown provider type"}

@app.post("/api/v1/translate")
async def translate(request: TranslationRequest):
    config = load_config()
    providers = config.get("providers", [])
    
    if not providers:
        return {"result": "[请先配置 AI 提供商]", "error": "No provider configured"}
    
    provider = providers[0]
    
    if provider["type"] == "openai":
        prompt = f"Translate the following text from {'Chinese to English' if request.direction == 'zh-en' else 'English to Chinese'}:\n\n{request.text}"
        return await call_openai(provider, prompt)
    elif provider["type"] == "anthropic":
        prompt = f"Translate this text from {'Chinese to English' if request.direction == 'zh-en' else 'English to Chinese'}:\n{request.text}"
        return await call_anthropic(provider, prompt)
    elif provider["type"] == "local":
        return {"result": "[本地模型暂不支持翻译]", "error": "Not implemented"}
    
    return {"error": "Unknown provider"}

@app.post("/api/v1/correct")
async def correct(request: CorrectionRequest):
    config = load_config()
    providers = config.get("providers", [])
    
    if not providers:
        return {"result": "[请先配置 AI 提供商]", "error": "No provider configured"}
    
    provider = providers[0]
    prompt = f"Correct any grammar, spelling, or punctuation errors in the following text. Only return the corrected text, no explanations:\n\n{request.text}"
    
    if provider["type"] == "openai":
        return await call_openai(provider, prompt)
    elif provider["type"] == "anthropic":
        return await call_anthropic(provider, prompt)
    
    return {"error": "Unknown provider"}

@app.post("/api/v1/expand")
async def expand(request: ExpansionRequest):
    config = load_config()
    providers = config.get("providers", [])
    
    if not providers:
        return {"result": "[请先配置 AI 提供商]", "error": "No provider configured"}
    
    provider = providers[0]
    prompt = f"Expand the following text by approximately {request.ratio}x, maintaining the original meaning and style:\n\n{request.text}"
    
    if provider["type"] == "openai":
        return await call_openai(provider, prompt)
    elif provider["type"] == "anthropic":
        return await call_anthropic(provider, prompt)
    
    return {"error": "Unknown provider"}

async def call_openai(provider: Dict, prompt: str) -> Dict:
    import httpx
    
    try:
        endpoint = provider.get("endpoint") or "https://api.openai.com/v1/chat/completions"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {provider['apiKey']}"},
                json={
                    "model": provider.get("model") or "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                return {"result": result}
            else:
                error = response.json().get("error", {})
                return {"error": error.get("message", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

async def call_anthropic(provider: Dict, prompt: str) -> Dict:
    import httpx
    
    try:
        endpoint = provider.get("endpoint") or "https://api.anthropic.com/v1/messages"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {provider['apiKey']}",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": provider.get("model") or "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data["content"][0]["text"]
                return {"result": result}
            else:
                error = response.json().get("error", {})
                return {"error": error.get("message", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
