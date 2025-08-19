#!/usr/bin/env python3
"""
診斷CSV錯誤
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor
from app.services.csv_service import csv_service
from app.models.receipt import ReceiptData


def check_data_types():
    """檢查數據類型"""
    print("🔍 檢查數據類型")
    print("=" * 60)

    # 檢查ReceiptData模型
    print("📋 ReceiptData模型:")
    print(f"   類型: {type(ReceiptData)}")
    print(f"   屬性: {dir(ReceiptData)}")

    # 檢查CSV服務
    print(f"\n📋 CSV服務:")
    print(f"   類型: {type(csv_service)}")
    print(
        f"   方法: {[method for method in dir(csv_service) if not method.startswith('_')]}"
    )


async def test_single_processing():
    """測試單個處理"""
    print("\n🧪 測試單個處理")
    print("=" * 60)

    # 檢查是否有測試圖片
    receipts_dir = "./data/receipts"
    if not os.path.exists(receipts_dir):
        print("❌ 沒有找到receipts目錄")
        return

    # 獲取第一個圖片進行測試
    image_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    image_files = []

    for filename in os.listdir(receipts_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(filename)
            break

    if not image_files:
        print("❌ 沒有找到測試圖片")
        return

    filename = image_files[0]
    print(f"📝 測試圖片: {filename}")

    try:
        # 測試單個處理
        result = await optimized_batch_processor._process_single_item_optimized(
            filename
        )

        print(f"\n📊 處理結果:")
        print(f"   成功: {result.get('success')}")
        print(f"   數據類型: {type(result.get('data'))}")

        if result.get("success") and result.get("data"):
            data = result["data"]
            print(f"   數據內容:")
            print(f"     類型: {type(data)}")
            print(f"     屬性: {dir(data)}")

            if hasattr(data, "store_name"):
                print(f"     商店名稱: {data.store_name}")
            else:
                print(f"     ❌ 沒有store_name屬性")
                print(
                    f"     實際屬性: {[attr for attr in dir(data) if not attr.startswith('_')]}"
                )

            # 測試CSV保存
            print(f"\n💾 測試CSV保存:")
            try:
                csv_result = csv_service.save_consolidated_csv([data])
                print(f"   ✅ CSV保存成功: {csv_result}")
            except Exception as e:
                print(f"   ❌ CSV保存失敗: {e}")
                import traceback

                traceback.print_exc()
        else:
            print(f"   錯誤: {result.get('error')}")

    except Exception as e:
        print(f"❌ 處理過程中出現錯誤: {e}")
        import traceback

        traceback.print_exc()


async def test_batch_processing():
    """測試批量處理"""
    print("\n🧪 測試批量處理")
    print("=" * 60)

    # 檢查是否有測試圖片
    receipts_dir = "./data/receipts"
    if not os.path.exists(receipts_dir):
        print("❌ 沒有找到receipts目錄")
        return

    # 獲取前2個圖片進行測試
    image_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
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
        result = await optimized_batch_processor.process_large_batch_optimized(
            image_files, True
        )

        print(f"\n📊 批量處理結果:")
        print(f"   成功: {result.get('success')}")
        print(f"   成功處理: {result['processed_count']}")
        print(f"   失敗數量: {result['failed_count']}")
        print(f"   CSV檔案: {result.get('csv_files')}")

        if result["failed_count"] > 0:
            print(f"   失敗檔案:")
            for failed_file in result["failed_files"]:
                print(f"      - {failed_file['filename']}: {failed_file['error']}")

    except Exception as e:
        print(f"❌ 批量處理過程中出現錯誤: {e}")
        import traceback

        traceback.print_exc()


def test_csv_service():
    """測試CSV服務"""
    print("\n🧪 測試CSV服務")
    print("=" * 60)

    # 創建測試數據
    from app.models.receipt import ReceiptItem
    from datetime import datetime

    test_item = ReceiptItem(
        name="測試商品",
        name_japanese="テスト商品",
        name_chinese="測試商品",
        price=100.0,
        quantity=1,
        tax_included=True,
        tax_amount=10.0,
    )

    test_receipt = ReceiptData(
        store_name="測試商店",
        date=datetime.now(),
        total_amount=110.0,
        items=[test_item],
        source_image="test.jpg",
        confidence_score=0.9,
        processing_time=1.0,
    )

    print(f"📋 測試數據:")
    print(f"   類型: {type(test_receipt)}")
    print(f"   商店名稱: {test_receipt.store_name}")
    print(f"   商品數量: {len(test_receipt.items)}")

    try:
        # 測試CSV保存
        csv_result = csv_service.save_consolidated_csv([test_receipt])
        print(f"   ✅ CSV保存成功: {csv_result}")
    except Exception as e:
        print(f"   ❌ CSV保存失敗: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """主測試函數"""
    print("🔧 CSV錯誤診斷")
    print("=" * 80)

    try:
        # 檢查數據類型
        check_data_types()

        # 測試CSV服務
        test_csv_service()

        # 測試單個處理
        await test_single_processing()

        # 測試批量處理
        await test_batch_processing()

        print("\n" + "=" * 80)
        print("🎉 CSV錯誤診斷完成！")

    except Exception as e:
        print(f"❌ 診斷失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
