#!/usr/bin/env python3
"""
AI 剪切板 - API 测试脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_response(response):
    """格式化打印响应"""
    print("\n" + "=" * 50)
    print(f"状态码: {response.status_code}")
    print("响应:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print("=" * 50)

def test_health():
    """测试健康检查"""
    print("\n🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200

def test_config():
    """测试配置接口"""
    print("\n🔍 测试配置接口...")
    response = requests.get(f"{BASE_URL}/api/v1/config")
    print_response(response)
    return response.status_code == 200

def test_correction():
    """测试文本纠错"""
    print("\n🔍 测试文本纠错...")
    data = {"text": "I goes to school everday"}
    response = requests.post(f"{BASE_URL}/api/v1/correct", json=data)
    print_response(response)
    return response.status_code == 200

def test_translation():
    """测试翻译"""
    print("\n🔍 测试翻译...")
    data = {
        "text": "人工智能正在改变世界",
        "direction": "zh-en"
    }
    response = requests.post(f"{BASE_URL}/api/v1/translate", json=data)
    print_response(response)
    return response.status_code == 200

def test_expansion():
    """测试文本扩写"""
    print("\n🔍 测试文本扩写...")
    data = {
        "text": "项目使用了 React 和 Node.js",
        "ratio": 2.0
    }
    response = requests.post(f"{BASE_URL}/api/v1/expand", json=data)
    print_response(response)
    return response.status_code == 200

def test_provider_test():
    """测试提供商连接"""
    print("\n🔍 测试提供商连接（模拟）...")
    # 这里不会真正调用 API，因为没有真实的 API key
    print("需要配置有效的 API Key 才能测试")
    return True

def main():
    """主测试函数"""
    print("⚡ AI 剪切板 - API 测试")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("配置接口", test_config),
        ("文本纠错", test_correction),
        ("翻译", test_translation),
        ("文本扩写", test_expansion),
        ("提供商测试", test_provider_test),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {name} - 通过")
                passed += 1
            else:
                print(f"❌ {name} - 失败")
                failed += 1
        except Exception as e:
            print(f"❌ {name} - 错误: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
