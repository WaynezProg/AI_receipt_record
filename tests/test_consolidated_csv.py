#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
測試整合CSV功能
"""

import os
import sys
import requests
import json
from datetime import datetime

# 添加項目路徑


from app.models.receipt import ReceiptData, ReceiptItem
from app.services.csv_service import CSVService

def test_consolidated_csv():
    """測試整合CSV功能"""
    print("🔍 測試整合CSV功能...")
    
    # 創建測試收據數據
    receipts = []
    
    # 收據1：便利商店
    items1 = [
        ReceiptItem(
            name="おにぎり", 
            name_japanese="おにぎり",
            name_chinese="飯糰",
            price=120.0, 
            quantity=1
        ),
        ReceiptItem(
            name="コーヒー", 
            name_japanese="コーヒー",
            name_chinese="咖啡",
            price=150.0, 
            quantity=1
        )
    ]
    
    receipt1 = ReceiptData(
        store_name="セブン-イレブン",
        date=datetime.now(),
        total_amount=270.0,
        items=items1,
        payment_method="現金",
        receipt_number="CVS001",
        confidence_score=0.9,
        processing_time=1.5,
        source_image="receipt1.jpg"
    )
    receipts.append(receipt1)
    
    # 收據2：餐廳
    items2 = [
        ReceiptItem(
            name="ラーメン", 
            name_japanese="ラーメン",
            name_chinese="拉麵",
            price=800.0, 
            quantity=1
        ),
        ReceiptItem(
            name="餃子", 
            name_japanese="餃子",
            name_chinese="餃子",
            price=300.0, 
            quantity=1
        ),
        ReceiptItem(
            name="ビール", 
            name_japanese="ビール",
            name_chinese="啤酒",
            price=400.0, 
            quantity=1
        )
    ]
    
    receipt2 = ReceiptData(
        store_name="ラーメン店",
        date=datetime.now(),
        total_amount=1500.0,
        items=items2,
        payment_method="信用卡",
        receipt_number="REST001",
        confidence_score=0.95,
        processing_time=2.0,
        source_image="receipt2.jpg"
    )
    receipts.append(receipt2)
    
    print("✅ 測試數據創建完成")
    print(f"   收據數量: {len(receipts)}")
    print(f"   總商品數量: {sum(len(r.items) for r in receipts)}")
    
    # 創建CSV服務
    csv_service = CSVService()
    
    # 測試整合CSV創建
    try:
        csv_files = csv_service.save_consolidated_csv(receipts, "test_consolidated.csv")
        print(f"✅ 整合CSV創建成功")
        print(f"   收據摘要: {csv_files['summary_csv']}")
        print(f"   商品明細: {csv_files['details_csv']}")
        
        # 檢查檔案內容
        for file_type, file_path in csv_files.items():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    print(f"\n📋 {file_type} 檔案內容預覽 ({len(lines)} 行):")
                    for i, line in enumerate(lines[:5]):  # 顯示前5行
                        print(f"   {i+1}: {line}")
                    if len(lines) > 5:
                        print(f"   ... 還有 {len(lines) - 5} 行")
        
        return True
    except Exception as e:
        print(f"❌ 整合CSV創建失敗: {e}")
        return False

def test_download_api():
    """測試下載API"""
    print("\n🔍 測試下載API...")
    
    try:
        # 檢查系統健康狀態
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 系統健康檢查正常")
        else:
            print(f"❌ 系統健康檢查失敗: {response.status_code}")
            return False
        
        # 檢查輸出目錄中的CSV檔案
        output_dir = "./data/output"
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print("❌ 沒有找到CSV檔案")
            return False
        
        # 測試下載第一個CSV檔案
        test_file = csv_files[0]
        print(f"📥 測試下載: {test_file}")
        
        response = requests.get(f"http://localhost:8000/download/{test_file}")
        
        if response.status_code == 200:
            print("✅ 下載API正常")
            print(f"   檔案大小: {len(response.content)} bytes")
            print(f"   內容類型: {response.headers.get('Content-Type', 'unknown')}")
        else:
            print(f"❌ 下載API失敗: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 下載API測試失敗: {e}")
        return False

def show_csv_format_info():
    """顯示CSV格式說明"""
    print("\n📋 整合CSV格式說明:")
    print("=" * 50)
    print("🔹 收據摘要CSV (receipts_summary_*.csv):")
    print("   欄位: 商店名稱, 日期, 總金額, 小計, 稅額, 稅率, 收據號碼, 付款方式, 識別信心度, 處理時間, 來源圖片")
    print("   用途: 每個收據一行，顯示基本資訊")
    
    print("\n🔹 商品明細CSV (receipts_details_*.csv):")
    print("   欄位: 收據來源, 商店名稱, 收據日期, 商品名稱（原始）, 商品名稱（日文）, 商品名稱（中文）, 單價, 數量, 小計")
    print("   用途: 每個商品一行，包含翻譯資訊")
    
    print("\n🔹 整合功能特點:")
    print("   1. 批量處理後自動生成")
    print("   2. 包含所有成功處理的收據")
    print("   3. 支援日文翻譯")
    print("   4. 提供下載連結")
    print("   5. 統一時間戳命名")

def cleanup_test_files():
    """清理測試檔案"""
    print("\n🔍 清理測試檔案...")
    
    output_dir = "./data/output"
    test_files = [f for f in os.listdir(output_dir) if f.startswith('test_consolidated')]
    
    for file in test_files:
        file_path = os.path.join(output_dir, file)
        try:
            os.remove(file_path)
            print(f"   ✅ 刪除: {file}")
        except Exception as e:
            print(f"   ❌ 刪除失敗: {file} - {e}")

def main():
    """主測試函數"""
    print("🚀 開始測試整合CSV功能...")
    print("=" * 50)
    
    # 測試各個功能
    consolidated_ok = test_consolidated_csv()
    download_api_ok = test_download_api()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   整合CSV: {'✅ 通過' if consolidated_ok else '❌ 失敗'}")
    print(f"   下載API: {'✅ 通過' if download_api_ok else '❌ 失敗'}")
    
    if all([consolidated_ok, download_api_ok]):
        print("\n🎉 所有測試通過！整合CSV功能正常運作！")
        print("\n📝 已實現功能:")
        print("   1. ✅ 收據摘要CSV")
        print("   2. ✅ 商品明細CSV")
        print("   3. ✅ 日文翻譯支援")
        print("   4. ✅ 批量整合")
        print("   5. ✅ 下載API")
        print("   6. ✅ 前端下載連結")
        
        show_csv_format_info()
    else:
        print("\n⚠️  部分測試失敗，請檢查系統狀態")
    
    # 清理測試檔案
    cleanup_test_files()

if __name__ == "__main__":
    main()
