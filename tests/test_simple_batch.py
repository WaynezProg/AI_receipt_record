#!/usr/bin/env python3
"""
簡化的批量處理測試（不增強圖片品質）
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加項目路徑


def test_simple_batch():
    """測試簡化的批量處理"""
    print("🚀 開始簡化批量處理測試...")
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
    
    # 檢查現有的測試圖片
    upload_dir = "./data/receipts"
    test_images = [f for f in os.listdir(upload_dir) if f.startswith('test_33_')]
    
    if len(test_images) < 5:
        print("❌ 測試圖片不足，請先運行 create_better_test_images.py")
        return
    
    # 只測試前5張圖片
    test_images = test_images[:5]
    print(f"📋 使用 {len(test_images)} 張測試圖片: {test_images}")
    
    # 測試批量處理（不增強圖片品質）
    print("\n🔄 測試批量處理（不增強圖片品質）...")
    
    try:
        # 準備請求資料
        data = {
            "filenames": test_images,
            "enhance_image": "false",  # 不增強圖片品質
            "save_detailed_csv": "true"
        }
        
        print(f"   準備處理 {len(test_images)} 個檔案...")
        print(f"   檔案列表: {test_images}")
        
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
            failed_files = result.get('failed_files', [])
            if failed_files:
                print(f"   ❌ 失敗的檔案:")
                for failed in failed_files:
                    print(f"     - {failed.get('filename', 'unknown')}: {failed.get('error', 'unknown error')}")
            
            # 檢查CSV檔案
            csv_files = result.get('csv_files', {})
            if csv_files:
                print(f"   📊 CSV檔案:")
                for file_type, file_path in csv_files.items():
                    print(f"     {file_type}: {os.path.basename(file_path)}")
            
            if result.get('processed_count', 0) == len(test_images):
                print(f"\n🎉 所有 {len(test_images)} 個檔案都成功處理！")
                return True
            else:
                print(f"\n⚠️  有 {len(test_images) - result.get('processed_count', 0)} 個檔案處理失敗")
                return False
        else:
            print(f"   ❌ 批量處理失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 批量處理錯誤: {e}")
        return False

def main():
    """主測試函數"""
    success = test_simple_batch()
    
    print("\n" + "=" * 50)
    print("📊 測試總結:")
    print(f"   簡化批量處理: {'✅ 成功' if success else '❌ 失敗'}")
    
    if success:
        print("\n🎉 簡化批量處理測試通過！")
        print("   問題已解決：檔案名稱重複問題已修復")
        print("   建議：關閉圖片品質增強功能以提高處理速度")
    else:
        print("\n⚠️  簡化批量處理測試失敗")
        print("   需要進一步診斷問題")

if __name__ == "__main__":
    main()
