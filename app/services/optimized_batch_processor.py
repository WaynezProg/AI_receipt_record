"""
優化批次處理服務 - 提升處理速度的智能批量處理
"""

import asyncio
import time
import uuid
import os
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.services.csv_service import csv_service
from app.services.cache_service import cache_service
from app.services.azure_usage_tracker import azure_usage_tracker
from app.utils.image_utils import image_utils


class OptimizedBatchProcessor:
    """優化批次處理器 - 智能並行處理和本地預處理"""

    def __init__(self):
        # API限制設定
        self.azure_rate_limit = 20  # Azure每分鐘20次
        self.claude_rate_limit = 50  # Claude每分鐘50次

        # 並行控制 - 符合Azure F0免費層限制
        self.max_concurrent_azure = 1  # 降低到1個並行Azure請求，避免429錯誤
        self.max_concurrent_claude = 5  # 最大並行Claude請求
        self.batch_size = 10  # 優化的批次大小

        # 延遲控制 - 確保符合Azure限制
        self.azure_delay = 4  # 增加到4秒，確保每分鐘不超過15次請求
        self.claude_delay = 1  # Claude請求間隔

        # 進度追蹤
        self.current_progress = 0
        self.total_items = 0
        self.current_batch = 0
        self.total_batches = 0
        self.start_time = None

        # 快取控制
        self.use_cache = True
        self.skip_enhancement = True  # 跳過圖片增強以提升速度

        # 本地預處理
        self.use_local_preprocessing = True

        # 檔案管理
        self.auto_delete_successful = True  # 處理成功後自動刪除圖片
        self.keep_failed_files = True  # 保留失敗的檔案以便重試

    async def _preprocess_image_local(self, image_path: str) -> str:
        """本地圖片預處理 - 減少對Azure的依賴"""
        try:
            # 快速圖片優化
            optimized_path = await asyncio.get_event_loop().run_in_executor(
                None, self._optimize_image_sync, image_path
            )
            return optimized_path
        except Exception as e:
            logger.warning(f"本地預處理失敗: {e}")
            return image_path

    def _optimize_image_sync(self, image_path: str) -> str:
        """同步圖片優化"""
        try:
            # 快速調整大小和格式
            optimized_path = image_utils.resize_image(
                image_path, max_width=1200, max_height=1600
            )
            return optimized_path
        except Exception as e:
            logger.warning(f"圖片優化失敗: {e}")
            return image_path

    async def _process_ocr_with_retry(self, image_path: str, retries: int = 2) -> Dict:
        """帶重試的OCR處理"""
        for attempt in range(retries + 1):
            try:
                # 檢查快取
                if self.use_cache:
                    # 從圖片路徑中提取檔案名稱
                    filename = os.path.basename(image_path)
                    cached_result = cache_service.load_ocr_result(filename)
                    if cached_result:
                        logger.info(f"使用快取OCR結果: {filename}")
                        return cached_result.get("ocr_data", {})

                # 執行OCR
                result = await ocr_service.extract_text(image_path)

                # 保存到快取
                if self.use_cache and result.get("success"):
                    filename = os.path.basename(image_path)
                    cache_service.save_ocr_result(filename, result)

                return result

            except Exception as e:
                error_msg = str(e)

                # 特殊處理429錯誤（請求頻率超限）
                if "RATE_LIMIT_EXCEEDED" in error_msg or "429" in error_msg:
                    if attempt < retries:
                        # 指數退避策略：等待時間逐漸增加
                        wait_time = min(10 * (2**attempt), 60)  # 最大等待60秒
                        logger.warning(
                            f"Azure API頻率限制，等待 {wait_time} 秒後重試 ({attempt + 1}/{retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"OCR處理失敗（頻率限制）: {error_msg}")
                        return {
                            "success": False,
                            "error": f"Azure API頻率限制: {error_msg}",
                        }
                else:
                    if attempt < retries:
                        logger.warning(f"OCR重試 {attempt + 1}/{retries}: {error_msg}")
                        await asyncio.sleep(self.azure_delay * (attempt + 1))
                    else:
                        logger.error(f"OCR處理失敗: {error_msg}")
                        return {"success": False, "error": error_msg}

    async def _process_ai_with_retry(self, ocr_result: Dict, filename: str, retries: int = 2) -> Dict:
        """帶重試的AI處理（檢查暫存）"""
        # 檢查是否有AI暫存
        ai_cache_data = cache_service.load_ai_result(filename)
        if ai_cache_data and ai_cache_data.get("receipt_data"):
            logger.info(f"使用AI暫存資料: {filename}")
            # 從暫存資料恢復ReceiptData對象
            from app.models.receipt import ReceiptData
            receipt_dict = ai_cache_data["receipt_data"]
            # 處理日期字串
            if isinstance(receipt_dict.get("date"), str):
                from datetime import datetime
                try:
                    receipt_dict["date"] = datetime.fromisoformat(receipt_dict["date"])
                except:
                    pass
            return ReceiptData(**receipt_dict)
        
        # 沒有暫存，執行AI處理
        for attempt in range(retries + 1):
            try:
                # 提取結構化資料
                structured_data = ocr_service.extract_structured_data(ocr_result)

                result = await ai_service.process_receipt_text(
                    ocr_result, structured_data
                )
                # 保存到暫存
                cache_service.save_ai_result(filename, result, ocr_result)
                return result

            except Exception as e:
                if attempt < retries:
                    logger.warning(f"AI重試 {attempt + 1}/{retries}: {e}")
                    await asyncio.sleep(self.claude_delay * (attempt + 1))
                else:
                    logger.error(f"AI處理失敗: {e}")
                    return {"success": False, "error": str(e)}

    async def _process_single_item_optimized(self, filename: str) -> Dict:
        """優化的單個項目處理"""
        try:
            image_path = f"./data/receipts/{filename}"

            # 1. 本地預處理
            if self.use_local_preprocessing:
                image_path = await self._preprocess_image_local(image_path)

            # 2. OCR處理（並行控制）
            ocr_result = await self._process_ocr_with_retry(image_path)
            if not ocr_result.get("success"):
                return {"success": False, "error": ocr_result.get("error", "OCR失敗")}

            # 3. AI處理（並行控制，檢查暫存）
            ai_result = await self._process_ai_with_retry(ocr_result, filename)
            if not ai_result or (isinstance(ai_result, dict) and not ai_result.get("success", True)):
                return {"success": False, "error": "AI處理失敗"}

            # 4. 處理成功後刪除圖片（如果啟用）
            if self.auto_delete_successful:
                await self._delete_successful_image(filename)

            return {
                "success": True,
                "filename": filename,
                "data": ai_result,
                "ocr_result": ocr_result,
                "processing_time": time.time(),
            }

        except Exception as e:
            logger.error(f"處理失敗 {filename}: {e}")
            return {"success": False, "error": str(e)}

    async def _delete_successful_image(self, filename: str):
        """刪除處理成功的圖片"""
        try:
            image_path = f"./data/receipts/{filename}"
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"🗑️ 已刪除處理成功的圖片: {filename}")
            else:
                logger.warning(f"圖片不存在，無法刪除: {filename}")
        except Exception as e:
            logger.error(f"刪除圖片失敗 {filename}: {e}")

    async def _cleanup_failed_images(self, failed_files: List[Dict]):
        """清理失敗的圖片（如果設定為不保留）"""
        if self.keep_failed_files:
            return

        for failed_file in failed_files:
            filename = failed_file.get("filename")
            if filename:
                try:
                    image_path = f"./data/receipts/{filename}"
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f"🗑️ 已刪除失敗的圖片: {filename}")
                except Exception as e:
                    logger.error(f"刪除失敗圖片時出錯 {filename}: {e}")

    async def _process_batch_parallel(self, filenames: List[str]) -> List[Dict]:
        """並行處理批次"""
        # 創建信號量來控制並行度
        azure_semaphore = asyncio.Semaphore(self.max_concurrent_azure)
        claude_semaphore = asyncio.Semaphore(self.max_concurrent_claude)

        async def process_with_semaphore(filename: str) -> Dict:
            async with azure_semaphore:
                # OCR處理
                image_path = f"./data/receipts/{filename}"
                if self.use_local_preprocessing:
                    image_path = await self._preprocess_image_local(image_path)

                ocr_result = await self._process_ocr_with_retry(image_path)
                if not ocr_result.get("success"):
                    return {
                        "success": False,
                        "filename": filename,
                        "error": ocr_result.get("error"),
                    }

                # 添加延遲以符合API限制
                await asyncio.sleep(self.azure_delay)

                async with claude_semaphore:
                    # AI處理
                    ai_result = await self._process_ai_with_retry(ocr_result, filename)
                    await asyncio.sleep(self.claude_delay)

                    if ai_result:
                        return {
                            "success": True,
                            "filename": filename,
                            "data": ai_result,
                        }
                    else:
                        return {
                            "success": False,
                            "filename": filename,
                            "error": "AI處理失敗",
                        }

        # 並行執行所有任務
        tasks = [process_with_semaphore(filename) for filename in filenames]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 處理結果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"success": False, "error": str(result)})
            else:
                processed_results.append(result)

        return processed_results

    async def process_large_batch_optimized(
        self, filenames: List[str], save_detailed_csv: bool = True
    ) -> Dict:
        """優化的大批量處理"""
        start_time = time.time()
        self.start_time = start_time
        self.total_items = len(filenames)
        self.current_progress = 0

        # 分批處理
        batches = [
            filenames[i : i + self.batch_size]
            for i in range(0, len(filenames), self.batch_size)
        ]
        self.total_batches = len(batches)

        logger.info(
            f"🚀 開始優化批量處理: {len(filenames)} 個檔案，{len(batches)} 個批次"
        )

        successful_receipts = []
        failed_files = []

        for batch_idx, batch_filenames in enumerate(batches):
            self.current_batch = batch_idx + 1
            logger.info(
                f"🔄 處理批次 {self.current_batch}/{self.total_batches}，包含 {len(batch_filenames)} 個檔案"
            )

            # 並行處理當前批次
            batch_results = await self._process_batch_parallel(batch_filenames)

            # 處理結果
            for result in batch_results:
                self.current_progress += 1

                if result.get("success") and result.get("data"):
                    successful_receipts.append(result["data"])
                    logger.info(f"✅ {result['filename']} 處理成功")
                else:
                    failed_files.append(
                        {
                            "filename": result.get("filename", "unknown"),
                            "error": result.get("error", "未知錯誤"),
                        }
                    )
                    logger.error(
                        f"❌ {result.get('filename', 'unknown')} 處理失敗: {result.get('error')}"
                    )

            # 批次間延遲（動態調整）
            if batch_idx < len(batches) - 1:
                delay = self._calculate_adaptive_delay(len(batch_filenames))
                logger.info(f"⏳ 批次間延遲: {delay}秒")
                await asyncio.sleep(delay)

        # 保存結果
        csv_files = {}
        if successful_receipts:
            csv_files = csv_service.save_consolidated_csv(successful_receipts)
            logger.info(f"📊 保存了 {len(successful_receipts)} 個收據到CSV")

        # 清理失敗的圖片（如果設定為不保留）
        await self._cleanup_failed_images(failed_files)

        total_time = time.time() - start_time

        return {
            "success": True,
            "processed_count": len(successful_receipts),
            "failed_count": len(failed_files),
            "failed_files": failed_files,
            "total_time": round(total_time, 2),
            "csv_files": csv_files,
            "avg_time_per_item": (
                round(total_time / len(filenames), 2) if filenames else 0
            ),
            "deleted_successful": (
                len(successful_receipts) if self.auto_delete_successful else 0
            ),
            "deleted_failed": len(failed_files) if not self.keep_failed_files else 0,
        }

    def _calculate_adaptive_delay(self, batch_size: int) -> float:
        """計算自適應延遲 - 確保符合Azure F0免費層限制"""
        # Azure F0免費層：每分鐘20次請求，即每3秒1次請求
        # 為了安全起見，設定為每4秒1次請求（每分鐘15次）
        min_delay_per_request = 4.0

        # 根據批次大小計算所需延遲
        required_delay = batch_size * min_delay_per_request

        # 添加額外的安全邊際
        safety_margin = 2.0
        total_delay = required_delay + safety_margin

        # 確保延遲在合理範圍內
        min_delay = 5.0  # 最少5秒
        max_delay = 30.0  # 最多30秒

        return max(min_delay, min(total_delay, max_delay))

    def get_progress(self) -> Dict:
        """獲取當前進度"""
        if self.total_items == 0:
            return {
                "current_progress": 0,
                "total_items": 0,
                "percentage": 0,
                "current_batch": 0,
                "total_batches": 0,
                "estimated_completion": "計算中...",
                "elapsed_time": 0,
                "optimization_status": "已啟用",
            }

        percentage = (self.current_progress / self.total_items) * 100
        elapsed_time = time.time() - self.start_time if self.start_time else 0

        # 估算剩餘時間
        if self.current_progress > 0:
            avg_time_per_item = elapsed_time / self.current_progress
            remaining_items = self.total_items - self.current_progress
            estimated_remaining = remaining_items * avg_time_per_item

            if estimated_remaining < 60:
                estimated_completion = f"{int(estimated_remaining)}秒"
            elif estimated_remaining < 3600:
                estimated_completion = f"{int(estimated_remaining / 60)}分鐘"
            else:
                estimated_completion = f"{int(estimated_remaining / 3600)}小時{int((estimated_remaining % 3600) / 60)}分鐘"
        else:
            estimated_completion = "計算中..."

        return {
            "current_progress": self.current_progress,
            "total_items": self.total_items,
            "percentage": round(percentage, 1),
            "current_batch": self.current_batch,
            "total_batches": self.total_batches,
            "estimated_completion": estimated_completion,
            "elapsed_time": round(elapsed_time, 1),
            "optimization_status": "已啟用",
            "parallel_azure": self.max_concurrent_azure,
            "parallel_claude": self.max_concurrent_claude,
        }


# 創建全局實例
optimized_batch_processor = OptimizedBatchProcessor()
