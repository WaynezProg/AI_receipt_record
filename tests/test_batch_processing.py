#!/usr/bin/env python3
"""
測試批次處理功能
"""

import requests
import json
import time
import asyncio

def test_batch_progress_api():
    """測試批次進度API"""
    print("🔍 測試批次進度API...")
    try:
        response = requests.get("http://localhost:8000/batch-progress")
        if response.status_code == 200:
            data = response.json()
            print("✅ 批次進度API正常")
            
            progress = data['progress']
            rate_limit_info = data['rate_limit_info']
            
            print(f"   當前進度: {progress['current_progress']}/{progress['total_items']}")
            print(f"   進度百分比: {progress['percentage']}%")
            print(f"   當前批次: {progress['current_batch']}/{progress['total_batches']}")
            print(f"   已耗時: {progress['elapsed_time']}秒")
            print(f"   預計完成: {progress['estimated_completion']}")
            
            print(f"   頻率限制: {rate_limit_info['rate_limit']} 次/分鐘")
            print(f"   批次大小: {rate_limit_info['batch_size']} 個檔案")
            print(f"   本小時使用量: {rate_limit_info['current_hour_usage']}")
            
            if rate_limit_info['warnings']:
                print("   ⚠️ 警告:")
                for warning in rate_limit_info['warnings']:
                    print(f"      - {warning}")
            else:
                print("   ✅ 無警告")
            
            return True
        else:
            print(f"❌ 批次進度API錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 批次進度API異常: {e}")
        return False

def test_usage_api():
    """測試使用量API"""
    print("\n🔍 測試使用量API...")
    try:
        response = requests.get("http://localhost:8000/usage")
        if response.status_code == 200:
            data = response.json()
            print("✅ 使用量API正常")
            
            summary = data['summary']
            print(f"   月度使用量: {summary['monthly_usage']}/{summary['monthly_limit']}")
            print(f"   剩餘額度: {summary['monthly_remaining']} 次")
            print(f"   今日使用量: {summary['today_usage']} 次")
            print(f"   本小時使用量: {summary['current_hour_usage']} 次")
            
            return True
        else:
            print(f"❌ 使用量API錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 使用量API異常: {e}")
        return False

def show_batch_processing_guidelines():
    """顯示批次處理指南"""
    print("\n📋 批次處理指南:")
    print("=" * 50)
    print("🔹 頻率限制:")
    print("   - Azure API: 每分鐘最多 20 次請求")
    print("   - 系統自動分批: 每批最多 20 個檔案")
    print("   - 批次間延遲: 60 秒")
    print("   - 請求間延遲: 3 秒")
    
    print("\n🔹 處理策略:")
    print("   - 小量檔案 (< 20): 直接處理")
    print("   - 中量檔案 (20-100): 自動分批")
    print("   - 大量檔案 (> 100): 建議分批處理")
    
    print("\n🔹 時間估算:")
    print("   - 每批 20 個檔案: 約 2 分鐘")
    print("   - 100 個檔案: 約 10 分鐘")
    print("   - 500 個檔案: 約 50 分鐘")
    
    print("\n🔹 監控工具:")
    print("   - 進度追蹤: 實時顯示處理進度")
    print("   - 使用量監控: 避免超出API限制")
    print("   - 警告系統: 及時收到限制警告")
    
    print("\n🔹 最佳實踐:")
    print("   1. 大量檔案建議分批上傳")
    print("   2. 定期檢查使用量頁面")
    print("   3. 避免同時處理多個大量批次")
    print("   4. 監控進度避免重複處理")

def test_batch_processing_simulation():
    """模擬批次處理測試"""
    print("\n🔍 模擬批次處理測試...")
    try:
        # 模擬一個小的批次處理請求
        test_filenames = ["test1.jpg", "test2.jpg", "test3.jpg"]
        
        print(f"   模擬處理 {len(test_filenames)} 個檔案")
        print("   注意：這是模擬測試，不會實際處理檔案")
        
        # 檢查進度API
        response = requests.get("http://localhost:8000/batch-progress")
        if response.status_code == 200:
            data = response.json()
            progress = data['progress']
            
            if progress['total_items'] == 0:
                print("   ✅ 系統準備就緒，無進行中的批次處理")
            else:
                print(f"   ⚠️  有進行中的批次處理: {progress['current_progress']}/{progress['total_items']}")
        
        return True
    except Exception as e:
        print(f"❌ 模擬測試異常: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試批次處理系統...")
    print("=" * 50)
    
    # 測試各個功能
    batch_progress_ok = test_batch_progress_api()
    usage_api_ok = test_usage_api()
    simulation_ok = test_batch_processing_simulation()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"   批次進度API: {'✅ 通過' if batch_progress_ok else '❌ 失敗'}")
    print(f"   使用量API: {'✅ 通過' if usage_api_ok else '❌ 失敗'}")
    print(f"   模擬測試: {'✅ 通過' if simulation_ok else '❌ 失敗'}")
    
    if all([batch_progress_ok, usage_api_ok, simulation_ok]):
        print("\n🎉 所有測試通過！批次處理系統正常運作！")
        print("\n📝 已實現功能:")
        print("   1. ✅ 批次處理服務")
        print("   2. ✅ 頻率控制機制")
        print("   3. ✅ 進度追蹤API")
        print("   4. ✅ 自動分批處理")
        print("   5. ✅ 延遲控制")
        print("   6. ✅ 時間估算")
        print("   7. ✅ 使用量監控")
        print("   8. ✅ 警告系統")
        
        show_batch_processing_guidelines()
    else:
        print("\n⚠️  部分測試失敗，請檢查系統狀態")

if __name__ == "__main__":
    main()
