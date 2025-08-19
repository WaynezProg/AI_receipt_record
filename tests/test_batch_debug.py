#!/usr/bin/env python3
"""
調試批量處理問題
"""

import os
import sys
import requests
import json


def check_uploaded_files():
    """檢查已上傳的檔案"""
    print("🔍 檢查已上傳的檔案...")

    upload_dir = "./data/receipts"
    if not os.path.exists(upload_dir):
        print("❌ 上傳目錄不存在")
        return []

    files = [
        f
        for f in os.listdir(upload_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".pdf"))
    ]

    print(f"✅ 找到 {len(files)} 個圖片檔案:")
    for i, file in enumerate(files, 1):
        file_path = os.path.join(upload_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"   {i}. {file} ({file_size:,} bytes)")

    return files


def test_batch_api():
    """測試批量處理API"""
    print("\n🔍 測試批量處理API...")

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

    # 檢查批次進度API
    try:
        response = requests.get("http://localhost:8000/batch-progress")
        if response.status_code == 200:
            data = response.json()
            print("✅ 批次進度API正常")
            print(
                f"   當前進度: {data['progress']['current_progress']}/{data['progress']['total_items']}"
            )
            print(
                f"   當前批次: {data['progress']['current_batch']}/{data['progress']['total_batches']}"
            )
        else:
            print(f"❌ 批次進度API失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 批次進度API錯誤: {e}")

    return True


def simulate_batch_request():
    """模擬批量處理請求"""
    print("\n🔍 模擬批量處理請求...")

    # 獲取上傳的檔案
    files = check_uploaded_files()
    if not files:
        print("❌ 沒有找到上傳的檔案")
        return False

    # 選擇前3個檔案進行測試
    test_files = files[:3]
    print(f"📋 測試檔案: {test_files}")

    # 構建請求數據
    form_data = {}
    for filename in test_files:
        if "filenames" not in form_data:
            form_data["filenames"] = []
        form_data["filenames"].append(filename)

    form_data["enhance_image"] = "true"
    form_data["save_detailed_csv"] = "true"

    print(f"📤 請求數據: {form_data}")

    try:
        # 發送請求
        response = requests.post(
            "http://localhost:8000/process-batch", data=form_data, timeout=30
        )

        print(f"📥 回應狀態: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ 批量處理請求成功")
            print(f"   處理結果: {result}")
        else:
            print(f"❌ 批量處理請求失敗: {response.text}")

    except Exception as e:
        print(f"❌ 請求錯誤: {e}")

    return True


def check_processing_logs():
    """檢查處理日誌"""
    print("\n🔍 檢查處理日誌...")

    # 檢查是否有重複處理的檔案
    log_patterns = [
        "receipt_20250817_154850.jpeg",
        "批次處理 - OCR:",
        "批次處理 - AI:",
        "批次處理失敗:",
    ]

    print("📋 常見日誌模式:")
    for pattern in log_patterns:
        print(f"   - {pattern}")

    print("\n💡 建議檢查:")
    print("   1. 上傳的檔案是否真的有多個")
    print("   2. 前端是否正確傳遞檔案列表")
    print("   3. 後端是否正確接收檔案列表")
    print("   4. 批量處理邏輯是否正確")


def show_debug_guidelines():
    """顯示調試指南"""
    print("\n📋 調試指南:")
    print("=" * 50)
    print("🔹 可能的原因:")
    print("   1. 上傳的檔案列表中只有一張圖片")
    print("   2. 前端沒有正確傳遞檔案列表")
    print("   3. 後端沒有正確接收檔案列表")
    print("   4. 批量處理邏輯有問題")

    print("\n🔹 調試步驟:")
    print("   1. 檢查上傳目錄中的檔案")
    print("   2. 檢查前端檔案列表")
    print("   3. 檢查後端接收的檔案列表")
    print("   4. 檢查批量處理邏輯")

    print("\n🔹 解決方案:")
    print("   1. 確保上傳多個檔案")
    print("   2. 檢查前端FormData構建")
    print("   3. 檢查後端參數接收")
    print("   4. 添加更多日誌輸出")


def main():
    """主調試函數"""
    print("🚀 開始調試批量處理問題...")
    print("=" * 50)

    # 執行調試步驟
    files_ok = check_uploaded_files()
    api_ok = test_batch_api()
    request_ok = simulate_batch_request()

    print("\n" + "=" * 50)
    print("📊 調試結果總結:")
    print(f"   檔案檢查: {'✅ 通過' if files_ok else '❌ 失敗'}")
    print(f"   API測試: {'✅ 通過' if api_ok else '❌ 失敗'}")
    print(f"   請求模擬: {'✅ 通過' if request_ok else '❌ 失敗'}")

    check_processing_logs()
    show_debug_guidelines()


if __name__ == "__main__":
    main()
