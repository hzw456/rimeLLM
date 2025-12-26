#!/bin/bash

# AI 剪切板 - 启动脚本

echo "⚡ AI 剪切板启动器"
echo "=================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装，请先安装 Python"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 install -q fastapi uvicorn httpx pydantic 2>/dev/null

# 启动后端
echo "🚀 启动后端服务..."
cd "$(dirname "$0")/backend"
python3 main.py > /tmp/ai-clipboard-backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 2

# 检查后端是否运行
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端启动失败"
    cat /tmp/ai-clipboard-backend.log
    exit 1
fi

echo "✅ 后端服务已启动 (http://localhost:8000)"
echo ""
echo "📝 使用说明:"
echo "   1. 后端服务已在后台运行"
echo "   2. 可以使用 curl 测试 API:"
echo "      curl http://localhost:8000/health"
echo "      curl http://localhost:8000/api/v1/config"
echo ""
echo "🛑 按 Ctrl+C 停止服务"

# 等待用户中断
trap "kill $BACKEND_PID 2>/dev/null; echo ''; echo '👋 已停止服务'" INT
wait $BACKEND_PID
