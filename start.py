#!/usr/bin/env python3
"""
日本收據識別系統啟動腳本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.config import settings


def check_environment():
    """檢查環境設定"""
    print("🔍 檢查環境設定...")

    # 檢查必要的環境變數
    required_vars = ["AZURE_VISION_ENDPOINT", "AZURE_VISION_KEY", "CLAUDE_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ 缺少必要的環境變數:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n請在.env檔案中設定這些變數")
        return False

    print("✅ 環境設定檢查通過")
    return True


def check_directories():
    """檢查必要的目錄"""
    print("📁 檢查目錄結構...")

    directories = [settings.upload_dir, settings.output_dir, "logs"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 目錄已準備: {directory}")

    return True


def main():
    """主函數"""
    print("🚀 啟動日本收據識別系統")
    print("=" * 50)

    # 檢查環境
    if not check_environment():
        print("\n❌ 環境設定檢查失敗，請檢查.env檔案")
        sys.exit(1)

    # 檢查目錄
    if not check_directories():
        print("\n❌ 目錄檢查失敗")
        sys.exit(1)

    print("\n✅ 系統準備完成")
    print("🌐 啟動Web服務...")
    print(f"📱 服務地址: http://localhost:8000")
    print(f"📚 API文檔: http://localhost:8000/docs")
    print("=" * 50)

    # 啟動服務
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )


if __name__ == "__main__":
    main()
