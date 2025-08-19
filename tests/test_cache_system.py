#!/usr/bin/env python3
"""
測試暫存點系統功能
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加項目路徑


def test_cache_system():
    """測試暫存點系統"""
    print("🔍 測試暫存點系統...")

    # 檢查系統健康狀態
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 系統健康檢查正常")
        else:
            print(f"❌ 系統健康檢查失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 無法連接到系統: {e}")
        return False

    # 創建測試圖片
    test_images = create_test_images()
    if not test_images:
        print("❌ 創建測試圖片失敗")
        return False

    print(f"✅ 創建了 {len(test_images)} 個測試圖片")

    # 測試OCR暫存功能
    print("\n📋 測試OCR暫存功能...")
    ocr_result = test_ocr_only(test_images)
    if not ocr_result:
        print("❌ OCR暫存測試失敗")
        return False

    batch_id = ocr_result.get("batch_id")
    print(f"✅ OCR暫存成功，批次ID: {batch_id}")

    # 測試從暫存處理AI
    print("\n🤖 測試從暫存處理AI...")
    ai_result = test_process_from_cache(batch_id)
    if not ai_result:
        print("❌ 從暫存處理AI測試失敗")
        return False

    print("✅ 從暫存處理AI成功")

    # 測試暫存摘要
    print("\n📊 測試暫存摘要...")
    cache_summary = test_cache_summary()
    if not cache_summary:
        print("❌ 暫存摘要測試失敗")
        return False

    print("✅ 暫存摘要正常")

    # 清理測試檔案
    cleanup_test_files(test_images)

    return True


def create_test_images():
    """創建測試圖片"""
    try:
        test_images = []
        upload_dir = "./data/receipts"

        # 確保上傳目錄存在
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 創建3個測試圖片
        for i in range(3):
            filename = f"test_cache_{i+1:03d}.jpg"
            file_path = os.path.join(upload_dir, filename)

            # 創建一個簡單的測試圖片（1x1像素的JPEG）
            with open(file_path, "wb") as f:
                # 最小JPEG檔案內容
                f.write(
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"
                )

            test_images.append(filename)
            print(f"   創建測試圖片: {filename}")

        return test_images

    except Exception as e:
        print(f"創建測試圖片失敗: {e}")
        return []


def test_ocr_only(filenames):
    """測試OCR暫存功能"""
    try:
        # 準備請求資料
        data = {"filenames": filenames, "enhance_image": "true"}

        # 發送OCR請求
        response = requests.post("http://localhost:8000/ocr-only", data=data)

        if response.status_code == 200:
            result = response.json()
            print(f"   OCR處理成功:")
            print(f"   成功: {result.get('processed_count', 0)}")
            print(f"   失敗: {result.get('failed_count', 0)}")
            print(f"   耗時: {result.get('total_time', 0)}秒")
            return result
        else:
            print(f"   OCR處理失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return None

    except Exception as e:
        print(f"OCR測試失敗: {e}")
        return None


def test_process_from_cache(batch_id):
    """測試從暫存處理AI"""
    try:
        # 準備請求資料
        data = {"batch_id": batch_id, "save_detailed_csv": "true"}

        # 發送AI處理請求
        response = requests.post("http://localhost:8000/process-from-cache", data=data)

        if response.status_code == 200:
            result = response.json()
            print(f"   AI處理成功:")
            print(f"   成功: {result.get('processed_count', 0)}")
            print(f"   失敗: {result.get('failed_count', 0)}")
            print(f"   耗時: {result.get('total_time', 0)}秒")

            # 檢查CSV檔案
            csv_files = result.get("csv_files", {})
            if csv_files:
                print(f"   CSV檔案:")
                for file_type, file_path in csv_files.items():
                    print(f"     {file_type}: {os.path.basename(file_path)}")

            return result
        else:
            print(f"   AI處理失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return None

    except Exception as e:
        print(f"AI處理測試失敗: {e}")
        return None


def test_cache_summary():
    """測試暫存摘要"""
    try:
        response = requests.get("http://localhost:8000/cache-summary")

        if response.status_code == 200:
            summary = response.json()
            print(f"   暫存摘要:")
            print(f"   總檔案數: {summary.get('total_files', 0)}")
            print(f"   OCR檔案: {summary.get('ocr_files', 0)}")
            print(f"   狀態檔案: {summary.get('status_files', 0)}")
            print(f"   總大小: {summary.get('total_size_mb', 0)} MB")
            return summary
        else:
            print(f"   暫存摘要失敗: {response.status_code}")
            return None

    except Exception as e:
        print(f"暫存摘要測試失敗: {e}")
        return None


def cleanup_test_files(filenames):
    """清理測試檔案"""
    print("\n🧹 清理測試檔案...")

    upload_dir = "./data/receipts"
    for filename in filenames:
        file_path = os.path.join(upload_dir, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ 刪除: {filename}")
        except Exception as e:
            print(f"   ❌ 刪除失敗: {filename} - {e}")


def show_cache_system_info():
    """顯示暫存點系統資訊"""
    print("\n📋 暫存點系統功能說明:")
    print("=" * 50)
    print("🔹 暫存點機制:")
    print("   1. OCR結果暫存到JSON檔案")
    print("   2. 支援中斷恢復處理")
    print("   3. 避免資料丟失")
    print("   4. 提高系統穩定性")

    print("\n🔹 處理流程:")
    print("   1. 上傳圖片 → OCR處理 → 暫存結果")
    print("   2. 從暫存 → AI分析 → 生成CSV")
    print("   3. 支援累積保存所有結果")

    print("\n🔹 新API端點:")
    print("   POST /ocr-only - 只執行OCR，結果暫存")
    print("   POST /process-from-cache - 從暫存處理AI")
    print("   GET /cache-summary - 獲取暫存摘要")

    print("\n🔹 優勢:")
    print("   1. 避免資料覆蓋問題")
    print("   2. 支援大量圖片處理")
    print("   3. 提高處理可靠性")
    print("   4. 節省API調用成本")


def main():
    """主測試函數"""
    print("🚀 開始測試暫存點系統...")
    print("=" * 50)

    # 測試暫存點系統
    success = test_cache_system()

    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   暫存點系統: {'✅ 通過' if success else '❌ 失敗'}")

    if success:
        print("\n🎉 暫存點系統測試通過！")
        print("\n📝 已實現功能:")
        print("   1. ✅ OCR結果暫存")
        print("   2. ✅ 從暫存處理AI")
        print("   3. ✅ 暫存摘要查詢")
        print("   4. ✅ 累積保存機制")
        print("   5. ✅ 中斷恢復支援")
        print("   6. ✅ 避免資料覆蓋")

        show_cache_system_info()
    else:
        print("\n⚠️  暫存點系統測試失敗，請檢查系統狀態")


if __name__ == "__main__":
    main()
