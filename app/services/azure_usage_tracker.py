"""
Azure Computer Vision API 使用量追蹤服務
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from app.config import settings


class AzureUsageTracker:
    """Azure API 使用量追蹤器"""
    
    def __init__(self):
        self.usage_file = os.path.join(settings.output_dir, "azure_usage.json")
        self.monthly_limit = 5000  # 每月免費額度
        self.rate_limit = 20  # 每分鐘請求限制
        self.max_image_size = 4 * 1024 * 1024  # 4MB
        
        # 初始化使用量檔案
        self._init_usage_file()
    
    def _init_usage_file(self):
        """初始化使用量檔案"""
        if not os.path.exists(self.usage_file):
            current_month = datetime.now().strftime("%Y-%m")
            initial_usage = {
                "current_month": current_month,
                "monthly_usage": 0,
                "daily_usage": {},
                "hourly_usage": {},
                "total_cost_estimate": 0.0,
                "last_reset": datetime.now().isoformat(),
                "api_calls": []
            }
            self._save_usage(initial_usage)
    
    def _load_usage(self) -> Dict:
        """載入使用量資料"""
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入使用量資料失敗: {e}")
            return self._get_default_usage()
    
    def _save_usage(self, usage_data: Dict):
        """儲存使用量資料"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(usage_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"儲存使用量資料失敗: {e}")
    
    def _get_default_usage(self) -> Dict:
        """獲取預設使用量資料"""
        current_month = datetime.now().strftime("%Y-%m")
        return {
            "current_month": current_month,
            "monthly_usage": 0,
            "daily_usage": {},
            "hourly_usage": {},
            "total_cost_estimate": 0.0,
            "last_reset": datetime.now().isoformat(),
            "api_calls": []
        }
    
    def _check_monthly_reset(self, usage_data: Dict):
        """檢查是否需要重置月度使用量"""
        current_month = datetime.now().strftime("%Y-%m")
        if usage_data["current_month"] != current_month:
            usage_data["current_month"] = current_month
            usage_data["monthly_usage"] = 0
            usage_data["daily_usage"] = {}
            usage_data["hourly_usage"] = {}
            usage_data["last_reset"] = datetime.now().isoformat()
            logger.info("月度使用量已重置")
    
    def record_api_call(self, image_size: int, processing_time: float, success: bool = True):
        """記錄API調用"""
        usage_data = self._load_usage()
        
        # 檢查月度重置
        self._check_monthly_reset(usage_data)
        
        # 更新使用量統計
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        
        # 月度使用量
        if success:
            usage_data["monthly_usage"] += 1
        
        # 每日使用量
        if current_date not in usage_data["daily_usage"]:
            usage_data["daily_usage"][current_date] = 0
        if success:
            usage_data["daily_usage"][current_date] += 1
        
        # 每小時使用量
        if current_hour not in usage_data["hourly_usage"]:
            usage_data["hourly_usage"][current_hour] = 0
        if success:
            usage_data["hourly_usage"][current_hour] += 1
        
        # 記錄詳細調用資訊
        api_call = {
            "timestamp": datetime.now().isoformat(),
            "image_size_mb": round(image_size / (1024 * 1024), 2),
            "processing_time": round(processing_time, 2),
            "success": success,
            "cost_estimate": self._calculate_cost_estimate(image_size)
        }
        usage_data["api_calls"].append(api_call)
        
        # 限制API調用記錄數量（保留最近1000次）
        if len(usage_data["api_calls"]) > 1000:
            usage_data["api_calls"] = usage_data["api_calls"][-1000:]
        
        # 更新總成本估算
        usage_data["total_cost_estimate"] = self._calculate_total_cost(usage_data["api_calls"])
        
        self._save_usage(usage_data)
        
        # 檢查限制
        self._check_limits(usage_data)
    
    def _calculate_cost_estimate(self, image_size: int) -> float:
        """計算單次調用成本估算（基於Azure定價）"""
        # Azure Computer Vision 定價（每1000次交易）
        # 免費層：前5000次免費
        # 付費層：$1.00 per 1000 transactions
        
        # 這裡只是估算，實際成本可能不同
        return 0.001  # $0.001 per transaction
    
    def _calculate_total_cost(self, api_calls: List[Dict]) -> float:
        """計算總成本估算"""
        total_cost = 0.0
        for call in api_calls:
            if call["success"]:
                total_cost += call["cost_estimate"]
        return round(total_cost, 4)
    
    def _check_limits(self, usage_data: Dict):
        """檢查使用量限制"""
        monthly_usage = usage_data["monthly_usage"]
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        hourly_usage = usage_data["hourly_usage"].get(current_hour, 0)
        
        # 檢查月度限制
        if monthly_usage >= self.monthly_limit:
            logger.warning(f"⚠️ 已達到月度免費額度限制: {monthly_usage}/{self.monthly_limit}")
        
        # 檢查每分鐘限制（這裡用每小時作為近似）
        if hourly_usage >= self.rate_limit * 60:
            logger.warning(f"⚠️ 已達到每小時請求限制: {hourly_usage}")
        
        # 檢查使用量警告
        if monthly_usage >= self.monthly_limit * 0.8:
            logger.warning(f"⚠️ 月度使用量已達80%: {monthly_usage}/{self.monthly_limit}")
    
    def get_usage_summary(self) -> Dict:
        """獲取使用量摘要"""
        usage_data = self._load_usage()
        self._check_monthly_reset(usage_data)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        
        return {
            "current_month": usage_data["current_month"],
            "monthly_usage": usage_data["monthly_usage"],
            "monthly_limit": self.monthly_limit,
            "monthly_remaining": max(0, self.monthly_limit - usage_data["monthly_usage"]),
            "monthly_percentage": round((usage_data["monthly_usage"] / self.monthly_limit) * 100, 1),
            "today_usage": usage_data["daily_usage"].get(current_date, 0),
            "current_hour_usage": usage_data["hourly_usage"].get(current_hour, 0),
            "rate_limit": self.rate_limit,
            "total_cost_estimate": usage_data["total_cost_estimate"],
            "last_reset": usage_data["last_reset"],
            "warnings": self._get_warnings(usage_data)
        }
    
    def _get_warnings(self, usage_data: Dict) -> List[str]:
        """獲取警告訊息"""
        warnings = []
        monthly_usage = usage_data["monthly_usage"]
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        hourly_usage = usage_data["hourly_usage"].get(current_hour, 0)
        
        if monthly_usage >= self.monthly_limit:
            warnings.append(f"已達到月度免費額度限制 ({monthly_usage}/{self.monthly_limit})")
        elif monthly_usage >= self.monthly_limit * 0.8:
            warnings.append(f"月度使用量已達80% ({monthly_usage}/{self.monthly_limit})")
        
        if hourly_usage >= self.rate_limit * 60:
            warnings.append(f"已達到每小時請求限制 ({hourly_usage})")
        
        return warnings
    
    def get_daily_usage_chart(self, days: int = 7) -> Dict:
        """獲取每日使用量圖表資料"""
        usage_data = self._load_usage()
        
        chart_data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            usage = usage_data["daily_usage"].get(date, 0)
            chart_data.append({
                "date": date,
                "usage": usage
            })
        
        return {
            "labels": [item["date"] for item in reversed(chart_data)],
            "data": [item["usage"] for item in reversed(chart_data)]
        }
    
    def get_recent_api_calls(self, limit: int = 10) -> List[Dict]:
        """獲取最近的API調用記錄"""
        usage_data = self._load_usage()
        return usage_data["api_calls"][-limit:]


# 全局實例
azure_usage_tracker = AzureUsageTracker()
