#!/usr/bin/env python3
"""
診斷33個圖片處理問題
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor

def check_image_files():
    """檢查圖片檔案"""
    print("🔍 檢查圖片檔案")
    print("=" * 60)
    
    # 檢查receipts目錄
    receipts_dir = "./data/receipts"
    if not os.path.exists(receipts_dir):
        print(f"❌ 目錄不存在: {receipts_dir}")
        return []
    
    # 獲取所有圖片檔案
    image_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    image_files = []
    
    for filename in os.listdir(receipts_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(filename)
    
    print(f"📁 找到 {len(image_files)} 個圖片檔案")
    
    # 顯示前10個檔案
    print("📋 前10個圖片檔案:")
    for i, filename in enumerate(image_files[:10]):
        filepath = os.path.join(receipts_dir, filename)
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"   {i+1:2d}. {filename} ({file_size:.2f}MB)")
    
    if len(image_files) > 10:
        print(f"   ... 還有 {len(image_files) - 10} 個檔案")
    
    return image_files

async def test_processing_debug():
    """測試處理並診斷問題"""
    print("\n🧪 測試處理並診斷問題")
    print("=" * 60)
    
    # 獲取圖片檔案
    image_files = check_image_files()
    if not image_files:
        print("❌ 沒有找到圖片檔案")
        return
    
    print(f"\n🔄 開始處理 {len(image_files)} 個圖片...")
    
    # 記錄處理開始時間
    start_time = time.time()
    
    try:
        # 使用優化批量處理器
        result = await optimized_batch_processor.process_large_batch_optimized(image_files, True)
        
        # 記錄處理結束時間
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📊 處理結果:")
        print(f"   成功處理: {result['processed_count']}")
        print(f"   失敗數量: {result['failed_count']}")
        print(f"   總耗時: {result['total_time']}秒")
        print(f"   平均每項: {result['avg_time_per_item']}秒")
        
        # 顯示失敗的檔案
        if result['failed_files']:
            print(f"\n❌ 失敗的檔案:")
            for failed_file in result['failed_files']:
                print(f"   - {failed_file['filename']}: {failed_file['error']}")
        
        # 分析問題
        print(f"\n🔍 問題分析:")
        print(f"   總檔案數: {len(image_files)}")
        print(f"   成功處理: {result['processed_count']}")
        print(f"   失敗處理: {result['failed_count']}")
        print(f"   處理率: {(result['processed_count'] / len(image_files) * 100):.1f}%")
        
        if result['processed_count'] < len(image_files):
            print(f"\n⚠️  問題診斷:")
            print(f"   - 有 {len(image_files) - result['processed_count']} 個檔案未被處理")
            print(f"   - 可能原因:")
            print(f"     1. 檔案格式不支援")
            print(f"     2. 檔案損壞")
            print(f"     3. 檔案大小超過限制")
            print(f"     4. API限制或網路問題")
            print(f"     5. 處理過程中出現錯誤")
        
        # 檢查CSV輸出
        if result.get('csv_files'):
            print(f"\n📄 CSV檔案:")
            for csv_type, csv_path in result['csv_files'].items():
                if os.path.exists(csv_path):
                    file_size = os.path.getsize(csv_path) / 1024  # KB
                    print(f"   {csv_type}: {csv_path} ({file_size:.1f}KB)")
                else:
                    print(f"   {csv_type}: {csv_path} (檔案不存在)")
        
    except Exception as e:
        print(f"❌ 處理過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

async def test_individual_files():
    """測試個別檔案處理"""
    print("\n🔍 測試個別檔案處理")
    print("=" * 60)
    
    # 獲取圖片檔案
    image_files = check_image_files()
    if not image_files:
        return
    
    # 測試前5個檔案
    test_files = image_files[:5]
    print(f"🧪 測試前 {len(test_files)} 個檔案:")
    
    for i, filename in enumerate(test_files):
        print(f"\n📝 測試檔案 {i+1}: {filename}")
        
        try:
            # 測試單個檔案處理
            result = await optimized_batch_processor._process_single_item_optimized(filename)
            
            if result.get('success'):
                print(f"   ✅ 處理成功")
                data = result.get('data')
                if data:
                    print(f"   商店: {data.store_name}")
                    print(f"   日期: {data.date}")
                    print(f"   總金額: {data.total_amount}")
                    print(f"   商品數量: {len(data.items)}")
            else:
                print(f"   ❌ 處理失敗: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ 處理異常: {e}")

async def main():
    """主測試函數"""
    print("🔧 33個圖片處理問題診斷")
    print("=" * 80)
    
    try:
        # 檢查檔案
        image_files = check_image_files()
        
        if not image_files:
            print("❌ 沒有找到圖片檔案，請先上傳圖片")
            return
        
        # 測試個別檔案
        await test_individual_files()
        
        # 測試批量處理
        await test_processing_debug()
        
        print("\n" + "=" * 80)
        print("🎉 診斷完成！")
        
    except Exception as e:
        print(f"❌ 診斷失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
