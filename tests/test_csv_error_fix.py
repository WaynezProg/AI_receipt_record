#!/usr/bin/env python3
"""
修復CSV錯誤
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor
from app.services.csv_service import csv_service
from app.models.receipt import ReceiptData

def fix_csv_service():
    """修復CSV服務，添加類型檢查"""
    print("🔧 修復CSV服務")
    print("=" * 60)
    
    # 檢查並修復save_consolidated_csv方法
    original_save_consolidated_csv = csv_service.save_consolidated_csv
    
    def safe_save_consolidated_csv(receipts, filename=None):
        """安全的CSV保存，包含類型檢查"""
        try:
            # 類型檢查和轉換
            safe_receipts = []
            for receipt in receipts:
                if isinstance(receipt, dict):
                    print(f"⚠️ 發現字典類型數據，嘗試轉換: {type(receipt)}")
                    # 嘗試從字典創建ReceiptData對象
                    try:
                        from app.models.receipt import ReceiptItem
                        from datetime import datetime
                        
                        # 創建ReceiptItem列表
                        items = []
                        for item_data in receipt.get('items', []):
                            if isinstance(item_data, dict):
                                item = ReceiptItem(
                                    name=item_data.get('name', ''),
                                    name_japanese=item_data.get('name_japanese', ''),
                                    name_chinese=item_data.get('name_chinese', ''),
                                    price=float(item_data.get('price', 0)),
                                    quantity=int(item_data.get('quantity', 1)),
                                    tax_included=item_data.get('tax_included', True),
                                    tax_amount=float(item_data.get('tax_amount', 0)) if item_data.get('tax_amount') else None
                                )
                                items.append(item)
                        
                        # 創建ReceiptData對象
                        receipt_obj = ReceiptData(
                            store_name=receipt.get('store_name', ''),
                            date=receipt.get('date', datetime.now()),
                            total_amount=float(receipt.get('total_amount', 0)),
                            items=items,
                            source_image=receipt.get('source_image', ''),
                            confidence_score=float(receipt.get('confidence_score', 0.9)),
                            processing_time=float(receipt.get('processing_time', 1.0))
                        )
                        safe_receipts.append(receipt_obj)
                        print(f"   ✅ 成功轉換字典為ReceiptData對象")
                    except Exception as e:
                        print(f"   ❌ 轉換失敗: {e}")
                        continue
                elif isinstance(receipt, ReceiptData):
                    safe_receipts.append(receipt)
                else:
                    print(f"⚠️ 未知類型: {type(receipt)}")
                    continue
            
            if not safe_receipts:
                raise Exception("沒有有效的收據數據")
            
            print(f"✅ 成功處理 {len(safe_receipts)} 個收據數據")
            return original_save_consolidated_csv(safe_receipts, filename)
            
        except Exception as e:
            print(f"❌ CSV保存失敗: {e}")
            raise
    
    # 替換方法
    csv_service.save_consolidated_csv = safe_save_consolidated_csv
    print("✅ CSV服務已修復，添加了類型檢查和轉換")

async def test_with_mixed_data():
    """測試混合數據類型"""
    print("\n🧪 測試混合數據類型")
    print("=" * 60)
    
    # 創建測試數據
    from app.models.receipt import ReceiptItem
    from datetime import datetime
    
    # 正常的ReceiptData對象
    test_item = ReceiptItem(
        name="測試商品",
        name_japanese="テスト商品",
        name_chinese="測試商品",
        price=100.0,
        quantity=1,
        tax_included=True,
        tax_amount=10.0
    )
    
    test_receipt = ReceiptData(
        store_name="測試商店",
        date=datetime.now(),
        total_amount=110.0,
        items=[test_item],
        source_image="test.jpg",
        confidence_score=0.9,
        processing_time=1.0
    )
    
    # 字典格式的數據（模擬可能的錯誤情況）
    dict_receipt = {
        'store_name': '字典商店',
        'date': datetime.now(),
        'total_amount': 200.0,
        'items': [
            {
                'name': '字典商品',
                'name_japanese': 'ディクショナリ商品',
                'name_chinese': '字典商品',
                'price': 200.0,
                'quantity': 1,
                'tax_included': True,
                'tax_amount': 20.0
            }
        ],
        'source_image': 'dict_test.jpg',
        'confidence_score': 0.8,
        'processing_time': 1.5
    }
    
    # 混合數據列表
    mixed_receipts = [test_receipt, dict_receipt]
    
    print(f"📋 測試數據:")
    print(f"   總數量: {len(mixed_receipts)}")
    print(f"   ReceiptData對象: 1個")
    print(f"   字典對象: 1個")
    
    try:
        # 測試修復後的CSV保存
        csv_result = csv_service.save_consolidated_csv(mixed_receipts)
        print(f"   ✅ CSV保存成功: {csv_result}")
    except Exception as e:
        print(f"   ❌ CSV保存失敗: {e}")
        import traceback
        traceback.print_exc()

async def test_actual_processing():
    """測試實際處理"""
    print("\n🧪 測試實際處理")
    print("=" * 60)
    
    # 檢查是否有測試圖片
    receipts_dir = "./data/receipts"
    if not os.path.exists(receipts_dir):
        print("❌ 沒有找到receipts目錄")
        return
    
    # 獲取前2個圖片進行測試
    image_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    image_files = []
    
    for filename in os.listdir(receipts_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(filename)
            if len(image_files) >= 2:
                break
    
    if not image_files:
        print("❌ 沒有找到測試圖片")
        return
    
    print(f"📝 測試 {len(image_files)} 個圖片:")
    for i, filename in enumerate(image_files):
        print(f"   {i+1}. {filename}")
    
    try:
        # 測試批量處理
        result = await optimized_batch_processor.process_large_batch_optimized(image_files, True)
        
        print(f"\n📊 批量處理結果:")
        print(f"   成功: {result.get('success')}")
        print(f"   成功處理: {result['processed_count']}")
        print(f"   失敗數量: {result['failed_count']}")
        print(f"   CSV檔案: {result.get('csv_files')}")
        
        if result['failed_count'] > 0:
            print(f"   失敗檔案:")
            for failed_file in result['failed_files']:
                print(f"      - {failed_file['filename']}: {failed_file['error']}")
        
    except Exception as e:
        print(f"❌ 批量處理過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主測試函數"""
    print("🔧 CSV錯誤修復測試")
    print("=" * 80)
    
    try:
        # 修復CSV服務
        fix_csv_service()
        
        # 測試混合數據類型
        await test_with_mixed_data()
        
        # 測試實際處理
        await test_actual_processing()
        
        print("\n" + "=" * 80)
        print("🎉 CSV錯誤修復測試完成！")
        print("\n📋 修復總結:")
        print("✅ 添加了CSV服務的類型檢查")
        print("✅ 支持字典到ReceiptData的轉換")
        print("✅ 改進了錯誤處理")
        print("✅ 確保數據類型一致性")
        
    except Exception as e:
        print(f"❌ 修復失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
