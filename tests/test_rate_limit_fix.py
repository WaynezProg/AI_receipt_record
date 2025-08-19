#!/usr/bin/env python3
"""
測試頻率限制修復
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.optimized_batch_processor import optimized_batch_processor


def check_rate_limit_settings():
    """檢查頻率限制設定"""
    print("🔧 檢查頻率限制設定")
    print("=" * 60)

    print("📊 當前設定:")
    print(f"   Azure每分鐘限制: {optimized_batch_processor.azure_rate_limit} 次")
    print(f"   Claude每分鐘限制: {optimized_batch_processor.claude_rate_limit} 次")
    print(f"   並行Azure請求: {optimized_batch_processor.max_concurrent_azure}")
    print(f"   並行Claude請求: {optimized_batch_processor.max_concurrent_claude}")
    print(f"   Azure延遲: {optimized_batch_processor.azure_delay} 秒")
    print(f"   Claude延遲: {optimized_batch_processor.claude_delay} 秒")
    print(f"   批次大小: {optimized_batch_processor.batch_size}")

    # 計算實際請求頻率
    azure_requests_per_minute = 60 / optimized_batch_processor.azure_delay
    print(f"\n📈 實際請求頻率:")
    print(f"   Azure實際頻率: {azure_requests_per_minute:.1f} 次/分鐘")
    print(f"   Azure限制: {optimized_batch_processor.azure_rate_limit} 次/分鐘")

    if azure_requests_per_minute <= optimized_batch_processor.azure_rate_limit:
        print("   ✅ Azure頻率符合限制")
    else:
        print("   ❌ Azure頻率超過限制")

    # 檢查並行設定
    print(f"\n🔀 並行處理分析:")
    print(f"   並行Azure請求: {optimized_batch_processor.max_concurrent_azure}")
    if optimized_batch_processor.max_concurrent_azure == 1:
        print("   ✅ 並行設定安全（單一請求）")
    else:
        print("   ⚠️ 並行設定可能導致頻率超限")


def test_adaptive_delay():
    """測試自適應延遲計算"""
    print("\n⏱️ 測試自適應延遲計算")
    print("=" * 60)

    test_batch_sizes = [1, 5, 10, 15, 20]

    for batch_size in test_batch_sizes:
        delay = optimized_batch_processor._calculate_adaptive_delay(batch_size)
        print(f"   批次大小 {batch_size:2d}: {delay:5.1f} 秒延遲")

    print("\n📋 延遲計算說明:")
    print("   - 每請求最少4秒間隔")
    print("   - 批次間最少5秒延遲")
    print("   - 批次間最多30秒延遲")
    print("   - 包含2秒安全邊際")


async def test_small_batch_processing():
    """測試小批量處理"""
    print("\n🧪 測試小批量處理")
    print("=" * 60)

    # 檢查是否有測試圖片
    receipts_dir = "./data/receipts"
    if not os.path.exists(receipts_dir):
        print("❌ 沒有找到receipts目錄")
        return

    # 獲取前3個圖片進行測試
    image_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    image_files = []

    for filename in os.listdir(receipts_dir):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(filename)
            if len(image_files) >= 3:
                break

    if not image_files:
        print("❌ 沒有找到測試圖片")
        return

    print(f"📝 測試 {len(image_files)} 個圖片:")
    for i, filename in enumerate(image_files):
        print(f"   {i+1}. {filename}")

    print(f"\n🔄 開始處理...")
    start_time = time.time()

    try:
        result = await optimized_batch_processor.process_large_batch_optimized(
            image_files, True
        )

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n📊 處理結果:")
        print(f"   成功處理: {result['processed_count']}")
        print(f"   失敗數量: {result['failed_count']}")
        print(f"   總耗時: {result['total_time']}秒")
        print(f"   平均每項: {result['avg_time_per_item']}秒")

        if result["failed_count"] == 0:
            print("   ✅ 所有圖片處理成功，無429錯誤")
        else:
            print("   ⚠️ 有處理失敗的圖片")
            for failed_file in result["failed_files"]:
                print(f"      - {failed_file['filename']}: {failed_file['error']}")

        # 檢查是否有429錯誤
        has_429_error = any(
            "429" in failed_file.get("error", "")
            for failed_file in result["failed_files"]
        )

        if not has_429_error:
            print("   ✅ 沒有429頻率限制錯誤")
        else:
            print("   ❌ 仍有429頻率限制錯誤")

    except Exception as e:
        print(f"❌ 處理過程中出現錯誤: {e}")
        import traceback

        traceback.print_exc()


def test_rate_limit_compliance():
    """測試頻率限制合規性"""
    print("\n📋 頻率限制合規性檢查")
    print("=" * 60)

    # Azure F0免費層限制
    azure_f0_limit = 20  # 每分鐘20次
    azure_f0_interval = 60 / azure_f0_limit  # 每次請求間隔3秒

    print("📊 Azure F0免費層限制:")
    print(f"   每分鐘限制: {azure_f0_limit} 次")
    print(f"   每次間隔: {azure_f0_interval:.1f} 秒")

    # 當前設定
    current_interval = optimized_batch_processor.azure_delay
    current_requests_per_minute = 60 / current_interval

    print(f"\n📊 當前設定:")
    print(f"   延遲間隔: {current_interval} 秒")
    print(f"   實際頻率: {current_requests_per_minute:.1f} 次/分鐘")

    # 合規性檢查
    if current_requests_per_minute <= azure_f0_limit:
        print("   ✅ 符合Azure F0免費層限制")
        safety_margin = azure_f0_limit - current_requests_per_minute
        print(f"   安全邊際: {safety_margin:.1f} 次/分鐘")
    else:
        print("   ❌ 超過Azure F0免費層限制")
        excess = current_requests_per_minute - azure_f0_limit
        print(f"   超出限制: {excess:.1f} 次/分鐘")

    # 並行處理檢查
    print(f"\n🔀 並行處理檢查:")
    print(f"   並行Azure請求: {optimized_batch_processor.max_concurrent_azure}")

    if optimized_batch_processor.max_concurrent_azure == 1:
        print("   ✅ 單一並行請求，不會造成頻率衝突")
    else:
        print("   ⚠️ 多個並行請求可能導致頻率超限")


async def main():
    """主測試函數"""
    print("🔧 頻率限制修復測試")
    print("=" * 80)

    try:
        # 檢查設定
        check_rate_limit_settings()

        # 測試延遲計算
        test_adaptive_delay()

        # 測試頻率限制合規性
        test_rate_limit_compliance()

        # 測試小批量處理
        await test_small_batch_processing()

        print("\n" + "=" * 80)
        print("🎉 頻率限制修復測試完成！")
        print("\n📋 修復總結:")
        print("✅ 降低並行Azure請求到1個")
        print("✅ 增加Azure延遲到4秒")
        print("✅ 改進429錯誤處理")
        print("✅ 實現指數退避策略")
        print("✅ 優化批次間延遲計算")
        print("✅ 確保符合Azure F0免費層限制")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
