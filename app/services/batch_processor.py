"""
批次處理服務 - 處理大量圖片時的頻率控制和分批處理
"""

import asyncio
import os
import time
import uuid
from typing import List, Dict, Optional
from loguru import logger
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.services.csv_service import csv_service
from app.services.cache_service import cache_service
from app.services.azure_usage_tracker import azure_usage_tracker
from app.utils.image_utils import image_utils


class BatchProcessor:
    """批次處理器 - 處理大量圖片時的頻率控制"""

    def __init__(self):
        self.rate_limit = 20  # 每分鐘最多20次請求
        self.batch_size = 20  # 每批最多20個圖片
        self.delay_between_batches = 60  # 批次間隔60秒
        self.delay_between_requests = 3  # 請求間隔3秒

        # 進度追蹤
        self.current_progress = 0
        self.total_items = 0
        self.current_batch = 0
        self.total_batches = 0
        self.start_time = None
        self.estimated_completion_time = None

        # 檔案管理
        self.auto_delete_successful = True  # 處理成功後自動刪除圖片
        self.keep_failed_files = True  # 保留失敗的檔案以便重試

    def _calculate_batch_delay(self, batch_size: int) -> float:
        """計算批次間需要的延遲時間"""
        # 確保每分鐘不超過20次請求
        requests_per_minute = batch_size
        if requests_per_minute > self.rate_limit:
            # 需要延遲以符合限制
            delay_needed = (requests_per_minute / self.rate_limit - 1) * 60
            return max(delay_needed, self.delay_between_batches)
        else:
            return self.delay_between_requests * batch_size

    def _estimate_completion_time(self, total_items: int) -> str:
        """估算完成時間"""
        if self.start_time is None:
            return "計算中..."

        elapsed_time = time.time() - self.start_time
        if self.current_progress == 0:
            return "計算中..."

        # 計算每項平均處理時間
        avg_time_per_item = elapsed_time / self.current_progress
        remaining_items = total_items - self.current_progress
        estimated_remaining_time = remaining_items * avg_time_per_item

        # 加上批次延遲時間
        remaining_batches = self.total_batches - self.current_batch
        batch_delay_time = remaining_batches * self.delay_between_batches

        total_remaining_time = estimated_remaining_time + batch_delay_time

        if total_remaining_time < 60:
            return f"{int(total_remaining_time)}秒"
        elif total_remaining_time < 3600:
            return f"{int(total_remaining_time / 60)}分鐘"
        else:
            return f"{int(total_remaining_time / 3600)}小時{int((total_remaining_time % 3600) / 60)}分鐘"

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
            }

        percentage = (self.current_progress / self.total_items) * 100
        elapsed_time = time.time() - self.start_time if self.start_time else 0

        return {
            "current_progress": self.current_progress,
            "total_items": self.total_items,
            "percentage": round(percentage, 1),
            "current_batch": self.current_batch,
            "total_batches": self.total_batches,
            "estimated_completion": self._estimate_completion_time(self.total_items),
            "elapsed_time": round(elapsed_time, 1),
        }

    async def process_single_item(
        self, filename: str, enhance_image: bool = True, save_detailed_csv: bool = False
    ) -> Dict:
        """處理單個圖片"""
        try:
            # 構建檔案路徑
            file_path = f"./data/receipts/{filename}"

            if not image_utils.validate_image(file_path):
                return {
                    "filename": filename,
                    "success": False,
                    "error": "無效的圖片檔案",
                }

            # 圖片預處理
            processed_image_path = file_path
            if enhance_image:
                processed_image_path = image_utils.enhance_image_quality(file_path)

            # OCR文字識別
            logger.info(f"批次處理 - OCR: {filename}")
            ocr_result = await ocr_service.extract_text(processed_image_path)

            # 提取結構化資料
            structured_data = ocr_service.extract_structured_data(ocr_result)

            # AI整理和結構化（檢查是否有暫存）
            logger.info(f"批次處理 - AI: {filename}")
            
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
                receipt_data = ReceiptData(**receipt_dict)
            else:
                # 執行AI處理
                receipt_data = await ai_service.process_receipt_text(
                    ocr_result, structured_data
                )
                # 保存到暫存
                cache_service.save_ai_result(filename, receipt_data, ocr_result)

            # 設定來源圖片
            receipt_data.source_image = filename

            # 不立即儲存CSV，而是收集結果
            # csv_service.save_receipt_to_csv(receipt_data)
            #
            # # 如果需要，儲存詳細CSV
            # if save_detailed_csv:
            #     csv_service.save_detailed_csv(receipt_data)

            # 處理成功後刪除圖片（如果啟用）
            if self.auto_delete_successful:
                await self._delete_successful_image(filename)

            return {"filename": filename, "success": True, "data": receipt_data}

        except Exception as e:
            logger.error(f"批次處理失敗: {filename}, 錯誤: {str(e)}")
            return {"filename": filename, "success": False, "error": str(e)}

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

    async def process_batch(
        self,
        filenames: List[str],
        enhance_image: bool = True,
        save_detailed_csv: bool = False,
    ) -> List[Dict]:
        """處理一個批次"""
        batch_results = []

        for i, filename in enumerate(filenames):
            logger.info(f"   處理檔案 {i+1}/{len(filenames)}: {filename}")

            # 處理單個圖片
            result = await self.process_single_item(
                filename, enhance_image, save_detailed_csv
            )
            batch_results.append(result)

            # 更新進度
            self.current_progress += 1

            logger.info(
                f"   檔案 {filename} 處理完成: {'成功' if result['success'] else '失敗'}"
            )

            # 如果不是最後一個，添加請求間隔
            if i < len(filenames) - 1:
                logger.info(f"   等待 {self.delay_between_requests} 秒...")
                await asyncio.sleep(self.delay_between_requests)

        return batch_results

    async def process_large_batch(
        self,
        filenames: List[str],
        enhance_image: bool = True,
        save_detailed_csv: bool = False,
    ) -> Dict:
        """處理大量圖片，包含頻率控制"""
        self.start_time = time.time()
        self.total_items = len(filenames)
        self.current_progress = 0
        self.current_batch = 0

        # 分批處理
        batches = [
            filenames[i : i + self.batch_size]
            for i in range(0, len(filenames), self.batch_size)
        ]
        self.total_batches = len(batches)

        all_results = []
        failed_files = []
        successful_receipts = []  # 收集成功的收據資料

        logger.info(f"開始批次處理 {len(filenames)} 個檔案，分為 {len(batches)} 個批次")
        logger.info(f"📊 批次分配:")
        for i, batch in enumerate(batches):
            logger.info(f"   批次 {i+1}: {len(batch)} 個檔案 - {batch}")

        for batch_index, batch_filenames in enumerate(batches):
            self.current_batch = batch_index + 1

            logger.info(
                f"🔄 處理批次 {self.current_batch}/{self.total_batches}，包含 {len(batch_filenames)} 個檔案"
            )
            logger.info(f"   批次檔案: {batch_filenames}")

            # 處理當前批次
            batch_results = await self.process_batch(
                batch_filenames, enhance_image, save_detailed_csv
            )
            all_results.extend(batch_results)

            # 收集失敗的檔案和成功的收據資料
            for result in batch_results:
                if result["success"]:
                    successful_receipts.append(result["data"])
                else:
                    failed_files.append(
                        {"filename": result["filename"], "error": result["error"]}
                    )

            # 如果不是最後一個批次，添加延遲
            if batch_index < len(batches) - 1:
                delay_time = self._calculate_batch_delay(len(batch_filenames))
                logger.info(
                    f"批次 {self.current_batch} 完成，等待 {delay_time:.1f} 秒後處理下一批次..."
                )
                await asyncio.sleep(delay_time)

        # 計算總處理時間
        total_time = time.time() - self.start_time

        # 統計結果
        processed_count = len([r for r in all_results if r["success"]])
        failed_count = len(failed_files)

        # 創建整合CSV檔案
        csv_files = {}
        if successful_receipts:
            try:
                csv_files = csv_service.save_consolidated_csv(successful_receipts)
                logger.info(f"整合CSV檔案已創建: {csv_files}")
            except Exception as e:
                logger.error(f"創建整合CSV失敗: {str(e)}")

        logger.info(f"批次處理完成，總耗時: {total_time:.2f}秒")
        logger.info(f"成功: {processed_count}, 失敗: {failed_count}")

        # 清理失敗的圖片（如果設定為不保留）
        await self._cleanup_failed_images(failed_files)

        return {
            "success": True,
            "processed_count": processed_count,
            "failed_count": failed_count,
            "results": all_results,
            "failed_files": failed_files,
            "csv_files": csv_files,  # 添加CSV檔案路徑
            "total_time": round(total_time, 2),
            "message": f"批次處理完成。成功: {processed_count}, 失敗: {failed_count}, 耗時: {total_time:.2f}秒",
            "deleted_successful": processed_count if self.auto_delete_successful else 0,
            "deleted_failed": failed_count if not self.keep_failed_files else 0,
        }

    async def process_ocr_only(
        self, filenames: List[str], enhance_image: bool = True
    ) -> Dict:
        """
        只執行OCR處理，結果暫存

        Args:
            filenames: 檔案名稱列表
            enhance_image: 是否增強圖片品質

        Returns:
            處理結果
        """
        batch_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.total_items = len(filenames)
        self.current_progress = 0

        logger.info(f"開始OCR處理 {len(filenames)} 個檔案，批次ID: {batch_id}")

        ocr_results = []
        failed_files = []

        for i, filename in enumerate(filenames):
            try:
                # 更新進度
                self.current_progress = i + 1

                # 驗證圖片
                from app.config import settings

                file_path = os.path.join(settings.upload_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"檔案不存在: {filename}")

                image_utils.validate_image(file_path)

                # 增強圖片品質
                if enhance_image:
                    enhanced_path = image_utils.enhance_image_quality(file_path)
                    process_path = enhanced_path
                else:
                    process_path = file_path

                # 執行OCR
                logger.info(f"OCR處理: {filename}")
                ocr_data = ocr_service.extract_text(process_path)

                # 暫存OCR結果
                cache_path = cache_service.save_ocr_result(filename, ocr_data)

                ocr_results.append(
                    {
                        "filename": filename,
                        "success": True,
                        "ocr_data": ocr_data,
                        "cache_path": cache_path,
                    }
                )

                logger.info(f"OCR完成並暫存: {filename}")

            except Exception as e:
                logger.error(f"OCR處理失敗: {filename}, 錯誤: {str(e)}")
                failed_files.append({"filename": filename, "error": str(e)})
                ocr_results.append(
                    {"filename": filename, "success": False, "error": str(e)}
                )

            # 添加請求間隔
            if i < len(filenames) - 1:
                await asyncio.sleep(self.delay_between_requests)

        # 儲存處理狀態
        status = {
            "batch_id": batch_id,
            "total_files": len(filenames),
            "ocr_success": len([r for r in ocr_results if r["success"]]),
            "ocr_failed": len(failed_files),
            "cache_files": [r["cache_path"] for r in ocr_results if r["success"]],
            "timestamp": time.time(),
        }
        cache_service.save_processing_status(batch_id, status)

        total_time = time.time() - self.start_time

        return {
            "success": True,
            "batch_id": batch_id,
            "processed_count": len([r for r in ocr_results if r["success"]]),
            "failed_count": len(failed_files),
            "results": ocr_results,
            "failed_files": failed_files,
            "total_time": round(total_time, 2),
            "message": f"OCR處理完成。成功: {len([r for r in ocr_results if r['success']])}, 失敗: {len(failed_files)}, 耗時: {total_time:.2f}秒",
        }

    async def process_from_cache(
        self, batch_id: str, save_detailed_csv: bool = False
    ) -> Dict:
        """
        從暫存處理AI分析

        Args:
            batch_id: 批量處理ID
            save_detailed_csv: 是否儲存詳細CSV

        Returns:
            處理結果
        """
        # 載入處理狀態
        status_data = cache_service.load_processing_status(batch_id)
        if not status_data:
            return {"success": False, "error": f"找不到批次ID: {batch_id}"}

        cache_files = status_data["status"]["cache_files"]
        logger.info(
            f"從暫存處理AI分析，批次ID: {batch_id}, 暫存檔案數: {len(cache_files)}"
        )

        self.start_time = time.time()
        self.total_items = len(cache_files)
        self.current_progress = 0

        ai_results = []
        successful_receipts = []
        failed_files = []

        for i, cache_path in enumerate(cache_files):
            try:
                # 更新進度
                self.current_progress = i + 1

                # 載入OCR結果
                cache_data = cache_service.load_ocr_result(cache_path)
                if not cache_data:
                    raise Exception(f"無法載入暫存資料: {cache_path}")

                filename = cache_data["filename"]
                ocr_data = cache_data["ocr_data"]

                # AI處理
                logger.info(f"AI處理: {filename}")
                receipt_data = ai_service.process_receipt_text(ocr_data["text"])
                receipt_data.source_image = filename

                successful_receipts.append(receipt_data)
                ai_results.append(
                    {"filename": filename, "success": True, "data": receipt_data}
                )

                logger.info(f"AI處理完成: {filename}")

            except Exception as e:
                logger.error(f"AI處理失敗: {cache_path}, 錯誤: {str(e)}")
                failed_files.append({"filename": cache_path, "error": str(e)})
                ai_results.append(
                    {"filename": cache_path, "success": False, "error": str(e)}
                )

            # 添加請求間隔
            if i < len(cache_files) - 1:
                await asyncio.sleep(self.delay_between_requests)

        # 創建整合CSV檔案
        csv_files = {}
        if successful_receipts:
            try:
                csv_files = csv_service.save_consolidated_csv(successful_receipts)
                logger.info(f"整合CSV檔案已創建: {csv_files}")
            except Exception as e:
                logger.error(f"創建整合CSV失敗: {str(e)}")

        total_time = time.time() - self.start_time

        return {
            "success": True,
            "batch_id": batch_id,
            "processed_count": len([r for r in ai_results if r["success"]]),
            "failed_count": len(failed_files),
            "results": ai_results,
            "failed_files": failed_files,
            "csv_files": csv_files,
            "total_time": round(total_time, 2),
            "message": f"AI處理完成。成功: {len([r for r in ai_results if r['success']])}, 失敗: {len(failed_files)}, 耗時: {total_time:.2f}秒",
        }

    async def merge_with_existing_csv(
        self, new_receipts: List, existing_csv_path: str = None
    ) -> Dict:
        """
        將新的收據資料合併到現有CSV檔案

        Args:
            new_receipts: 新的收據資料列表
            existing_csv_path: 現有CSV檔案路徑（可選）

        Returns:
            合併結果
        """
        try:
            # 載入現有收據資料
            existing_receipts = []
            if existing_csv_path and os.path.exists(existing_csv_path):
                existing_receipts = csv_service.load_receipts_from_csv(
                    existing_csv_path
                )
                logger.info(f"載入現有收據: {len(existing_receipts)} 筆")

            # 合併收據資料
            all_receipts = existing_receipts + new_receipts
            logger.info(f"合併後總收據數: {len(all_receipts)} 筆")

            # 創建新的整合CSV
            csv_files = csv_service.save_consolidated_csv(all_receipts)

            return {
                "success": True,
                "existing_count": len(existing_receipts),
                "new_count": len(new_receipts),
                "total_count": len(all_receipts),
                "csv_files": csv_files,
                "message": f"合併完成。原有: {len(existing_receipts)}, 新增: {len(new_receipts)}, 總計: {len(all_receipts)}",
            }

        except Exception as e:
            logger.error(f"合併CSV失敗: {str(e)}")
            return {"success": False, "error": str(e)}


# 全局實例
batch_processor = BatchProcessor()
