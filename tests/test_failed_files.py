#!/usr/bin/env python3
"""
測試重新處理失敗的檔案
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加項目路徑


def test_failed_files():
    """測試重新處理失敗的檔案"""
    print("🔄 測試重新處理失敗的檔案...")
    print("=" * 50)

    # 檢查系統健康狀態
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 系統健康檢查正常")
        else:
            print(f"❌ 系統健康檢查失敗: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 無法連接到系統: {e}")
        return

    # 失敗的檔案列表（從日誌中獲取）
    failed_files = [
        "receipt_20250817_170034_004.jpeg",
        "receipt_20250817_170034_005.jpeg",
        "receipt_20250817_170034_007.jpeg",
    ]

    print(f"📋 重新處理 {len(failed_files)} 個失敗的檔案:")
    for i, filename in enumerate(failed_files):
        print(f"   {i+1}. {filename}")

    # 檢查檔案是否存在
    upload_dir = "./data/receipts"
    existing_files = []
    for filename in failed_files:
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            existing_files.append(filename)
            print(f"   ✅ {filename} 存在 ({file_size:.2f}MB)")
        else:
            print(f"   ❌ {filename} 不存在")

    if not existing_files:
        print("❌ 沒有找到失敗的檔案")
        return

    # 測試重新處理（不增強圖片品質）
    print(f"\n🔄 重新處理 {len(existing_files)} 個檔案（不增強圖片品質）...")

    try:
        # 準備請求資料
        data = {
            "filenames": existing_files,
            "enhance_image": "false",  # 不增強圖片品質
            "save_detailed_csv": "true",
        }

        # 發送批量處理請求
        start_time = time.time()
        response = requests.post("http://localhost:8000/process-batch", data=data)
        end_time = time.time()

        print(f"   請求耗時: {end_time - start_time:.2f} 秒")

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 重新處理成功:")
            print(f"   成功: {result.get('processed_count', 0)}")
            print(f"   失敗: {result.get('failed_count', 0)}")
            print(f"   總耗時: {result.get('total_time', 0)} 秒")

            # 檢查失敗的檔案
            failed_files = result.get("failed_files", [])
            if failed_files:
                print(f"   ❌ 仍然失敗的檔案:")
                for failed in failed_files:
                    print(
                        f"     - {failed.get('filename', 'unknown')}: {failed.get('error', 'unknown error')}"
                    )
            else:
                print(f"   🎉 所有檔案都成功處理！")

            # 檢查CSV檔案
            csv_files = result.get("csv_files", {})
            if csv_files:
                print(f"   📊 CSV檔案:")
                for file_type, file_path in csv_files.items():
                    print(f"     {file_type}: {os.path.basename(file_path)}")

            return result.get("processed_count", 0) == len(existing_files)
        else:
            print(f"   ❌ 重新處理失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ 重新處理錯誤: {e}")
        return False


def main():
    """主測試函數"""
    success = test_failed_files()

    print("\n" + "=" * 50)
    print("📊 測試總結:")
    print(f"   重新處理失敗檔案: {'✅ 成功' if success else '❌ 失敗'}")

    if success:
        print("\n🎉 失敗檔案重新處理成功！")
        print("   問題已解決：圖片品質增強導致的檔案大小超限")
        print("   建議：對於大檔案，關閉圖片品質增強功能")
    else:
        print("\n⚠️  失敗檔案重新處理失敗")
        print("   需要進一步診斷問題")


if __name__ == "__main__":
    main()
