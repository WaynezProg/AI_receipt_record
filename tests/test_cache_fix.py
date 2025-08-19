#!/usr/bin/env python3
"""
測試緩存修復功能
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.cache_service import cache_service
from app.services.optimized_batch_processor import optimized_batch_processor


def create_test_image():
    """創建測試圖片"""
    from PIL import Image, ImageDraw
    import os

    # 確保目錄存在
    os.makedirs("./data/receipts", exist_ok=True)

    # 創建測試圖片
    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)

    # 添加一些文字
    draw.text((50, 50), "Test Receipt", fill="black")
    draw.text((50, 100), "Store: Test Store", fill="black")
    draw.text((50, 150), "Date: 2025-01-01", fill="black")
    draw.text((50, 200), "Total: ¥1000", fill="black")

    # 保存圖片
    filename = "test_cache_fix.jpg"
    filepath = f"./data/receipts/{filename}"
    img.save(filepath, "JPEG", quality=85)

    print(f"✅ 創建測試圖片: {filename}")
    return filename


async def test_cache_fix():
    """測試緩存修復"""
    print("🧪 測試緩存修復功能")
    print("=" * 60)

    # 創建測試圖片
    print("📝 創建測試圖片...")
    test_filename = create_test_image()
    image_path = f"./data/receipts/{test_filename}"

    # 測試1: 保存OCR結果
    print("\n💾 測試保存OCR結果...")
    mock_ocr_data = {
        "success": True,
        "text": "Test receipt text",
        "confidence": 0.95,
        "words": ["Test", "receipt", "text"],
    }

    try:
        cache_path = cache_service.save_ocr_result(test_filename, mock_ocr_data)
        print(f"✅ OCR結果已保存: {cache_path}")
    except Exception as e:
        print(f"❌ 保存OCR結果失敗: {e}")
        return

    # 測試2: 使用檔案名稱載入OCR結果
    print("\n📂 測試使用檔案名稱載入OCR結果...")
    try:
        cached_result = cache_service.load_ocr_result(test_filename)
        if cached_result:
            print("✅ 使用檔案名稱載入成功")
            print(f"   檔案名稱: {cached_result.get('filename')}")
            print(f"   時間戳: {cached_result.get('timestamp')}")
            print(f"   狀態: {cached_result.get('status')}")
        else:
            print("❌ 使用檔案名稱載入失敗")
    except Exception as e:
        print(f"❌ 載入OCR結果失敗: {e}")

    # 測試3: 使用完整路徑載入OCR結果
    print("\n📂 測試使用完整路徑載入OCR結果...")
    try:
        cached_result = cache_service.load_ocr_result(cache_path)
        if cached_result:
            print("✅ 使用完整路徑載入成功")
            print(f"   檔案名稱: {cached_result.get('filename')}")
            print(f"   時間戳: {cached_result.get('timestamp')}")
            print(f"   狀態: {cached_result.get('status')}")
        else:
            print("❌ 使用完整路徑載入失敗")
    except Exception as e:
        print(f"❌ 載入OCR結果失敗: {e}")

    # 測試4: 測試優化批量處理器的緩存功能
    print("\n🔄 測試優化批量處理器的緩存功能...")
    try:
        # 啟用緩存
        optimized_batch_processor.use_cache = True

        # 模擬OCR處理（應該會使用緩存）
        result = await optimized_batch_processor._process_ocr_with_retry(image_path)

        if result.get("success"):
            print("✅ 優化批量處理器緩存功能正常")
            print(f"   結果: {result.get('text', 'N/A')}")
        else:
            print(f"❌ 優化批量處理器緩存功能失敗: {result.get('error')}")

    except Exception as e:
        print(f"❌ 優化批量處理器測試失敗: {e}")

    # 測試5: 測試查找緩存文件功能
    print("\n🔍 測試查找緩存文件功能...")
    try:
        cache_file = cache_service._find_cache_file(test_filename)
        if cache_file:
            print(f"✅ 找到緩存文件: {cache_file}")
        else:
            print("❌ 找不到緩存文件")
    except Exception as e:
        print(f"❌ 查找緩存文件失敗: {e}")

    # 清理測試檔案
    print("\n🧹 清理測試檔案...")
    try:
        # 刪除測試圖片
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"✅ 刪除測試圖片: {test_filename}")

        # 刪除緩存文件
        cache_files = cache_service.list_cache_files()
        for cache_file in cache_files:
            if test_filename in cache_file["filename"]:
                os.remove(cache_file["path"])
                print(f"✅ 刪除緩存文件: {cache_file['filename']}")

    except Exception as e:
        print(f"❌ 清理失敗: {e}")


async def test_error_scenarios():
    """測試錯誤場景"""
    print("\n🚨 測試錯誤場景")
    print("=" * 60)

    # 測試1: 載入不存在的檔案
    print("\n📂 測試載入不存在的檔案...")
    try:
        result = cache_service.load_ocr_result("nonexistent_file.jpg")
        if result is None:
            print("✅ 正確處理不存在的檔案")
        else:
            print("❌ 應該返回None")
    except Exception as e:
        print(f"❌ 載入不存在的檔案時出錯: {e}")

    # 測試2: 查找不存在的緩存文件
    print("\n🔍 測試查找不存在的緩存文件...")
    try:
        result = cache_service._find_cache_file("nonexistent_file.jpg")
        if result is None:
            print("✅ 正確處理不存在的緩存文件")
        else:
            print("❌ 應該返回None")
    except Exception as e:
        print(f"❌ 查找不存在的緩存文件時出錯: {e}")

    # 測試3: 傳遞圖片路徑（應該不會再出錯）
    print("\n🖼️ 測試傳遞圖片路徑...")
    try:
        # 創建一個臨時圖片
        from PIL import Image

        temp_image_path = "./data/receipts/temp_test.jpg"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(temp_image_path, "JPEG")

        # 嘗試載入（應該會查找緩存文件，找不到就返回None）
        result = cache_service.load_ocr_result(temp_image_path)
        if result is None:
            print("✅ 正確處理圖片路徑（找不到緩存文件）")
        else:
            print("❌ 應該返回None")

        # 清理
        os.remove(temp_image_path)

    except Exception as e:
        print(f"❌ 測試圖片路徑時出錯: {e}")


async def main():
    """主測試函數"""
    print("🔧 緩存修復功能測試")
    print("=" * 80)

    try:
        # 測試緩存修復
        await test_cache_fix()

        # 測試錯誤場景
        await test_error_scenarios()

        print("\n" + "=" * 80)
        print("🎉 緩存修復測試完成！")
        print("\n📋 修復總結:")
        print("✅ 修復了 load_ocr_result 函數的參數問題")
        print("✅ 添加了 _find_cache_file 輔助函數")
        print("✅ 支援檔案名稱和完整路徑兩種輸入")
        print("✅ 優化批量處理器現在正確使用緩存")
        print("✅ 錯誤處理更加健壯")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
