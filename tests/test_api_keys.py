#!/usr/bin/env python3
"""
API金鑰測試腳本
用於驗證Azure Vision和Claude API金鑰是否正確設定
"""

import os
import sys
import requests
import httpx
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def test_azure_vision_api():
    """測試Azure Computer Vision API"""
    print("🔍 測試Azure Computer Vision API...")

    endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    key = os.getenv("AZURE_VISION_KEY")

    if not endpoint or not key:
        print("❌ Azure Vision API金鑰未設定")
        return False

    if "your-resource.cognitiveservices.azure.com" in endpoint:
        print("❌ 請設定真實的Azure Vision端點")
        return False

    try:
        # 測試API連接
        headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"}

        # 使用一個簡單的測試圖片URL
        test_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/printed_text.jpg"

        response = requests.post(
            f"{endpoint}/vision/v3.2/read/analyze",
            headers=headers,
            json={"url": test_image_url},
        )

        if response.status_code == 202:
            print("✅ Azure Vision API連接成功")
            return True
        else:
            print(f"❌ Azure Vision API連接失敗: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Azure Vision API測試錯誤: {str(e)}")
        return False


async def test_claude_api():
    """測試Claude API"""
    print("🤖 測試Claude API...")

    api_key = os.getenv("CLAUDE_API_KEY")

    if not api_key:
        print("❌ Claude API金鑰未設定")
        return False

    if "your_claude_api_key_here" in api_key:
        print("❌ 請設定真實的Claude API金鑰")
        return False

    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test message."}
                    ],
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                print("✅ Claude API連接成功")
                return True
            else:
                print(f"❌ Claude API連接失敗: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Claude API測試錯誤: {str(e)}")
        return False


def check_env_file():
    """檢查.env檔案設定"""
    print("📁 檢查環境變數檔案...")

    if not os.path.exists(".env"):
        print("❌ .env檔案不存在，請複製env.example並設定")
        return False

    print("✅ .env檔案存在")
    return True


def main():
    """主測試函數"""
    print("🚀 API金鑰測試開始")
    print("=" * 50)

    # 檢查.env檔案
    if not check_env_file():
        return

    # 測試Azure Vision API
    azure_ok = test_azure_vision_api()

    # 測試Claude API
    claude_ok = asyncio.run(test_claude_api())

    print("=" * 50)
    print("📊 測試結果總結:")

    if azure_ok and claude_ok:
        print("🎉 所有API金鑰設定正確！")
        print("✅ 您的系統已準備好使用真實的AI服務")
    elif azure_ok:
        print("⚠️  Azure Vision API正常，但Claude API有問題")
    elif claude_ok:
        print("⚠️  Claude API正常，但Azure Vision API有問題")
    else:
        print("❌ 兩個API都有問題，請檢查設定")

    print("\n💡 提示:")
    print("- 如果API測試失敗，請檢查金鑰是否正確")
    print("- 確保網路連接正常")
    print("- 檢查API服務是否在您的區域可用")


if __name__ == "__main__":
    main()
