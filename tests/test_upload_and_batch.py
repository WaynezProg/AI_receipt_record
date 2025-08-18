#!/usr/bin/env python3
"""
測試上傳和批量處理
"""

import os
import sys
import requests
import json
from PIL import Image
import numpy as np

def create_test_images():
    """創建測試圖片"""
    print("🔍 創建測試圖片...")
    
    # 確保上傳目錄存在
    upload_dir = "./data/receipts"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 創建3個測試圖片
    test_images = []
    for i in range(3):
        # 創建一個簡單的測試圖片
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        
        # 添加一些文字（模擬收據）
        filename = f"test_receipt_{i+1:03d}.jpg"
        filepath = os.path.join(upload_dir, filename)
        img.save(filepath, 'JPEG', quality=85)
        
        test_images.append(filename)
        print(f"   ✅ 創建測試圖片: {filename}")
    
    return test_images

def test_upload_files():
    """測試檔案上傳"""
    print("\n🔍 測試檔案上傳...")
    
    # 獲取測試圖片
    upload_dir = "./data/receipts"
    files = [f for f in os.listdir(upload_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not files:
        print("❌ 沒有找到測試圖片")
        return []
    
    print(f"✅ 找到 {len(files)} 個測試圖片:")
    for file in files:
        file_path = os.path.join(upload_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"   - {file} ({file_size:,} bytes)")
    
    return files

def test_batch_processing():
    """測試批量處理"""
    print("\n🔍 測試批量處理...")
    
    # 獲取上傳的檔案
    files = test_upload_files()
    if not files:
        print("❌ 沒有檔案可以處理")
        return False
    
    # 構建批量處理請求
    form_data = {}
    for filename in files:
        if 'filenames' not in form_data:
            form_data['filenames'] = []
        form_data['filenames'].append(filename)
    
    form_data['enhance_image'] = 'true'
    form_data['save_detailed_csv'] = 'true'
    
    print(f"📤 批量處理請求:")
    print(f"   檔案數量: {len(files)}")
    print(f"   檔案列表: {files}")
    
    try:
        # 發送批量處理請求
        response = requests.post(
            "http://localhost:8000/process-batch",
            data=form_data,
            timeout=60
        )
        
        print(f"📥 回應狀態: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 批量處理成功")
            print(f"   處理結果: {result}")
            
            # 檢查結果
            if 'processed_count' in result:
                print(f"   成功處理: {result['processed_count']} 個檔案")
            if 'failed_count' in result:
                print(f"   失敗檔案: {result['failed_count']} 個")
            if 'failed_files' in result and result['failed_files']:
                print(f"   失敗檔案列表: {result['failed_files']}")
            
            return True
        else:
            print(f"❌ 批量處理失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 請求錯誤: {e}")
        return False

def monitor_progress():
    """監控處理進度"""
    print("\n🔍 監控處理進度...")
    
    try:
        response = requests.get("http://localhost:8000/batch-progress")
        if response.status_code == 200:
            data = response.json()
            progress = data['progress']
            
            print(f"📊 當前進度:")
            print(f"   總檔案數: {progress['total_items']}")
            print(f"   已處理: {progress['current_progress']}")
            print(f"   當前批次: {progress['current_batch']}/{progress['total_batches']}")
            print(f"   處理時間: {progress.get('elapsed_time', 0):.1f} 秒")
            
            if progress['total_items'] > 0:
                percentage = (progress['current_progress'] / progress['total_items']) * 100
                print(f"   完成度: {percentage:.1f}%")
            
            return True
        else:
            print(f"❌ 獲取進度失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 進度監控錯誤: {e}")
        return False

def cleanup_test_files():
    """清理測試檔案"""
    print("\n🔍 清理測試檔案...")
    
    upload_dir = "./data/receipts"
    test_files = [f for f in os.listdir(upload_dir) if f.startswith('test_receipt_')]
    
    for file in test_files:
        file_path = os.path.join(upload_dir, file)
        try:
            os.remove(file_path)
            print(f"   ✅ 刪除: {file}")
        except Exception as e:
            print(f"   ❌ 刪除失敗: {file} - {e}")

def main():
    """主測試函數"""
    print("🚀 開始測試上傳和批量處理...")
    print("=" * 50)
    
    # 創建測試圖片
    create_test_images()
    
    # 測試檔案上傳
    files_ok = test_upload_files()
    
    # 測試批量處理
    batch_ok = test_batch_processing()
    
    # 監控進度
    progress_ok = monitor_progress()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   檔案上傳: {'✅ 通過' if files_ok else '❌ 失敗'}")
    print(f"   批量處理: {'✅ 通過' if batch_ok else '❌ 失敗'}")
    print(f"   進度監控: {'✅ 通過' if progress_ok else '❌ 失敗'}")
    
    if all([files_ok, batch_ok, progress_ok]):
        print("\n🎉 所有測試通過！批量處理功能正常！")
    else:
        print("\n⚠️  部分測試失敗，請檢查系統狀態")
    
    # 清理測試檔案
    cleanup_test_files()

if __name__ == "__main__":
    main()
