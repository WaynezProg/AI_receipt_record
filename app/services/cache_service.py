#!/usr/bin/env python3
"""
暫存服務 - 管理OCR結果和處理狀態
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
from app.models.receipt import ReceiptData


class CacheService:
    """暫存服務，管理OCR結果和處理狀態"""

    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """確保暫存目錄存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"創建暫存目錄: {self.cache_dir}")

    def save_ocr_result(self, filename: str, ocr_data: Dict[str, Any]) -> str:
        """
        儲存OCR結果到暫存檔案

        Args:
            filename: 原始檔案名稱
            ocr_data: OCR結果資料

        Returns:
            暫存檔案路徑
        """
        try:
            # 創建暫存資料
            cache_data = {
                "filename": filename,
                "ocr_data": ocr_data,
                "timestamp": datetime.now().isoformat(),
                "status": "ocr_completed",
            }

            # 生成暫存檔案名稱
            cache_filename = f"ocr_{filename}_{int(time.time())}.json"
            cache_path = os.path.join(self.cache_dir, cache_filename)

            # 儲存到JSON檔案
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"OCR結果已暫存: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"儲存OCR結果失敗: {str(e)}")
            raise

    def load_ocr_result(self, filename_or_path: str) -> Optional[Dict[str, Any]]:
        """
        從暫存檔案載入OCR結果

        Args:
            filename_or_path: 原始檔案名稱或暫存檔案路徑

        Returns:
            OCR結果資料
        """
        try:
            # 如果是完整路徑，直接使用
            if os.path.isabs(filename_or_path) or filename_or_path.startswith("./"):
                cache_path = filename_or_path
            else:
                # 如果是檔案名稱，查找對應的暫存檔案
                cache_path = self._find_cache_file(filename_or_path)
                if not cache_path:
                    logger.warning(f"找不到對應的暫存檔案: {filename_or_path}")
                    return None

            if not os.path.exists(cache_path):
                logger.warning(f"暫存檔案不存在: {cache_path}")
                return None

            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            logger.info(f"載入OCR結果: {cache_path}")
            return cache_data

        except Exception as e:
            logger.error(f"載入OCR結果失敗: {str(e)}")
            return None

    def _find_cache_file(self, filename: str, cache_type: str = "ocr") -> Optional[str]:
        """
        根據原始檔案名稱查找對應的暫存檔案

        Args:
            filename: 原始檔案名稱
            cache_type: 暫存類型 ("ocr" 或 "ai")

        Returns:
            暫存檔案路徑，如果找不到則返回None
        """
        try:
            # 查找以 "{cache_type}_{filename}_" 開頭的暫存檔案
            cache_prefix = f"{cache_type}_{filename}_"

            for cache_filename in os.listdir(self.cache_dir):
                if cache_filename.startswith(cache_prefix) and cache_filename.endswith(
                    ".json"
                ):
                    return os.path.join(self.cache_dir, cache_filename)

            return None

        except Exception as e:
            logger.error(f"查找暫存檔案失敗: {str(e)}")
            return None

    def save_ai_result(self, filename: str, receipt_data: ReceiptData, ocr_result: Dict[str, Any]) -> str:
        """
        儲存AI處理結果到暫存檔案

        Args:
            filename: 原始檔案名稱
            receipt_data: ReceiptData 對象
            ocr_result: OCR結果資料（用於關聯）

        Returns:
            暫存檔案路徑
        """
        try:
            # 將ReceiptData轉換為字典（使用Pydantic的dict方法）
            if hasattr(receipt_data, 'dict'):
                # Pydantic v1
                receipt_dict = receipt_data.dict()
            elif hasattr(receipt_data, 'model_dump'):
                # Pydantic v2
                receipt_dict = receipt_data.model_dump()
            else:
                # 如果已經是字典，直接使用
                receipt_dict = receipt_data

            # 創建暫存資料
            cache_data = {
                "filename": filename,
                "receipt_data": receipt_dict,
                "ocr_result": ocr_result,  # 保存OCR結果以便關聯
                "timestamp": datetime.now().isoformat(),
                "status": "ai_completed",
            }

            # 生成暫存檔案名稱
            cache_filename = f"ai_{filename}_{int(time.time())}.json"
            cache_path = os.path.join(self.cache_dir, cache_filename)

            # 儲存到JSON檔案
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"AI結果已暫存: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"儲存AI結果失敗: {str(e)}")
            raise

    def load_ai_result(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        從暫存檔案載入AI處理結果

        Args:
            filename: 原始檔案名稱

        Returns:
            AI結果資料（包含receipt_data和ocr_result），可以直接用ReceiptData.parse_obj()轉換
        """
        try:
            # 查找對應的暫存檔案
            cache_path = self._find_cache_file(filename, "ai")
            if not cache_path:
                logger.debug(f"找不到對應的AI暫存檔案: {filename}")
                return None

            if not os.path.exists(cache_path):
                logger.warning(f"AI暫存檔案不存在: {cache_path}")
                return None

            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            logger.info(f"載入AI結果: {cache_path}")
            return cache_data

        except Exception as e:
            logger.error(f"載入AI結果失敗: {str(e)}")
            return None

    def save_processing_status(self, batch_id: str, status: Dict[str, Any]) -> str:
        """
        儲存批量處理狀態

        Args:
            batch_id: 批量處理ID
            status: 處理狀態資料

        Returns:
            狀態檔案路徑
        """
        try:
            status_data = {
                "batch_id": batch_id,
                "status": status,
                "timestamp": datetime.now().isoformat(),
            }

            status_filename = f"status_{batch_id}.json"
            status_path = os.path.join(self.cache_dir, status_filename)

            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)

            logger.info(f"處理狀態已儲存: {status_path}")
            return status_path

        except Exception as e:
            logger.error(f"儲存處理狀態失敗: {str(e)}")
            raise

    def load_processing_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        載入批量處理狀態

        Args:
            batch_id: 批量處理ID

        Returns:
            處理狀態資料
        """
        try:
            status_filename = f"status_{batch_id}.json"
            status_path = os.path.join(self.cache_dir, status_filename)

            if not os.path.exists(status_path):
                return None

            with open(status_path, "r", encoding="utf-8") as f:
                status_data = json.load(f)

            return status_data

        except Exception as e:
            logger.error(f"載入處理狀態失敗: {str(e)}")
            return None

    def list_cache_files(self) -> List[Dict[str, Any]]:
        """
        列出所有暫存檔案

        Returns:
            暫存檔案列表
        """
        try:
            cache_files = []

            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_stat = os.stat(file_path)

                    # 判斷暫存類型
                    if filename.startswith("ocr_"):
                        cache_type = "ocr"
                    elif filename.startswith("ai_"):
                        cache_type = "ai"
                    else:
                        cache_type = "status"
                    
                    cache_files.append(
                        {
                            "filename": filename,
                            "path": file_path,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(
                                file_stat.st_mtime
                            ).isoformat(),
                            "type": cache_type,
                        }
                    )

            return sorted(cache_files, key=lambda x: x["modified"], reverse=True)

        except Exception as e:
            logger.error(f"列出暫存檔案失敗: {str(e)}")
            return []

    def cleanup_old_cache(self, max_age_hours: int = 24) -> int:
        """
        清理舊的暫存檔案

        Args:
            max_age_hours: 最大保留時間（小時）

        Returns:
            清理的檔案數量
        """
        try:
            cleaned_count = 0
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_age = current_time - os.path.getmtime(file_path)

                    if file_age > max_age_seconds:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"清理舊暫存檔案: {filename}")
                        except Exception as e:
                            logger.error(f"清理檔案失敗: {filename}, 錯誤: {str(e)}")

            logger.info(f"清理完成，共清理 {cleaned_count} 個檔案")
            return cleaned_count

        except Exception as e:
            logger.error(f"清理暫存檔案失敗: {str(e)}")
            return 0

    def delete_ocr_cache(self, filename: str) -> bool:
        """
        刪除指定檔案的OCR暫存

        Args:
            filename: 原始檔案名稱

        Returns:
            是否成功刪除
        """
        try:
            cache_path = self._find_cache_file(filename, "ocr")
            if cache_path and os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"已刪除OCR暫存: {cache_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"刪除OCR暫存失敗: {str(e)}")
            return False

    def delete_ai_cache(self, filename: str) -> bool:
        """
        刪除指定檔案的AI暫存

        Args:
            filename: 原始檔案名稱

        Returns:
            是否成功刪除
        """
        try:
            cache_path = self._find_cache_file(filename, "ai")
            if cache_path and os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"已刪除AI暫存: {cache_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"刪除AI暫存失敗: {str(e)}")
            return False

    def get_cache_summary(self) -> Dict[str, Any]:
        """
        獲取暫存摘要資訊

        Returns:
            暫存摘要資訊
        """
        try:
            cache_files = self.list_cache_files()

            ocr_files = [f for f in cache_files if f["type"] == "ocr"]
            ai_files = [f for f in cache_files if f["type"] == "ai"]
            status_files = [f for f in cache_files if f["type"] == "status"]

            total_size = sum(f["size"] for f in cache_files)

            return {
                "total_files": len(cache_files),
                "ocr_files": len(ocr_files),
                "ai_files": len(ai_files),
                "status_files": len(status_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": self.cache_dir,
            }

        except Exception as e:
            logger.error(f"獲取暫存摘要失敗: {str(e)}")
            return {}


# 全局實例
cache_service = CacheService()
