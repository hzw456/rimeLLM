"""
Rime 输入法集成模块

实现与 Rime 输入法的通信，支持：
- 输入上下文捕获
- 建议注入
- 实时状态同步
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InputMode(Enum):
    COMPOSITION = "composition"
    PREEDIT = "preedit"
    COMMITED = "commited"


@dataclass
class InputContext:
    raw_input: str
    composed_text: str
    cursor_position: int
    selection_start: int
    selection_end: int
    input_mode: InputMode
    surrounding_text: Optional[str] = None
    language: str = "zh"


ContextCallback = Callable[[InputContext], Union[None, Any]]
SuggestionCallback = Callable[[Dict[str, Any]], Union[None, Any]]


class RimeClient:
    def __init__(self, socket_path: Optional[str] = None, host: str = "localhost", port: int = 12345):
        self.socket_path = socket_path
        self.host = host
        self.port = port
        self.websocket = None
        self.websocket_module = None
        self.connected = False
        self.context_callbacks: list[ContextCallback] = []
        self.suggestion_callbacks: list[SuggestionCallback] = []
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3
        self._mock_mode = False
    
    async def connect(self) -> bool:
        """建立与 Rime 的连接"""
        try:
            self.websocket_module = __import__('websockets')
            if self.socket_path:
                self.websocket = await self.websocket_module.connect(
                    f"ws://{self.socket_path}",
                    ping_interval=None
                )
            else:
                self.websocket = await self.websocket_module.connect(
                    f"ws://{self.host}:{self.port}",
                    ping_interval=None
                )
            self.connected = True
            self._reconnect_attempts = 0
            self._mock_mode = False
            logger.info(f"Connected to Rime at {self.socket_path or f'{self.host}:{self.port}'}")
            
            asyncio.create_task(self._message_handler())
            return True
        except (ImportError, ModuleNotFoundError):
            logger.warning("websockets not installed, using mock mode")
            self._mock_mode = True
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Rime: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开与 Rime 的连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False
    
    async def _message_handler(self):
        """处理来自 Rime 的消息"""
        if self._mock_mode:
            return
        
        try:
            if not self.websocket:
                return
            async for message in self.websocket:
                data = json.loads(message)
                await self._process_message(data)
        except (self.websocket_module.exceptions.ConnectionClosed if self.websocket_module else Exception):
            logger.warning("Rime connection closed")
            self.connected = False
            await self._reconnect()
        except Exception as e:
            logger.error(f"Message handler error: {e}")
    
    async def _process_message(self, data: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = data.get("type", "")
        
        if msg_type == "context":
            context = self._parse_context(data)
            for callback in self.context_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(context)
                    else:
                        callback(context)
                except Exception as e:
                    logger.error(f"Context callback error: {e}")
        
        elif msg_type == "suggestion":
            for callback in self.suggestion_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Suggestion callback error: {e}")
    
    def _parse_context(self, data: Dict[str, Any]) -> InputContext:
        """解析输入上下文"""
        input_mode_str = data.get("input_mode", "composition")
        try:
            input_mode = InputMode(input_mode_str)
        except ValueError:
            input_mode = InputMode.COMPOSITION
        
        return InputContext(
            raw_input=data.get("raw_input", ""),
            composed_text=data.get("composed_text", ""),
            cursor_position=data.get("cursor_position", 0),
            selection_start=data.get("selection_start", 0),
            selection_end=data.get("selection_end", 0),
            input_mode=input_mode,
            surrounding_text=data.get("surrounding_text"),
            language=data.get("language", "zh")
        )
    
    async def _reconnect(self):
        """尝试重新连接"""
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            logger.info(f"Attempting to reconnect ({self._reconnect_attempts}/{self._max_reconnect_attempts})...")
            await asyncio.sleep(2)
            await self.connect()
        else:
            logger.error("Max reconnection attempts reached")
    
    def on_context(self, callback: ContextCallback):
        """注册上下文变化回调"""
        self.context_callbacks.append(callback)
    
    def on_suggestion(self, callback: SuggestionCallback):
        """注册建议回调"""
        self.suggestion_callbacks.append(callback)
    
    async def send_command(self, command: str, params: Optional[Dict] = None):
        """发送命令到 Rime"""
        if self._mock_mode:
            logger.debug(f"Mock command: {command} with params {params}")
            return
        
        if not self.connected or not self.websocket:
            raise ConnectionError("Not connected to Rime")
        
        message = json.dumps({
            "command": command,
            "params": params or {}
        })
        await self.websocket.send(message)
    
    async def inject_suggestion(self, text: str, position: int = -1):
        """注入 AI 建议"""
        await self.send_command("inject_suggestion", {
            "text": text,
            "position": position
        })
    
    async def show_candidate(self, candidates: list[str], indices: Optional[list[int]] = None):
        """在候选窗显示建议"""
        await self.send_command("show_candidate", {
            "candidates": candidates,
            "indices": indices or list(range(len(candidates)))
        })
    
    async def request_completion(self, context: InputContext):
        """请求自动补全"""
        await self.send_command("request_completion", {
            "context": {
                "raw_input": context.raw_input,
                "composed_text": context.composed_text,
                "cursor_position": context.cursor_position
            }
        })


class RimeInputCapture:
    """输入捕获管理器"""
    
    def __init__(self, client: Optional[RimeClient] = None):
        self.client = client if client is not None else RimeClient()
        self.is_capturing = False
        self._context_buffer: list[InputContext] = []
        self._suggestions: list[Dict[str, Any]] = []
    
    async def start_capture(self):
        """开始捕获输入"""
        if not self.client.connected:
            if not await self.client.connect():
                raise ConnectionError("Failed to connect to Rime")
        
        self.client.on_context(self._on_context_received)
        self.client.on_suggestion(self._on_suggestion_received)
        self.is_capturing = True
        logger.info("Input capture started")
    
    async def stop_capture(self):
        """停止捕获输入"""
        self.is_capturing = False
        if self.client.connected and not self.client._mock_mode:
            await self.client.disconnect()
        logger.info("Input capture stopped")
    
    def _on_context_received(self, context: InputContext):
        """处理接收到的上下文"""
        self._context_buffer.append(context)
        logger.debug(f"Context captured: {context.raw_input}")
    
    def _on_suggestion_received(self, suggestion: Dict[str, Any]):
        """处理接收到的建议"""
        self._suggestions.append(suggestion)
    
    def get_latest_context(self) -> Optional[InputContext]:
        """获取最新的输入上下文"""
        if self._context_buffer:
            return self._context_buffer[-1]
        return None
    
    def get_recent_contexts(self, count: int = 5) -> list[InputContext]:
        """获取最近的输入上下文"""
        return self._context_buffer[-count:]
    
    def clear_contexts(self):
        """清空上下文缓冲区"""
        self._context_buffer.clear()


class RimeSuggestionInjector:
    """建议注入器"""
    
    def __init__(self, client: Optional[RimeClient] = None):
        self.client = client if client is not None else RimeClient()
        self.suggestion_queue: list[Dict[str, Any]] = []
        self._displayed_suggestions: set = set()
    
    async def inject(self, text: str, suggestion_id: Optional[str] = None, priority: int = 0):
        """注入建议"""
        suggestion_id_str = suggestion_id if suggestion_id is not None else f"suggestion_{len(self.suggestion_queue)}"
        suggestion = {
            "id": suggestion_id_str,
            "text": text,
            "priority": priority,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.suggestion_queue.append(suggestion)
        self.suggestion_queue.sort(key=lambda x: x["priority"], reverse=True)
        
        if self.client.connected:
            await self._display_top_suggestion()
    
    async def _display_top_suggestion(self):
        """显示最高优先级的建议"""
        if not self.suggestion_queue:
            return
        
        top = self.suggestion_queue[0]
        if top["id"] not in self._displayed_suggestions:
            await self.client.inject_suggestion(top["text"])
            self._displayed_suggestions.add(top["id"])
    
    async def show_candidates(self, count: int = 5):
        """显示多个候选建议"""
        candidates = [s["text"] for s in self.suggestion_queue[:count]]
        if candidates and self.client.connected:
            await self.client.show_candidate(candidates)
    
    async def accept_suggestion(self, suggestion_id: str):
        """接受建议"""
        self.suggestion_queue = [
            s for s in self.suggestion_queue if s["id"] != suggestion_id
        ]
        self._displayed_suggestions.discard(suggestion_id)
    
    async def reject_suggestion(self, suggestion_id: str):
        """拒绝建议"""
        self.suggestion_queue = [
            s for s in self.suggestion_queue if s["id"] != suggestion_id
        ]
        self._displayed_suggestions.discard(suggestion_id)
    
    def clear_queue(self):
        """清空建议队列"""
        self.suggestion_queue.clear()
        self._displayed_suggestions.clear()


async def main():
    """测试 Rime 集成"""
    client = RimeClient()
    
    async def on_context(ctx: InputContext):
        print(f"Context: {ctx.raw_input} -> {ctx.composed_text}")
    
    async def on_suggestion(data: Dict[str, Any]):
        print(f"Suggestion: {data}")
    
    client.on_context(on_context)
    client.on_suggestion(on_suggestion)
    
    try:
        if await client.connect():
            print("Connected to Rime (mock mode)" if client._mock_mode else "Connected to Rime")
            
            capture = RimeInputCapture(client)
            await capture.start_capture()
            
            await asyncio.sleep(10)
            
            await capture.stop_capture()
            
            await client.disconnect()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
