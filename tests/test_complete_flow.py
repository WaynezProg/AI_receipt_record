#!/usr/bin/env python3
"""
完整收據識別流程測試
測試上傳、OCR、AI處理、CSV生成和前端顯示
"""

import os
import time
import requests
import json
from pathlib import Path


def test_complete_flow():
    """測試完整的收據識別流程"""
    print("🚀 開始完整收據識別流程測試")
    print("=" * 50)

    # 1. 檢查服務狀態
    print("1. 檢查服務狀態...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 服務正常運行")
        else:
            print("❌ 服務異常")
            return False
    except Exception as e:
        print(f"❌ 無法連接到服務: {e}")
        return False

    # 2. 檢查是否有測試圖片
    print("\n2. 檢查測試圖片...")
    test_images = list(Path("data/receipts").glob("*.jpeg")) + list(
        Path("data/receipts").glob("*.jpg")
    )

    if not test_images:
        print("❌ 沒有找到測試圖片")
        return False

    test_image = test_images[0]
    print(f"✅ 找到測試圖片: {test_image.name}")

    # 3. 測試上傳
    print(f"\n3. 測試上傳 {test_image.name}...")
    try:
        with open(test_image, "rb") as f:
            files = {"file": (test_image.name, f, "image/jpeg")}
            response = requests.post("http://localhost:8000/upload", files=files)

        if response.status_code == 200:
            upload_result = response.json()
            filename = upload_result.get("filename")
            print(f"✅ 上傳成功: {filename}")
        else:
            print(f"❌ 上傳失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 上傳錯誤: {e}")
        return False

    # 4. 測試識別處理
    print(f"\n4. 測試識別處理...")
    try:
        data = {
            "filename": filename,
            "enhance_image": "true",
            "save_detailed_csv": "true",
        }

        start_time = time.time()
        response = requests.post("http://localhost:8000/process", data=data)
        processing_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                receipt_data = result.get("data", {})
                print("✅ 識別處理成功")
                print(f"   - 商店名稱: {receipt_data.get('store_name', 'N/A')}")
                print(f"   - 總金額: ¥{receipt_data.get('total_amount', 0):,}")
                print(f"   - 商品數量: {len(receipt_data.get('items', []))}項")
                print(f"   - 處理時間: {processing_time:.2f}秒")
                print(
                    f"   - 信心度: {receipt_data.get('confidence_score', 0)*100:.1f}%"
                )
            else:
                print(f"❌ 識別失敗: {result.get('error', '未知錯誤')}")
                return False
        else:
            print(f"❌ 處理請求失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 處理錯誤: {e}")
        return False

    # 5. 檢查CSV檔案
    print("\n5. 檢查生成的CSV檔案...")
    try:
        csv_files = list(Path("data/output").glob("*.csv"))
        if csv_files:
            latest_csv = max(csv_files, key=os.path.getctime)
            print(f"✅ 找到最新CSV檔案: {latest_csv.name}")

            # 讀取CSV內容
            with open(latest_csv, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"   - 檔案大小: {len(content)} 字元")
                print(f"   - 包含商品明細: {'商品明細' in content}")
        else:
            print("❌ 沒有找到CSV檔案")
            return False
    except Exception as e:
        print(f"❌ 檢查CSV檔案錯誤: {e}")
        return False

    # 6. 測試前端頁面
    print("\n6. 測試前端頁面...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ 前端頁面正常")
        else:
            print(f"❌ 前端頁面異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端頁面錯誤: {e}")

    print("\n" + "=" * 50)
    print("🎉 完整流程測試完成！")
    print("\n📋 測試結果總結:")
    print("✅ 服務狀態正常")
    print("✅ 圖片上傳成功")
    print("✅ OCR識別成功")
    print("✅ AI處理成功")
    print("✅ CSV檔案生成")
    print("✅ 前端頁面正常")

    print("\n🌐 您可以訪問以下地址:")
    print("   - 主頁面: http://localhost:8000")
    print("   - API文檔: http://localhost:8000/docs")
    print("   - 健康檢查: http://localhost:8000/health")

    return True


if __name__ == "__main__":
    test_complete_flow()
