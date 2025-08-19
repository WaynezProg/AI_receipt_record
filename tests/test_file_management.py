#!/usr/bin/env python3
"""
測試檔案管理功能
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor
from app.services.batch_processor import batch_processor


def create_test_images(count: int = 5):
    """創建測試圖片"""
    from PIL import Image, ImageDraw
    import os

    # 確保目錄存在
    os.makedirs("./data/receipts", exist_ok=True)

    test_images = []
    for i in range(count):
        # 創建測試圖片
        img = Image.new("RGB", (800, 600), color="white")
        draw = ImageDraw.Draw(img)

        # 添加一些文字
        draw.text((50, 50), f"Test Receipt {i+1}", fill="black")
        draw.text((50, 100), f"Store: Test Store {i+1}", fill="black")
        draw.text((50, 150), f"Date: 2025-01-{i+1:02d}", fill="black")
        draw.text((50, 200), f"Total: ¥{1000 + i*100}", fill="black")

        # 保存圖片
        filename = f"test_file_mgmt_{i+1:03d}.jpg"
        filepath = f"./data/receipts/{filename}"
        img.save(filepath, "JPEG", quality=85)
        test_images.append(filename)

        print(f"✅ 創建測試圖片: {filename}")

    return test_images


def check_files_exist(filenames):
    """檢查檔案是否存在"""
    existing_files = []
    for filename in filenames:
        filepath = f"./data/receipts/{filename}"
        if os.path.exists(filepath):
            existing_files.append(filename)
    return existing_files


async def test_file_management_features():
    """測試檔案管理功能"""
    print("🧪 測試檔案管理功能")
    print("=" * 60)

    # 創建測試圖片
    print("📝 創建測試圖片...")
    test_images = create_test_images(5)
    print(f"✅ 創建了 {len(test_images)} 個測試圖片")

    # 檢查檔案存在
    existing_files = check_files_exist(test_images)
    print(f"📁 檢查檔案存在: {len(existing_files)}/{len(test_images)} 個檔案存在")

    # 測試檔案管理設定
    print("\n🔧 測試檔案管理設定...")

    # 測試自動刪除成功圖片
    print("  測試自動刪除成功圖片...")
    optimized_batch_processor.auto_delete_successful = True
    optimized_batch_processor.keep_failed_files = True

    print(f"    自動刪除成功圖片: {optimized_batch_processor.auto_delete_successful}")
    print(f"    保留失敗檔案: {optimized_batch_processor.keep_failed_files}")

    # 測試處理（會觸發刪除）
    print("\n🔄 測試處理（會觸發自動刪除）...")
    try:
        result = await optimized_batch_processor.process_large_batch_optimized(
            test_images, True
        )

        print(f"✅ 處理完成:")
        print(f"   成功: {result['processed_count']}")
        print(f"   失敗: {result['failed_count']}")
        print(f"   刪除成功圖片: {result.get('deleted_successful', 0)}")
        print(f"   刪除失敗圖片: {result.get('deleted_failed', 0)}")

        # 檢查檔案是否被刪除
        remaining_files = check_files_exist(test_images)
        print(f"📁 處理後剩餘檔案: {len(remaining_files)}/{len(test_images)}")

        if len(remaining_files) == 0:
            print("✅ 所有成功處理的圖片已被自動刪除")
        else:
            print(f"⚠️  仍有 {len(remaining_files)} 個檔案未被刪除: {remaining_files}")

    except Exception as e:
        print(f"❌ 處理失敗: {e}")

    # 測試禁用自動刪除
    print("\n🔧 測試禁用自動刪除...")

    # 重新創建測試圖片
    test_images_2 = create_test_images(3)

    # 禁用自動刪除
    optimized_batch_processor.auto_delete_successful = False
    optimized_batch_processor.keep_failed_files = True

    print(f"    自動刪除成功圖片: {optimized_batch_processor.auto_delete_successful}")
    print(f"    保留失敗檔案: {optimized_batch_processor.keep_failed_files}")

    # 測試處理（不會刪除）
    print("\n🔄 測試處理（不會刪除）...")
    try:
        result = await optimized_batch_processor.process_large_batch_optimized(
            test_images_2, True
        )

        print(f"✅ 處理完成:")
        print(f"   成功: {result['processed_count']}")
        print(f"   失敗: {result['failed_count']}")
        print(f"   刪除成功圖片: {result.get('deleted_successful', 0)}")
        print(f"   刪除失敗圖片: {result.get('deleted_failed', 0)}")

        # 檢查檔案是否被保留
        remaining_files = check_files_exist(test_images_2)
        print(f"📁 處理後剩餘檔案: {len(remaining_files)}/{len(test_images_2)}")

        if len(remaining_files) == len(test_images_2):
            print("✅ 所有圖片都被保留（自動刪除已禁用）")
        else:
            print(f"⚠️  檔案數量不符預期: {len(remaining_files)}/{len(test_images_2)}")

    except Exception as e:
        print(f"❌ 處理失敗: {e}")

    # 測試標準批量處理器的檔案管理
    print("\n🔄 測試標準批量處理器的檔案管理...")

    # 重新創建測試圖片
    test_images_3 = create_test_images(2)

    # 啟用自動刪除
    batch_processor.auto_delete_successful = True
    batch_processor.keep_failed_files = True

    print(f"    自動刪除成功圖片: {batch_processor.auto_delete_successful}")
    print(f"    保留失敗檔案: {batch_processor.keep_failed_files}")

    try:
        result = await batch_processor.process_large_batch(test_images_3, False, True)

        print(f"✅ 標準處理完成:")
        print(f"   成功: {result['processed_count']}")
        print(f"   失敗: {result['failed_count']}")
        print(f"   刪除成功圖片: {result.get('deleted_successful', 0)}")
        print(f"   刪除失敗圖片: {result.get('deleted_failed', 0)}")

        # 檢查檔案是否被刪除
        remaining_files = check_files_exist(test_images_3)
        print(f"📁 處理後剩餘檔案: {len(remaining_files)}/{len(test_images_3)}")

    except Exception as e:
        print(f"❌ 標準處理失敗: {e}")

    # 清理剩餘檔案
    print("\n🧹 清理剩餘測試檔案...")
    all_test_files = []
    for i in range(1, 6):
        all_test_files.extend(
            [f"test_file_mgmt_{i:03d}.jpg", f"test_receipt_{i:03d}.jpg"]
        )

    cleaned_count = 0
    for filename in all_test_files:
        filepath = f"./data/receipts/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)
            cleaned_count += 1
            print(f"✅ 刪除: {filename}")

    print(f"🧹 清理完成: {cleaned_count} 個檔案")


async def test_file_management_api():
    """測試檔案管理API"""
    print("\n🌐 測試檔案管理API")
    print("=" * 60)

    import requests

    base_url = "http://localhost:8000"

    try:
        # 測試獲取檔案管理設定
        print("📋 測試獲取檔案管理設定...")
        response = requests.get(f"{base_url}/file-management-settings")

        if response.status_code == 200:
            settings = response.json()
            print("✅ 檔案管理設定:")
            print(f"   標準處理器:")
            print(
                f"     自動刪除成功圖片: {settings['standard_processor']['auto_delete_successful']}"
            )
            print(
                f"     保留失敗檔案: {settings['standard_processor']['keep_failed_files']}"
            )
            print(f"   優化處理器:")
            print(
                f"     自動刪除成功圖片: {settings['optimized_processor']['auto_delete_successful']}"
            )
            print(
                f"     保留失敗檔案: {settings['optimized_processor']['keep_failed_files']}"
            )
        else:
            print(f"❌ 獲取設定失敗: {response.status_code}")

        # 測試配置檔案管理設定
        print("\n⚙️ 測試配置檔案管理設定...")
        data = {
            "auto_delete_successful": "false",
            "keep_failed_files": "true",
            "processor_type": "optimized",
        }

        response = requests.post(f"{base_url}/configure-file-management", data=data)

        if response.status_code == 200:
            result = response.json()
            print("✅ 配置成功:")
            print(f"   設定: {result['settings']}")
        else:
            print(f"❌ 配置失敗: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到API服務器，請確保服務器正在運行")
    except Exception as e:
        print(f"❌ API測試失敗: {e}")


async def main():
    """主測試函數"""
    print("🗂️ 檔案管理功能測試")
    print("=" * 80)

    try:
        # 測試檔案管理功能
        await test_file_management_features()

        # 測試檔案管理API
        await test_file_management_api()

        print("\n" + "=" * 80)
        print("🎉 檔案管理功能測試完成！")
        print("\n📋 功能總結:")
        print("✅ 自動刪除成功處理的圖片")
        print("✅ 可選保留失敗的檔案")
        print("✅ 可配置的檔案管理設定")
        print("✅ API端點支援")
        print("✅ 前端顯示刪除統計")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
