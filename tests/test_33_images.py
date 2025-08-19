#!/usr/bin/env python3
"""
測試33張照片的批量處理
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加項目路徑


def create_33_test_images():
    """創建33張測試圖片"""
    print("🖼️  創建33張測試圖片...")

    upload_dir = "./data/receipts"

    # 確保目錄存在
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 清理現有的測試圖片
    for file in os.listdir(upload_dir):
        if file.startswith("test_33_"):
            os.remove(os.path.join(upload_dir, file))

    # 創建33張測試圖片
    test_images = []
    for i in range(33):
        filename = f"test_33_{i+1:03d}.jpg"
        file_path = os.path.join(upload_dir, filename)

        # 創建一個簡單的測試圖片
        with open(file_path, "wb") as f:
            # 最小JPEG檔案內容
            f.write(
                b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"
            )

        test_images.append(filename)
        if (i + 1) % 10 == 0:
            print(f"   已創建 {i + 1} 張圖片...")

    print(f"✅ 成功創建 {len(test_images)} 張測試圖片")
    return test_images


def test_batch_upload(filenames):
    """測試批量上傳"""
    print("\n📤 測試批量上傳...")

    try:
        # 準備FormData
        files = []
        for filename in filenames:
            file_path = os.path.join("./data/receipts", filename)
            with open(file_path, "rb") as f:
                files.append(("files", (filename, f.read(), "image/jpeg")))

        print(f"   準備上傳 {len(files)} 個檔案...")

        # 發送批量上傳請求
        response = requests.post("http://localhost:8000/upload-batch", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批量上傳成功:")
            print(f"   成功: {result.get('uploaded_count', 0)}")
            print(f"   失敗: {result.get('failed_count', 0)}")
            print(f"   檔案列表: {result.get('uploaded_files', [])}")
            return result.get("uploaded_files", [])
        else:
            print(f"   ❌ 批量上傳失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return []

    except Exception as e:
        print(f"   ❌ 批量上傳錯誤: {e}")
        return []


def test_batch_processing(filenames):
    """測試批量處理"""
    print("\n🔄 測試批量處理...")

    try:
        # 準備請求資料
        data = {
            "filenames": filenames,
            "enhance_image": "true",
            "save_detailed_csv": "true",
        }

        print(f"   準備處理 {len(filenames)} 個檔案...")
        print(f"   檔案列表: {filenames}")

        # 發送批量處理請求
        start_time = time.time()
        response = requests.post("http://localhost:8000/process-batch", data=data)
        end_time = time.time()

        print(f"   請求耗時: {end_time - start_time:.2f} 秒")

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批量處理成功:")
            print(f"   成功: {result.get('processed_count', 0)}")
            print(f"   失敗: {result.get('failed_count', 0)}")
            print(f"   總耗時: {result.get('total_time', 0)} 秒")

            # 檢查失敗的檔案
            failed_files = result.get("failed_files", [])
            if failed_files:
                print(f"   ❌ 失敗的檔案:")
                for failed in failed_files:
                    print(
                        f"     - {failed.get('filename', 'unknown')}: {failed.get('error', 'unknown error')}"
                    )

            return result
        else:
            print(f"   ❌ 批量處理失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ 批量處理錯誤: {e}")
        return None


def monitor_progress():
    """監控處理進度"""
    print("\n📊 監控處理進度...")

    try:
        response = requests.get("http://localhost:8000/batch-progress")

        if response.status_code == 200:
            progress = response.json()
            print(f"   進度: {progress.get('progress', {})}")
            return progress
        else:
            print(f"   ❌ 獲取進度失敗: {response.status_code}")
            return None

    except Exception as e:
        print(f"   ❌ 監控進度錯誤: {e}")
        return None


def cleanup_test_files(filenames):
    """清理測試檔案"""
    print("\n🧹 清理測試檔案...")

    upload_dir = "./data/receipts"
    cleaned_count = 0

    for filename in filenames:
        file_path = os.path.join(upload_dir, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                cleaned_count += 1
        except Exception as e:
            print(f"   ❌ 刪除失敗: {filename} - {e}")

    print(f"   ✅ 清理完成，刪除 {cleaned_count} 個檔案")


def main():
    """主測試函數"""
    print("🚀 開始測試33張照片批量處理...")
    print("=" * 60)

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

    # 創建33張測試圖片
    test_images = create_33_test_images()

    # 測試批量上傳
    uploaded_files = test_batch_upload(test_images)
    if not uploaded_files:
        print("❌ 批量上傳失敗，無法繼續測試")
        cleanup_test_files(test_images)
        return

    print(f"✅ 批量上傳成功，準備處理 {len(uploaded_files)} 個檔案")

    # 測試批量處理
    result = test_batch_processing(uploaded_files)

    if result:
        print(f"\n🎉 批量處理完成！")
        print(f"   總檔案數: {len(uploaded_files)}")
        print(f"   成功處理: {result.get('processed_count', 0)}")
        print(f"   處理失敗: {result.get('failed_count', 0)}")
        print(f"   總耗時: {result.get('total_time', 0)} 秒")

        # 檢查CSV檔案
        csv_files = result.get("csv_files", {})
        if csv_files:
            print(f"   📊 CSV檔案:")
            for file_type, file_path in csv_files.items():
                print(f"     {file_type}: {os.path.basename(file_path)}")

        if result.get("processed_count", 0) == len(uploaded_files):
            print("\n✅ 所有檔案都成功處理！")
        else:
            print(
                f"\n⚠️  有 {len(uploaded_files) - result.get('processed_count', 0)} 個檔案處理失敗"
            )
    else:
        print("\n❌ 批量處理失敗")

    # 清理測試檔案
    cleanup_test_files(test_images)

    print("\n" + "=" * 60)
    print("📊 測試總結:")
    print(f"   測試檔案數: {len(test_images)}")
    print(f"   上傳成功: {len(uploaded_files)}")
    print(f"   處理成功: {result.get('processed_count', 0) if result else 0}")
    print(
        f"   處理失敗: {result.get('failed_count', 0) if result else len(uploaded_files)}"
    )


if __name__ == "__main__":
    main()
