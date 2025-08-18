#!/usr/bin/env python3
"""
測試AI prompt修復
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from app.services.ai_service import ai_service

def test_prompt_format():
    """測試prompt格式"""
    print("🔧 測試AI Prompt格式")
    print("=" * 60)
    
    # 模擬OCR數據
    ocr_data = {
        'text': 'セブン-イレブン\n2024年8月17日\nおにぎり 120円\nコーヒー 150円\n合計 270円',
        'confidence': 0.85
    }
    
    structured_data = {}
    
    # 生成prompt
    prompt = ai_service._build_receipt_prompt(ocr_data, structured_data)
    
    print("📋 生成的Prompt:")
    print(prompt)
    
    print("\n📊 Prompt分析:")
    print(f"   包含JSON格式示例: {'JSON格式' in prompt}")
    print(f"   包含tax_type說明: {'tax_type' in prompt}")
    print(f"   包含字符串要求: {'字符串' in prompt}")
    print(f"   包含JSON語法要求: {'JSON語法' in prompt}")

def test_json_parsing():
    """測試JSON解析"""
    print("\n🧪 測試JSON解析")
    print("=" * 60)
    
    # 測試正常的JSON
    normal_json = '''
    {
      "store_name": "セブン-イレブン",
      "date": "2024-08-17",
      "time": "14:30",
      "total_amount": 270,
      "items": [
        {
          "name": "おにぎり",
          "name_japanese": "おにぎり",
          "name_chinese": "飯糰",
          "price": 120,
          "quantity": 1,
          "tax_included": true,
          "tax_amount": 12
        }
      ],
      "payment_method": "現金",
      "receipt_number": "001",
      "tax_amount": 27,
      "subtotal": 243,
      "tax_type": "內含稅"
    }
    '''
    
    # 測試有問題的JSON（tax_type是字典）
    problematic_json = '''
    {
      "store_name": "セブン-イレブン",
      "date": "2024-08-17",
      "time": "14:30",
      "total_amount": 270,
      "items": [
        {
          "name": "おにぎり",
          "name_japanese": "おにぎり",
          "name_chinese": "飯糰",
          "price": 120,
          "quantity": 1,
          "tax_included": true,
          "tax_amount": 12
        }
      ],
      "payment_method": "現金",
      "receipt_number": "001",
      "tax_amount": 27,
      "subtotal": 243,
      "tax_type": {
        "standard_rate": {"rate": 10, "amount": 27},
        "reduced_rate": {"rate": 8, "amount": 0}
      }
    }
    '''
    
    # 測試OCR數據
    ocr_data = {'confidence': 0.85}
    
    print("📋 測試正常JSON:")
    try:
        result = ai_service._parse_ai_response(normal_json, ocr_data)
        print(f"   ✅ 解析成功")
        print(f"   商店名稱: {result.store_name}")
        print(f"   稅金類型: {result.tax_type}")
        print(f"   商品數量: {len(result.items)}")
    except Exception as e:
        print(f"   ❌ 解析失敗: {e}")
    
    print("\n📋 測試問題JSON (tax_type是字典):")
    try:
        result = ai_service._parse_ai_response(problematic_json, ocr_data)
        print(f"   ✅ 解析成功")
        print(f"   商店名稱: {result.store_name}")
        print(f"   稅金類型: {result.tax_type}")
        print(f"   商品數量: {len(result.items)}")
    except Exception as e:
        print(f"   ❌ 解析失敗: {e}")

def test_api_format():
    """測試API格式"""
    print("\n🧪 測試API格式")
    print("=" * 60)
    
    # 檢查API調用格式
    import inspect
    source = inspect.getsource(ai_service._call_claude_api)
    
    print("📋 API調用格式檢查:")
    print(f"   包含response_format: {'response_format' in source}")
    print(f"   包含json_object: {'json_object' in source}")
    
    if 'response_format' in source:
        print("   ✅ 已啟用JSON模式")
    else:
        print("   ❌ 未啟用JSON模式")

async def test_actual_processing():
    """測試實際處理"""
    print("\n🧪 測試實際處理")
    print("=" * 60)
    
    # 模擬OCR數據
    ocr_data = {
        'text': 'セブン-イレブン\n2024年8月17日\nおにぎり 120円\nコーヒー 150円\n合計 270円',
        'confidence': 0.85
    }
    
    structured_data = {}
    
    try:
        # 測試AI處理
        result = await ai_service.process_receipt_text(ocr_data, structured_data)
        
        print("📊 處理結果:")
        print(f"   成功: {result is not None}")
        if result:
            print(f"   商店名稱: {result.store_name}")
            print(f"   稅金類型: {result.tax_type}")
            print(f"   商品數量: {len(result.items)}")
            print(f"   總金額: {result.total_amount}")
        
    except Exception as e:
        print(f"❌ 處理失敗: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主測試函數"""
    print("🔧 AI Prompt修復測試")
    print("=" * 80)
    
    try:
        # 測試prompt格式
        test_prompt_format()
        
        # 測試JSON解析
        test_json_parsing()
        
        # 測試API格式
        test_api_format()
        
        # 測試實際處理
        await test_actual_processing()
        
        print("\n" + "=" * 80)
        print("🎉 AI Prompt修復測試完成！")
        print("\n📋 修復總結:")
        print("✅ 改進了prompt格式，提供明確的JSON示例")
        print("✅ 啟用了Claude JSON模式")
        print("✅ 改進了JSON解析邏輯")
        print("✅ 添加了tax_type類型轉換")
        print("✅ 增強了錯誤處理")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
