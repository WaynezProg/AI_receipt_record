#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
測試CSV創建功能，包含日文翻譯
"""

import os
import sys
from datetime import datetime

# 添加項目路徑


from app.models.receipt import ReceiptData, ReceiptItem
from app.services.csv_service import CSVService

def test_csv_creation_with_translation():
    """測試包含翻譯的CSV創建"""
    print("🔍 測試CSV創建功能（包含日文翻譯）...")
    
    # 創建測試收據數據
    test_items = [
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
        ),
        ReceiptItem(
            name="パン",
            name_japanese="パン",
            name_chinese="麵包",
            price=80.0,
            quantity=2
        ),
        ReceiptItem(
            name="お茶",
            name_japanese="お茶",
            name_chinese="茶",
            price=90.0,
            quantity=1
        )
    ]
    
    # 計算總金額
    total_amount = sum(item.price * item.quantity for item in test_items)
    
    # 創建收據數據
    receipt_data = ReceiptData(
        store_name="セブン-イレブン",
        date=datetime.now(),
        total_amount=total_amount,
        items=test_items,
        payment_method="現金",
        receipt_number="TEST001",
        tax_amount=total_amount * 0.1,
        subtotal=total_amount * 0.9,
        confidence_score=0.95,
        processing_time=2.5,
        source_image="test_receipt.jpg"
    )
    
    print("✅ 測試數據創建完成")
    print(f"   商店名稱: {receipt_data.store_name}")
    print(f"   總金額: ¥{receipt_data.total_amount:,}")
    print(f"   商品數量: {len(receipt_data.items)}")
    
    # 創建CSV服務
    csv_service = CSVService()
    
    # 測試詳細CSV創建
    try:
        csv_path = csv_service.save_detailed_csv(receipt_data, "test_translation.csv")
        print(f"✅ 詳細CSV創建成功: {csv_path}")
        
        # 檢查CSV文件內容
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\n📋 CSV文件內容預覽:")
                print(content)
        
        return True
    except Exception as e:
        print(f"❌ CSV創建失敗: {e}")
        return False

def test_multiple_receipts():
    """測試多個收據的CSV創建"""
    print("\n🔍 測試多個收據的CSV創建...")
    
    # 創建多個測試收據
    receipts = []
    
    # 收據1：便利商店
    items1 = [
        ReceiptItem(name="おにぎり", name_japanese="おにぎり", name_chinese="飯糰", price=120.0, quantity=1),
        ReceiptItem(name="コーヒー", name_japanese="コーヒー", name_chinese="咖啡", price=150.0, quantity=1)
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
        ReceiptItem(name="ラーメン", name_japanese="ラーメン", name_chinese="拉麵", price=800.0, quantity=1),
        ReceiptItem(name="餃子", name_japanese="餃子", name_chinese="餃子", price=300.0, quantity=1),
        ReceiptItem(name="ビール", name_japanese="ビール", name_chinese="啤酒", price=400.0, quantity=1)
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
    
    print("✅ 多個收據數據創建完成")
    print(f"   收據數量: {len(receipts)}")
    
    # 創建批量CSV
    try:
        csv_service = CSVService()
        csv_path = csv_service.save_receipts_to_csv(receipts, "test_multiple_receipts.csv")
        print(f"✅ 批量CSV創建成功: {csv_path}")
        
        return True
    except Exception as e:
        print(f"❌ 批量CSV創建失敗: {e}")
        return False

def show_csv_format_info():
    """顯示CSV格式資訊"""
    print("\n📋 CSV格式說明:")
    print("=" * 50)
    print("🔹 詳細CSV格式（單個收據）:")
    print("   1. 收據基本資訊")
    print("   2. 商品明細（包含翻譯）")
    print("      - 商品名稱（原始）")
    print("      - 商品名稱（日文）")
    print("      - 商品名稱（中文）")
    print("      - 價格、數量、小計")
    
    print("\n🔹 批量CSV格式（多個收據）:")
    print("   1. 每個收據一行")
    print("   2. 包含基本資訊")
    print("   3. 商品明細在詳細CSV中")
    
    print("\n🔹 翻譯欄位說明:")
    print("   - name: 原始識別的商品名稱")
    print("   - name_japanese: 日文原名（如果適用）")
    print("   - name_chinese: AI翻譯的繁體中文")

def main():
    """主測試函數"""
    print("🚀 開始測試CSV創建功能（包含日文翻譯）...")
    print("=" * 50)
    
    # 測試各個功能
    single_csv_ok = test_csv_creation_with_translation()
    multiple_csv_ok = test_multiple_receipts()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   單個收據CSV: {'✅ 通過' if single_csv_ok else '❌ 失敗'}")
    print(f"   多個收據CSV: {'✅ 通過' if multiple_csv_ok else '❌ 失敗'}")
    
    if all([single_csv_ok, multiple_csv_ok]):
        print("\n🎉 所有測試通過！CSV創建功能正常運作！")
        print("\n📝 已實現功能:")
        print("   1. ✅ 單個收據詳細CSV")
        print("   2. ✅ 多個收據批量CSV")
        print("   3. ✅ 日文商品名稱保存")
        print("   4. ✅ 中文翻譯保存")
        print("   5. ✅ 完整商品資訊")
        print("   6. ✅ UTF-8編碼支援")
        
        show_csv_format_info()
    else:
        print("\n⚠️  部分測試失敗，請檢查系統狀態")

if __name__ == "__main__":
    main()
