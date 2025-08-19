#!/usr/bin/env python3
"""
OCR測試腳本
用於測試Azure Computer Vision API的連接和功能
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.utils.image_utils import image_utils


async def test_ocr_service():
    """測試OCR服務"""
    print("🧪 開始測試OCR服務...")

    # 檢查API金鑰
    if not ocr_service.key:
        print("❌ Azure Vision API金鑰未設定")
        print("請在.env檔案中設定AZURE_VISION_KEY")
        return False

    if not ocr_service.endpoint:
        print("❌ Azure Vision API端點未設定")
        print("請在.env檔案中設定AZURE_VISION_ENDPOINT")
        return False

    print("✅ API設定檢查通過")

    # 檢查測試圖片
    test_image_path = "test_receipt.jpg"
    if not os.path.exists(test_image_path):
        print(f"❌ 測試圖片不存在: {test_image_path}")
        print("請將測試收據圖片命名為 test_receipt.jpg 並放在專案根目錄")
        return False

    print(f"✅ 找到測試圖片: {test_image_path}")

    try:
        # 驗證圖片
        if not image_utils.validate_image(test_image_path):
            print("❌ 圖片驗證失敗")
            return False

        print("✅ 圖片驗證通過")

        # 測試OCR
        print("🔄 開始OCR處理...")
        ocr_result = await ocr_service.extract_text(test_image_path)

        print(f"✅ OCR處理完成")
        print(f"   識別文字行數: {len(ocr_result['text_lines'])}")
        print(f"   識別單詞數: {len(ocr_result['words'])}")
        print(f"   信心度: {ocr_result['confidence']:.2f}")
        print(f"   處理時間: {ocr_result['processing_time']:.2f}秒")

        # 顯示識別的文字
        print("\n📝 識別的文字內容:")
        print("-" * 50)
        print(ocr_result["full_text"])
        print("-" * 50)

        # 測試結構化資料提取
        print("\n🔄 提取結構化資料...")
        structured_data = ocr_service.extract_structured_data(ocr_result)

        print(f"✅ 結構化資料提取完成")
        print(f"   數字: {structured_data['numbers']}")
        print(f"   日期: {structured_data['dates']}")
        print(f"   可能的商店名稱: {structured_data['store_names']}")

        return True

    except Exception as e:
        print(f"❌ OCR測試失敗: {str(e)}")
        return False


async def test_ai_service():
    """測試AI服務"""
    print("\n🧪 開始測試AI服務...")

    # 檢查API金鑰
    if not ai_service.api_key:
        print("❌ Claude API金鑰未設定")
        print("請在.env檔案中設定CLAUDE_API_KEY")
        return False

    print("✅ Claude API設定檢查通過")

    # 模擬OCR結果
    mock_ocr_result = {
        "full_text": "セブン-イレブン\n2024年1月15日\nコーヒー 150円\nパン 200円\n合計 350円",
        "confidence": 0.95,
        "source_image": "test_receipt.jpg",
    }

    mock_structured_data = {
        "numbers": [150, 200, 350],
        "dates": ["2024年1月15日"],
        "store_names": ["セブン-イレブン"],
        "full_text": mock_ocr_result["full_text"],
        "confidence": 0.95,
    }

    try:
        print("🔄 開始AI處理...")
        receipt_data = await ai_service.process_receipt_text(
            mock_ocr_result, mock_structured_data
        )

        print(f"✅ AI處理完成")
        print(f"   商店名稱: {receipt_data.store_name}")
        print(f"   日期: {receipt_data.date}")
        print(f"   總金額: {receipt_data.total_amount}")
        print(f"   信心度: {receipt_data.confidence_score}")
        print(f"   處理時間: {receipt_data.processing_time:.2f}秒")

        return True

    except Exception as e:
        print(f"❌ AI測試失敗: {str(e)}")
        return False


async def main():
    """主測試函數"""
    print("🚀 日本收據識別系統 - 測試腳本")
    print("=" * 50)

    # 測試OCR服務
    ocr_success = await test_ocr_service()

    # 測試AI服務
    ai_success = await test_ai_service()

    print("\n" + "=" * 50)
    print("📊 測試結果摘要:")
    print(f"   OCR服務: {'✅ 通過' if ocr_success else '❌ 失敗'}")
    print(f"   AI服務: {'✅ 通過' if ai_success else '❌ 失敗'}")

    if ocr_success and ai_success:
        print("\n🎉 所有測試通過！系統可以正常使用。")
        print("\n📋 下一步:")
        print("   1. 啟動服務: python app/main.py")
        print("   2. 開啟瀏覽器: http://localhost:8000")
        print("   3. 上傳收據圖片進行測試")
    else:
        print("\n⚠️  部分測試失敗，請檢查設定和網路連接。")

    return ocr_success and ai_success


if __name__ == "__main__":
    asyncio.run(main())
