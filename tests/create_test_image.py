#!/usr/bin/env python3
"""
創建測試圖片
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_receipt_image(filename, store_name="テスト店", total_amount=1500):
    """創建測試收據圖片"""
    # 創建圖片
    width, height = 400, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 嘗試使用系統字體
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 繪製收據內容
    y_position = 50
    
    # 商店名稱
    draw.text((50, y_position), store_name, fill='black', font=font)
    y_position += 40
    
    # 日期
    draw.text((50, y_position), "2025-08-17", fill='black', font=font)
    y_position += 40
    
    # 商品項目
    items = [
        ("商品A", 500),
        ("商品B", 800),
        ("商品C", 200)
    ]
    
    for item_name, price in items:
        draw.text((50, y_position), f"{item_name} ¥{price}", fill='black', font=small_font)
        y_position += 30
    
    # 分隔線
    draw.line([(50, y_position), (350, y_position)], fill='black', width=2)
    y_position += 20
    
    # 總金額
    draw.text((50, y_position), f"合計: ¥{total_amount}", fill='black', font=font)
    y_position += 40
    
    # 付款方式
    draw.text((50, y_position), "現金", fill='black', font=font)
    
    # 儲存圖片
    image.save(filename, 'JPEG', quality=95)
    print(f"創建測試圖片: {filename}")

def main():
    """主函數"""
    upload_dir = "./data/receipts"
    
    # 確保目錄存在
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 創建3個測試圖片
    for i in range(3):
        filename = f"test_cache_{i+1:03d}.jpg"
        file_path = os.path.join(upload_dir, filename)
        
        store_name = f"テスト店{i+1}"
        total_amount = 1000 + (i * 500)
        
        create_test_receipt_image(file_path, store_name, total_amount)
    
    print("✅ 測試圖片創建完成")

if __name__ == "__main__":
    main()
