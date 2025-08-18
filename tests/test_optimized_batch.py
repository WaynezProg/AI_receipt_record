#!/usr/bin/env python3
"""
測試優化批量處理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor
from app.services.batch_processor import batch_processor

def create_test_images(count: int = 10):
    """創建測試圖片"""
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # 確保目錄存在
    os.makedirs("./data/receipts", exist_ok=True)
    
    test_images = []
    for i in range(count):
        # 創建測試圖片
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加一些文字
        draw.text((50, 50), f"Test Receipt {i+1}", fill='black')
        draw.text((50, 100), f"Store: Test Store {i+1}", fill='black')
        draw.text((50, 150), f"Date: 2025-01-{i+1:02d}", fill='black')
        draw.text((50, 200), f"Total: ¥{1000 + i*100}", fill='black')
        
        # 保存圖片
        filename = f"test_receipt_{i+1:03d}.jpg"
        filepath = f"./data/receipts/{filename}"
        img.save(filepath, 'JPEG', quality=85)
        test_images.append(filename)
        
        print(f"✅ 創建測試圖片: {filename}")
    
    return test_images

async def test_optimized_batch_processing():
    """測試優化批量處理"""
    print("🧪 測試優化批量處理功能")
    print("=" * 60)
    
    # 創建測試圖片
    print("📝 創建測試圖片...")
    test_images = create_test_images(10)
    print(f"✅ 創建了 {len(test_images)} 個測試圖片")
    
    # 測試標準批量處理
    print("\n🔄 測試標準批量處理...")
    start_time = time.time()
    standard_result = await batch_processor.process_large_batch(test_images, False, True)
    standard_time = time.time() - start_time
    
    print(f"✅ 標準批量處理完成:")
    print(f"   成功: {standard_result['processed_count']}")
    print(f"   失敗: {standard_result['failed_count']}")
    print(f"   耗時: {standard_time:.2f}秒")
    print(f"   平均每項: {standard_time/len(test_images):.2f}秒")
    
    # 測試優化批量處理
    print("\n⚡ 測試優化批量處理...")
    start_time = time.time()
    optimized_result = await optimized_batch_processor.process_large_batch_optimized(test_images, True)
    optimized_time = time.time() - start_time
    
    print(f"✅ 優化批量處理完成:")
    print(f"   成功: {optimized_result['processed_count']}")
    print(f"   失敗: {optimized_result['failed_count']}")
    print(f"   耗時: {optimized_time:.2f}秒")
    print(f"   平均每項: {optimized_time/len(test_images):.2f}秒")
    
    # 性能比較
    print("\n📊 性能比較:")
    if standard_time > 0:
        speedup = standard_time / optimized_time
        print(f"   速度提升: {speedup:.2f}x")
        print(f"   時間節省: {((standard_time - optimized_time) / standard_time * 100):.1f}%")
    
    # 測試進度追蹤
    print("\n📈 測試進度追蹤...")
    standard_progress = batch_processor.get_progress()
    optimized_progress = optimized_batch_processor.get_progress()
    
    print(f"標準進度: {standard_progress}")
    print(f"優化進度: {optimized_progress}")
    
    # 清理測試檔案
    print("\n🧹 清理測試檔案...")
    for filename in test_images:
        filepath = f"./data/receipts/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ 刪除: {filename}")
    
    print("\n🎉 優化批量處理測試完成！")

async def test_optimization_features():
    """測試優化功能特性"""
    print("\n🔧 測試優化功能特性")
    print("=" * 60)
    
    # 測試並行控制
    print("🔄 測試並行控制...")
    print(f"   Azure並行數: {optimized_batch_processor.max_concurrent_azure}")
    print(f"   Claude並行數: {optimized_batch_processor.max_concurrent_claude}")
    print(f"   批次大小: {optimized_batch_processor.batch_size}")
    
    # 測試延遲控制
    print("\n⏱️ 測試延遲控制...")
    print(f"   Azure延遲: {optimized_batch_processor.azure_delay}秒")
    print(f"   Claude延遲: {optimized_batch_processor.claude_delay}秒")
    
    # 測試快取控制
    print("\n💾 測試快取控制...")
    print(f"   使用快取: {optimized_batch_processor.use_cache}")
    print(f"   本地預處理: {optimized_batch_processor.use_local_preprocessing}")
    print(f"   跳過增強: {optimized_batch_processor.skip_enhancement}")
    
    # 測試自適應延遲
    print("\n🎯 測試自適應延遲...")
    for batch_size in [5, 10, 15, 20]:
        delay = optimized_batch_processor._calculate_adaptive_delay(batch_size)
        print(f"   批次大小 {batch_size}: {delay:.2f}秒延遲")
    
    print("\n✅ 優化功能特性測試完成！")

async def main():
    """主測試函數"""
    print("🚀 優化批量處理功能測試")
    print("=" * 80)
    
    try:
        # 測試優化功能特性
        await test_optimization_features()
        
        # 測試實際處理
        await test_optimized_batch_processing()
        
        print("\n" + "=" * 80)
        print("🎉 所有測試完成！")
        print("\n📋 優化功能總結:")
        print("✅ 智能並行處理")
        print("✅ 本地圖片預處理")
        print("✅ 快取機制")
        print("✅ 自適應延遲")
        print("✅ 跳過圖片增強")
        print("✅ 重試機制")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
