import os
import time
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import settings
from app.models.receipt import ReceiptResponse, ReceiptListResponse
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.services.csv_service import csv_service
from app.services.azure_usage_tracker import azure_usage_tracker
from app.services.batch_processor import batch_processor
from app.services.optimized_batch_processor import optimized_batch_processor
from app.services.cache_service import cache_service
from app.utils.image_utils import image_utils

# Configure logging / 配置日誌
logger.add("logs/app.log", rotation="1 day", retention="7 days", level="INFO")

# Create FastAPI application / 創建FastAPI應用
app = FastAPI(
    title="日本收據識別系統",
    description="基於OCR + AI的日本收據識別和CSV輸出系統",
    version="1.0.0",
)

# Add CORS middleware / 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist / 確保目錄存在
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files / 掛載靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - Returns web interface
    根端點 - 返回Web介面
    """
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
        <html>
        <head><title>日本收據識別系統</title></head>
        <body>
            <h1>日本收據識別系統</h1>
            <p>請確保 static/index.html 檔案存在</p>
            <p><a href="/docs">API文檔</a></p>
        </body>
        </html>
        """
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    健康檢查端點
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"ocr": "available", "ai": "available", "csv": "available"},
    }


@app.get("/api-status")
async def check_api_status():
    """
    Check API configuration status
    檢查 API 配置狀態

    Returns:
        API configuration status and diagnostic information
        API 配置狀態和診斷資訊
    """
    status = {
        "azure_vision": {
            "configured": bool(settings.azure_vision_endpoint and settings.azure_vision_key),
            "endpoint": settings.azure_vision_endpoint[:50] + "..." if settings.azure_vision_endpoint and len(settings.azure_vision_endpoint) > 50 else settings.azure_vision_endpoint,
            "endpoint_full": settings.azure_vision_endpoint if settings.azure_vision_endpoint else None,
            "key_set": bool(settings.azure_vision_key),
            "key_preview": settings.azure_vision_key[:10] + "..." if settings.azure_vision_key and len(settings.azure_vision_key) > 10 else None,
            "test_mode": ocr_service.test_mode,
        },
        "claude_api": {
            "configured": bool(settings.claude_api_key),
            "key_set": bool(settings.claude_api_key),
            "key_preview": settings.claude_api_key[:10] + "..." if settings.claude_api_key and len(settings.claude_api_key) > 10 else None,
            "test_mode": ai_service.test_mode,
        },
        "diagnostics": {
            "upload_dir_exists": os.path.exists(settings.upload_dir),
            "output_dir_exists": os.path.exists(settings.output_dir),
        }
    }
    
    # Try to parse Azure endpoint (no actual connection, only format check) / 嘗試解析 Azure 端點（不實際連接，只檢查格式）
    if settings.azure_vision_endpoint:
        endpoint = settings.azure_vision_endpoint.strip().rstrip("/")
        if not endpoint.startswith("https://"):
            status["azure_vision"]["warning"] = "Endpoint URL should start with https:// / 端點 URL 應該以 https:// 開頭"
        elif not endpoint.endswith(".cognitiveservices.azure.com"):
            status["azure_vision"]["warning"] = "Endpoint URL format may be incorrect (should include .cognitiveservices.azure.com) / 端點 URL 格式可能不正確（應包含 .cognitiveservices.azure.com）"
        else:
            status["azure_vision"]["endpoint_valid"] = True
    
    return status


@app.post("/upload", response_model=dict)
async def upload_receipt(file: UploadFile = File(...)):
    """
    Upload receipt image
    上傳收據圖片

    Args:
        file: Uploaded image file / 上傳的圖片檔案

    Returns:
        Upload result / 上傳結果
    """
    try:
        # Validate file format / 驗證檔案格式
        allowed_extensions = settings.allowed_extensions_list
        file_ext = file.filename.split(".")[-1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)} / 不支援的檔案格式。支援的格式: {', '.join(allowed_extensions)}",
            )

        # Generate filename (add microseconds to avoid duplicates) / 生成檔案名稱（添加微秒避免重複）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds / 包含毫秒
        filename = f"receipt_{timestamp}.{file_ext}"
        file_path = os.path.join(settings.upload_dir, filename)

        # Save file / 儲存檔案
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate image / 驗證圖片
        if not image_utils.validate_image(file_path, settings.max_file_size):
            os.remove(file_path)  # Delete invalid file / 刪除無效檔案
            raise HTTPException(status_code=400, detail="Invalid image file / 無效的圖片檔案")

        logger.info(f"Image upload successful: {filename} / 圖片上傳成功: {filename}")

        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "upload_time": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)} / 圖片上傳失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)} / 上傳失敗: {str(e)}")


@app.post("/upload-batch")
async def upload_batch_receipts(files: List[UploadFile] = File(...)):
    """
    批量上傳收據圖片

    Args:
        files: 上傳的圖片檔案列表

    Returns:
        批量上傳結果
    """
    try:
        uploaded_files = []
        failed_files = []

        for file_index, file in enumerate(files):
            try:
                # Validate file format / 驗證檔案格式
                allowed_extensions = settings.allowed_extensions_list
                file_ext = file.filename.split(".")[-1].lower()

                if file_ext not in allowed_extensions:
                    failed_files.append(
                        {
                            "filename": file.filename,
                            "error": f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)} / 不支援的檔案格式。支援的格式: {', '.join(allowed_extensions)}",
                        }
                    )
                    continue

                # Generate filename (add index to avoid duplicates) / 生成檔案名稱（添加索引避免重複）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipt_{timestamp}_{file_index:03d}.{file_ext}"
                file_path = os.path.join(settings.upload_dir, filename)

                # Save file / 儲存檔案
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                    buffer.flush()
                    if hasattr(buffer, 'fileno'):
                        try:
                            os.fsync(buffer.fileno())
                        except:
                            pass  # Some systems may not support fsync / 某些系統可能不支援 fsync

                # Verify file exists (wait a short time to ensure file is written) / 驗證檔案是否存在（等待一小段時間確保檔案已寫入）
                import time
                time.sleep(0.01)  # Brief delay to ensure filesystem sync / 短暫延遲確保檔案系統同步
                
                if not os.path.exists(file_path):
                    failed_files.append(
                        {"filename": file.filename, "error": "File save failed / 檔案儲存失敗"}
                    )
                    logger.error(f"File does not exist: {file_path} / 檔案不存在: {file_path}")
                    continue

                # Validate image (PDF files skip image validation) / 驗證圖片（PDF 檔案跳過圖片驗證）
                if file_ext.lower() != "pdf":
                    if not image_utils.validate_image(file_path, settings.max_file_size):
                        if os.path.exists(file_path):
                            os.remove(file_path)  # Delete invalid file / 刪除無效檔案
                        failed_files.append(
                            {"filename": file.filename, "error": "Invalid image file / 無效的圖片檔案"}
                        )
                        continue

                uploaded_files.append(filename)
                logger.info(f"Batch upload successful: {filename} / 批量上傳成功: {filename}")

            except Exception as e:
                failed_files.append({"filename": file.filename, "error": str(e)})
                logger.error(f"批量上傳失敗: {file.filename}, 錯誤: {str(e)}")

        return {
            "success": True,
            "uploaded_count": len(uploaded_files),
            "failed_count": len(failed_files),
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "message": f"批量上傳完成。成功: {len(uploaded_files)}, 失敗: {len(failed_files)}",
        }

    except Exception as e:
        logger.error(f"批量上傳失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量上傳失敗: {str(e)}")


@app.post("/process", response_model=ReceiptResponse)
async def process_receipt(
    filename: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    enhance_image: bool = Form(True),
    save_detailed_csv: bool = Form(False),
):
    """
    Process receipt recognition
    處理收據識別

    Args:
        filename: Image file name / 圖片檔案名稱
        background_tasks: Background tasks / 背景任務
        enhance_image: Whether to enhance image quality / 是否增強圖片品質
        save_detailed_csv: Whether to save detailed CSV / 是否儲存詳細CSV

    Returns:
        Recognition result / 識別結果
    """
    try:
        start_time = time.time()

        # Build file path / 構建檔案路徑
        file_path = os.path.join(settings.upload_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found / 檔案不存在")

        # 圖片預處理
        processed_image_path = file_path
        if enhance_image:
            processed_image_path = image_utils.enhance_image_quality(file_path)

        # OCR文字識別（檢查是否有暫存）
        logger.info(f"開始OCR處理: {filename}")
        
        # 檢查是否有OCR暫存
        cache_data = cache_service.load_ocr_result(filename)
        if cache_data and cache_data.get("ocr_data"):
            logger.info(f"使用OCR暫存資料: {filename}")
            ocr_result = cache_data["ocr_data"]
        else:
            # 執行OCR
            ocr_result = await ocr_service.extract_text(processed_image_path)
            # 保存到暫存
            cache_service.save_ocr_result(filename, ocr_result)

        # 提取結構化資料
        structured_data = ocr_service.extract_structured_data(ocr_result)

        # AI整理和結構化（檢查是否有暫存）
        logger.info(f"開始AI處理: {filename}")
        
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

        # 計算總處理時間
        total_time = time.time() - start_time
        receipt_data.processing_time = total_time

        # 儲存CSV檔案
        csv_filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = csv_service.save_receipt_to_csv(receipt_data, csv_filename)

        # 如果需要詳細CSV，在背景任務中處理
        if save_detailed_csv:
            background_tasks.add_task(
                csv_service.save_detailed_csv, receipt_data, f"detailed_{csv_filename}"
            )

        # 清理臨時檔案
        if enhance_image and processed_image_path != file_path:
            background_tasks.add_task(os.remove, processed_image_path)

        # 處理成功後刪除原始圖片（與批量處理保持一致）
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ 已刪除處理成功的圖片: {filename}")
        except Exception as e:
            logger.warning(f"刪除圖片失敗: {str(e)}")

        logger.info(f"收據處理完成: {filename}, 耗時: {total_time:.2f}秒")

        return ReceiptResponse(
            success=True, data=receipt_data, processing_time=total_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"收據處理失敗: {str(e)}")
        return ReceiptResponse(
            success=False, error=str(e), processing_time=time.time() - start_time
        )


@app.post("/process-batch")
async def process_batch_receipts(
    filenames: List[str] = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    enhance_image: bool = Form(True),
    save_detailed_csv: bool = Form(False),
):
    """
    批量處理收據識別（包含頻率控制）

    Args:
        filenames: 圖片檔案名稱列表
        background_tasks: 背景任務
        enhance_image: 是否增強圖片品質
        save_detailed_csv: 是否儲存詳細CSV

    Returns:
        批量處理結果
    """
    try:
        logger.info(f"📋 收到批量處理請求:")
        logger.info(f"   檔案數量: {len(filenames)}")
        logger.info(f"   檔案列表: {filenames}")
        logger.info(f"   增強圖片: {enhance_image}")
        logger.info(f"   儲存詳細CSV: {save_detailed_csv}")

        # 詳細檢查每個檔案
        logger.info("🔍 詳細檔案檢查:")
        for i, filename in enumerate(filenames):
            file_path = os.path.join(settings.upload_dir, filename)
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0
            logger.info(f"   {i+1:2d}. {filename} - 存在: {exists}, 大小: {size} bytes")

        # 檢查檔案數量
        if len(filenames) > 100:
            logger.warning(f"大量檔案處理警告: {len(filenames)} 個檔案")
            logger.info("建議分批處理大量檔案以避免API限制")

        # 檢查檔案是否存在
        for filename in filenames:
            file_path = os.path.join(settings.upload_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                raise HTTPException(status_code=404, detail=f"檔案不存在: {filename}")
            else:
                logger.info(f"檔案存在: {file_path}")

        # 使用批次處理服務
        result = await batch_processor.process_large_batch(
            filenames, enhance_image, save_detailed_csv
        )

        return result

    except Exception as e:
        logger.error(f"批量處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量處理失敗: {str(e)}")


@app.post("/process-batch-optimized")
async def process_batch_optimized(
    filenames: List[str] = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    save_detailed_csv: bool = Form(False),
):
    """
    優化批量處理收據識別（快速版本）

    Args:
        filenames: 圖片檔案名稱列表
        background_tasks: 背景任務
        save_detailed_csv: 是否儲存詳細CSV

    Returns:
        優化批量處理結果
    """
    try:
        logger.info(f"🚀 收到優化批量處理請求:")
        logger.info(f"   檔案數量: {len(filenames)}")
        logger.info(f"   檔案列表: {filenames}")
        logger.info(f"   儲存詳細CSV: {save_detailed_csv}")

        # 詳細檢查每個檔案
        logger.info("🔍 詳細檔案檢查:")
        for i, filename in enumerate(filenames):
            file_path = os.path.join(settings.upload_dir, filename)
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0
            logger.info(f"   {i+1:2d}. {filename} - 存在: {exists}, 大小: {size} bytes")

        # 檢查檔案數量
        if len(filenames) > 100:
            logger.warning(f"大量檔案處理警告: {len(filenames)} 個檔案")
            logger.info("優化版本可以更快速地處理大量檔案")

        # 檢查檔案是否存在
        for filename in filenames:
            file_path = os.path.join(settings.upload_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                raise HTTPException(status_code=404, detail=f"檔案不存在: {filename}")
            else:
                logger.info(f"檔案存在: {file_path}")

        # 使用優化批次處理服務
        result = await optimized_batch_processor.process_large_batch_optimized(
            filenames, save_detailed_csv
        )

        return result

    except Exception as e:
        logger.error(f"優化批量處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"優化批量處理失敗: {str(e)}")


@app.post("/ocr-only")
async def process_ocr_only(
    filenames: List[str] = Form(...), enhance_image: bool = Form(True)
):
    """
    只執行OCR處理，結果暫存
    """
    try:
        logger.info(f"📋 收到OCR處理請求:")
        logger.info(f"   檔案數量: {len(filenames)}")
        logger.info(f"   檔案列表: {filenames}")
        logger.info(f"   增強圖片: {enhance_image}")

        # 檢查檔案是否存在
        for filename in filenames:
            file_path = os.path.join(settings.upload_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                raise HTTPException(status_code=404, detail=f"檔案不存在: {filename}")
            else:
                logger.info(f"檔案存在: {file_path}")

        # 執行OCR處理
        result = await batch_processor.process_ocr_only(filenames, enhance_image)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR處理失敗: {str(e)}")


@app.post("/process-from-cache")
async def process_from_cache(
    batch_id: str = Form(...), save_detailed_csv: bool = Form(True)
):
    """
    從暫存處理AI分析
    """
    try:
        logger.info(f"📋 收到從暫存處理請求:")
        logger.info(f"   批次ID: {batch_id}")
        logger.info(f"   儲存詳細CSV: {save_detailed_csv}")

        # 從暫存處理AI分析
        result = await batch_processor.process_from_cache(batch_id, save_detailed_csv)

        return result

    except Exception as e:
        logger.error(f"從暫存處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"從暫存處理失敗: {str(e)}")


@app.get("/cache-summary")
async def get_cache_summary():
    """
    獲取暫存摘要資訊
    """
    try:
        summary = cache_service.get_cache_summary()
        return summary
    except Exception as e:
        logger.error(f"獲取暫存摘要失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取暫存摘要失敗: {str(e)}")


@app.get("/batch-progress")
async def get_batch_progress():
    """
    獲取批次處理進度

    Returns:
        當前批次處理進度
    """
    try:
        progress = batch_processor.get_progress()

        # 添加頻率限制資訊
        usage_summary = azure_usage_tracker.get_usage_summary()

        return {
            "progress": progress,
            "rate_limit_info": {
                "rate_limit": batch_processor.rate_limit,
                "batch_size": batch_processor.batch_size,
                "delay_between_batches": batch_processor.delay_between_batches,
                "delay_between_requests": batch_processor.delay_between_requests,
                "current_hour_usage": usage_summary["current_hour_usage"],
                "warnings": usage_summary["warnings"],
            },
        }

    except Exception as e:
        logger.error(f"獲取批次進度失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取進度失敗: {str(e)}")


@app.get("/batch-progress-optimized")
async def get_batch_progress_optimized():
    """
    獲取優化批次處理進度

    Returns:
        當前優化批次處理進度
    """
    try:
        progress = optimized_batch_processor.get_progress()

        # 添加優化資訊
        usage_summary = azure_usage_tracker.get_usage_summary()

        return {
            "progress": progress,
            "optimization_info": {
                "max_concurrent_azure": optimized_batch_processor.max_concurrent_azure,
                "max_concurrent_claude": optimized_batch_processor.max_concurrent_claude,
                "batch_size": optimized_batch_processor.batch_size,
                "azure_delay": optimized_batch_processor.azure_delay,
                "claude_delay": optimized_batch_processor.claude_delay,
                "use_cache": optimized_batch_processor.use_cache,
                "use_local_preprocessing": optimized_batch_processor.use_local_preprocessing,
                "auto_delete_successful": optimized_batch_processor.auto_delete_successful,
                "keep_failed_files": optimized_batch_processor.keep_failed_files,
                "current_hour_usage": usage_summary["current_hour_usage"],
                "warnings": usage_summary["warnings"],
            },
        }

    except Exception as e:
        logger.error(f"獲取優化批次進度失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取優化進度失敗: {str(e)}")


@app.post("/configure-file-management")
async def configure_file_management(
    auto_delete_successful: bool = Form(True),
    keep_failed_files: bool = Form(True),
    processor_type: str = Form("optimized"),  # "standard" or "optimized"
):
    """
    配置檔案管理設定

    Args:
        auto_delete_successful: 處理成功後是否自動刪除圖片
        keep_failed_files: 是否保留失敗的檔案
        processor_type: 處理器類型 ("standard" 或 "optimized")

    Returns:
        配置結果
    """
    try:
        if processor_type == "optimized":
            processor = optimized_batch_processor
        else:
            processor = batch_processor

        # 更新設定
        processor.auto_delete_successful = auto_delete_successful
        processor.keep_failed_files = keep_failed_files

        logger.info(f"檔案管理設定已更新 ({processor_type}):")
        logger.info(f"  自動刪除成功圖片: {auto_delete_successful}")
        logger.info(f"  保留失敗檔案: {keep_failed_files}")

        return {
            "success": True,
            "message": "檔案管理設定已更新",
            "settings": {
                "auto_delete_successful": auto_delete_successful,
                "keep_failed_files": keep_failed_files,
                "processor_type": processor_type,
            },
        }

    except Exception as e:
        logger.error(f"配置檔案管理設定失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"配置失敗: {str(e)}")


@app.get("/file-management-settings")
async def get_file_management_settings():
    """
    獲取檔案管理設定

    Returns:
        當前檔案管理設定
    """
    try:
        return {
            "standard_processor": {
                "auto_delete_successful": batch_processor.auto_delete_successful,
                "keep_failed_files": batch_processor.keep_failed_files,
            },
            "optimized_processor": {
                "auto_delete_successful": optimized_batch_processor.auto_delete_successful,
                "keep_failed_files": optimized_batch_processor.keep_failed_files,
            },
        }

    except Exception as e:
        logger.error(f"獲取檔案管理設定失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取設定失敗: {str(e)}")


@app.get("/usage")
async def get_azure_usage():
    """
    獲取Azure API使用量資訊

    Returns:
        Azure API使用量摘要
    """
    try:
        usage_summary = azure_usage_tracker.get_usage_summary()
        daily_chart = azure_usage_tracker.get_daily_usage_chart()
        recent_calls = azure_usage_tracker.get_recent_api_calls()

        return {
            "summary": usage_summary,
            "daily_chart": daily_chart,
            "recent_calls": recent_calls,
            "limits": {
                "monthly_limit": 5000,
                "rate_limit_per_minute": 20,
                "max_image_size_mb": 4,
                "supported_formats": ["JPEG", "PNG", "GIF", "BMP"],
            },
            "cost_info": {
                "free_tier": "前5000次交易免費",
                "paid_tier": "$1.00 per 1000 transactions",
                "estimated_cost": usage_summary["total_cost_estimate"],
            },
        }

    except Exception as e:
        logger.error(f"獲取Azure使用量失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取使用量失敗: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    下載CSV檔案

    Args:
        filename: 檔案名稱

    Returns:
        檔案內容
    """
    try:
        file_path = os.path.join(settings.output_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="檔案不存在")

        # 讀取檔案內容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 設定回應標頭
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8",
        }

        return Response(content=content, headers=headers)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下載檔案失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下載檔案失敗: {str(e)}")


@app.get("/uploaded-files")
async def get_uploaded_files():
    """
    獲取所有已上傳的圖片檔案列表（包含處理狀態）

    Returns:
        已上傳的檔案列表（包含檔名、大小、上傳時間、圖片URL、處理狀態）
    """
    try:
        files = []
        allowed_extensions = (".jpg", ".jpeg", ".png", ".pdf")
        
        if os.path.exists(settings.upload_dir):
            for filename in os.listdir(settings.upload_dir):
                # 只顯示圖片檔案，排除處理過的檔案（如 _resized, _enhanced 等）
                if any(filename.lower().endswith(ext) for ext in allowed_extensions):
                    file_path = os.path.join(settings.upload_dir, filename)
                    
                    # 跳過處理過的檔案（包含 _resized, _enhanced 等後綴）
                    if any(suffix in filename for suffix in ["_resized", "_enhanced"]):
                        continue
                    
                    try:
                        file_stat = os.stat(file_path)
                        
                        # 檢查處理狀態
                        processing_status = "not_processed"  # 未處理
                        has_ocr_cache = False
                        
                        # 檢查是否有OCR暫存
                        cache_data = cache_service.load_ocr_result(filename)
                        if cache_data:
                            has_ocr_cache = True
                            processing_status = "ocr_completed"  # OCR已完成
                        
                        # 檢查是否已有CSV輸出（表示已完成處理）
                        csv_files = []
                        if os.path.exists(settings.output_dir):
                            csv_files = [f for f in os.listdir(settings.output_dir) 
                                       if f.endswith(".csv") and not f.startswith("detailed_")]
                        
                        # 簡單檢查：如果CSV檔案較新於上傳時間，可能已處理（這只是粗略判斷）
                        # 更準確的方法需要檢查CSV內容，但這裡先簡單判斷
                        
                        files.append({
                            "filename": filename,
                            "size": file_stat.st_size,
                            "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                            "upload_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "modified_time": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "image_url": f"/receipt-image/{filename}",
                            "processing_status": processing_status,
                            "has_ocr_cache": has_ocr_cache,
                        })
                    except Exception as e:
                        logger.warning(f"讀取檔案資訊失敗: {filename}, 錯誤: {str(e)}")
                        continue
        
        # 按修改時間排序（最新的在前）
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return {
            "success": True,
            "files": files,
            "total_count": len(files),
        }
    
    except Exception as e:
        logger.error(f"獲取上傳檔案列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取檔案列表失敗: {str(e)}")


@app.get("/file-status/{filename}")
async def get_file_status(filename: str):
    """
    檢查檔案的處理狀態

    Args:
        filename: 檔案名稱

    Returns:
        檔案的處理狀態（是否已上傳、是否有OCR暫存、是否可以處理）
    """
    try:
        # 安全檢查：防止路徑遍歷攻擊
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="無效的檔案名稱")
        
        file_path = os.path.join(settings.upload_dir, filename)
        
        result = {
            "filename": filename,
            "exists": os.path.exists(file_path),
            "has_ocr_cache": False,
            "processing_status": "not_processed",
            "can_process": False,
        }
        
        if not result["exists"]:
            return result
        
        # 檢查OCR暫存
        cache_data = cache_service.load_ocr_result(filename)
        if cache_data:
            result["has_ocr_cache"] = True
            result["processing_status"] = "ocr_completed"
            result["can_process"] = True  # 有OCR暫存，可以直接處理
        
        # 如果檔案存在，也可以處理（即使沒有暫存）
        if not result["can_process"]:
            result["can_process"] = True
            result["processing_status"] = "not_processed"
        
        return result
    
    except Exception as e:
        logger.error(f"檢查檔案狀態失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"檢查檔案狀態失敗: {str(e)}")


@app.get("/receipt-image/{filename}")
async def get_receipt_image(filename: str):
    """
    獲取上傳的收據圖片

    Args:
        filename: 圖片檔案名稱

    Returns:
        圖片檔案
    """
    try:
        # 安全檢查：防止路徑遍歷攻擊
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="無效的檔案名稱")
        
        file_path = os.path.join(settings.upload_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="圖片不存在")
        
        # 根據檔案擴展名決定 MIME 類型
        ext = filename.split(".")[-1].lower()
        media_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
        }
        media_type = media_types.get(ext, "application/octet-stream")
        
        return FileResponse(file_path, media_type=media_type, filename=filename)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取圖片失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取圖片失敗: {str(e)}")


@app.get("/receipts", response_model=ReceiptListResponse)
async def get_receipts(limit: int = 10, offset: int = 0):
    """
    獲取已處理的收據列表

    Args:
        limit: 限制數量
        offset: 偏移量

    Returns:
        收據列表
    """
    try:
        # 掃描輸出目錄中的CSV檔案
        csv_files = []
        for file in os.listdir(settings.output_dir):
            if file.endswith(".csv") and not file.startswith("detailed_"):
                csv_files.append(file)

        # 按時間排序
        csv_files.sort(reverse=True)

        # 分頁
        csv_files = csv_files[offset : offset + limit]

        # 載入收據資料
        receipts = []
        for csv_file in csv_files:
            try:
                csv_path = os.path.join(settings.output_dir, csv_file)
                file_receipts = csv_service.load_receipts_from_csv(csv_path)
                receipts.extend(file_receipts)
            except Exception as e:
                logger.warning(f"載入CSV檔案失敗: {csv_file}, 錯誤: {str(e)}")
                continue

        return ReceiptListResponse(receipts=receipts, total_count=len(receipts))

    except Exception as e:
        logger.error(f"獲取收據列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取收據列表失敗: {str(e)}")


@app.get("/download/{filename}")
async def download_csv(filename: str):
    """
    下載CSV檔案

    Args:
        filename: CSV檔案名稱

    Returns:
        CSV檔案
    """
    try:
        file_path = os.path.join(settings.output_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="檔案不存在")

        return FileResponse(file_path, media_type="text/csv", filename=filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下載CSV檔案失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下載失敗: {str(e)}")


@app.get("/csv-files-list")
async def get_csv_files_list():
    """
    獲取所有可用的CSV檔案列表

    Returns:
        CSV檔案列表
    """
    try:
        if not os.path.exists(settings.output_dir):
            return {
                "success": False,
                "message": "輸出目錄不存在",
                "csv_files": []
            }

        # 查找所有summary CSV檔案
        csv_files_list = [
            f
            for f in os.listdir(settings.output_dir)
            if f.startswith("receipts_summary_") and f.endswith(".csv")
        ]

        csv_files_list.sort(reverse=True)  # 最新的在前

        # 格式化檔案名稱為顯示名稱（提取時間戳）
        csv_files_with_info = []
        for csv_file in csv_files_list:
            # receipts_summary_20251230_164641.csv -> 2025-12-30 16:46:41
            try:
                timestamp_str = csv_file.replace("receipts_summary_", "").replace(".csv", "")
                date_str = timestamp_str[:8]  # 20251230
                time_str = timestamp_str[9:]  # 164641
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                csv_files_with_info.append({
                    "filename": csv_file,
                    "display_name": formatted_date
                })
            except:
                csv_files_with_info.append({
                    "filename": csv_file,
                    "display_name": csv_file
                })

        return {
            "success": True,
            "csv_files": csv_files_with_info
        }

    except Exception as e:
        logger.error(f"獲取CSV檔案列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取CSV檔案列表失敗: {str(e)}")


@app.get("/csv-data/{filename}")
async def get_csv_data(filename: str):
    """
    獲取指定CSV檔案的完整資料（包含摘要和明細）
    並自動刪除已處理的圖片（僅限最新檔案）

    Args:
        filename: CSV檔案名稱（receipts_summary_*.csv）

    Returns:
        CSV資料（摘要和明細）
    """
    try:
        import csv
        
        if not os.path.exists(settings.output_dir):
            return {
                "success": False,
                "message": "輸出目錄不存在",
                "summary_data": [],
                "details_data": []
            }

        # 驗證檔案名稱
        if not filename.startswith("receipts_summary_") or not filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="無效的CSV檔案名稱")

        summary_path = os.path.join(settings.output_dir, filename)
        if not os.path.exists(summary_path):
            raise HTTPException(status_code=404, detail="CSV檔案不存在")
        
        # 推斷對應的details CSV檔案名稱
        timestamp = filename.replace("receipts_summary_", "").replace(".csv", "")
        details_filename = f"receipts_details_{timestamp}.csv"
        details_path = os.path.join(settings.output_dir, details_filename)
        
        # 讀取summary CSV
        summary_data = []
        processed_images = set()  # 收集所有已處理的圖片檔名
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summary_data = list(reader)
                # 從summary CSV中提取已處理的圖片檔名
                for row in summary_data:
                    source_image = row.get("來源圖片", "").strip()
                    if source_image:
                        processed_images.add(source_image)
        
        # 讀取details CSV
        details_data = []
        if os.path.exists(details_path):
            with open(details_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                details_data = list(reader)
        
        # 只有在請求最新檔案時才刪除已處理的圖片
        deleted_count = 0
        csv_files_list = [
            f
            for f in os.listdir(settings.output_dir)
            if f.startswith("receipts_summary_") and f.endswith(".csv")
        ]
        if csv_files_list:
            csv_files_list.sort(reverse=True)
            is_latest = csv_files_list[0] == filename
            
            if is_latest and processed_images and os.path.exists(settings.upload_dir):
                for image_filename in processed_images:
                    image_path = os.path.join(settings.upload_dir, image_filename)
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            logger.info(f"🗑️ 已刪除CSV中已記錄的圖片: {image_filename}")
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"刪除圖片失敗 {image_filename}: {str(e)}")
                
                if deleted_count > 0:
                    logger.info(f"✅ 已清理 {deleted_count} 個已處理的圖片檔案")
        
        return {
            "success": True,
            "summary_filename": filename,
            "details_filename": details_filename,
            "summary_data": summary_data,
            "details_data": details_data,
            "deleted_images_count": deleted_count,
            "is_latest": csv_files_list and csv_files_list[0] == filename if csv_files_list else False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"讀取CSV資料失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"讀取CSV資料失敗: {str(e)}")


@app.get("/latest-csv-data")
async def get_latest_csv_data():
    """
    獲取最新CSV檔案的完整資料（包含摘要和明細）
    並自動刪除已處理的圖片

    Returns:
        CSV資料（摘要和明細）
    """
    try:
        if not os.path.exists(settings.output_dir):
            return {
                "success": False,
                "message": "輸出目錄不存在",
                "summary_data": [],
                "details_data": []
            }

        # 查找最新的summary CSV檔案
        csv_files_list = [
            f
            for f in os.listdir(settings.output_dir)
            if f.startswith("receipts_summary_") and f.endswith(".csv")
        ]

        if not csv_files_list:
            return {
                "success": False,
                "message": "沒有找到CSV檔案",
                "summary_data": [],
                "details_data": []
            }

        csv_files_list.sort(reverse=True)
        latest_summary_csv = csv_files_list[0]
        
        # 使用新的端點來獲取資料（通過內部調用）
        # 這裡需要重新實現邏輯，因為不能直接調用另一個路由處理函數
        import csv
        
        summary_path = os.path.join(settings.output_dir, latest_summary_csv)
        
        # 推斷對應的details CSV檔案名稱
        timestamp = latest_summary_csv.replace("receipts_summary_", "").replace(".csv", "")
        details_filename = f"receipts_details_{timestamp}.csv"
        details_path = os.path.join(settings.output_dir, details_filename)
        
        # 讀取summary CSV
        summary_data = []
        processed_images = set()
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summary_data = list(reader)
                for row in summary_data:
                    source_image = row.get("來源圖片", "").strip()
                    if source_image:
                        processed_images.add(source_image)
        
        # 讀取details CSV
        details_data = []
        if os.path.exists(details_path):
            with open(details_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                details_data = list(reader)
        
        # 刪除已處理的圖片（僅限最新檔案）
        deleted_count = 0
        if processed_images and os.path.exists(settings.upload_dir):
            for image_filename in processed_images:
                image_path = os.path.join(settings.upload_dir, image_filename)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        logger.info(f"🗑️ 已刪除CSV中已記錄的圖片: {image_filename}")
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"刪除圖片失敗 {image_filename}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"✅ 已清理 {deleted_count} 個已處理的圖片檔案")
        
        return {
            "success": True,
            "summary_filename": latest_summary_csv,
            "details_filename": details_filename,
            "summary_data": summary_data,
            "details_data": details_data,
            "deleted_images_count": deleted_count,
            "is_latest": True
        }

    except Exception as e:
        logger.error(f"讀取CSV資料失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"讀取CSV資料失敗: {str(e)}")


@app.get("/summary")
async def get_summary():
    """
    獲取系統摘要資訊

    Returns:
        摘要資訊
    """
    try:
        # 統計檔案數量（確保目錄存在）
        receipt_files = 0
        if os.path.exists(settings.upload_dir):
            receipt_files = len(
                [
                    f
                    for f in os.listdir(settings.upload_dir)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]
            )
        
        csv_files = 0
        if os.path.exists(settings.output_dir):
            csv_files = len(
                [f for f in os.listdir(settings.output_dir) if f.endswith(".csv")]
            )

        # 獲取最新的CSV摘要
        latest_csv = None
        csv_summary = None

        csv_files_list = []
        if os.path.exists(settings.output_dir):
            csv_files_list = [
                f
                for f in os.listdir(settings.output_dir)
                if f.endswith(".csv") and not f.startswith("detailed_")
            ]

        if csv_files_list:
            csv_files_list.sort(reverse=True)
            latest_csv = csv_files_list[0]
            csv_path = os.path.join(settings.output_dir, latest_csv)
            csv_summary = csv_service.get_csv_summary(csv_path)

        return {
            "uploaded_receipts": receipt_files,
            "processed_csv_files": csv_files,
            "latest_csv": latest_csv,
            "csv_summary": csv_summary,
            "system_status": "running",
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"獲取摘要資訊失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取摘要失敗: {str(e)}")


@app.delete("/uploaded-image/{filename}")
async def delete_uploaded_image(filename: str):
    """
    刪除已上傳的圖片檔案（僅刪除圖片，不刪除CSV）

    Args:
        filename: 圖片檔案名稱

    Returns:
        刪除結果
    """
    try:
        # 刪除上傳的圖片
        image_path = os.path.join(settings.upload_dir, filename)
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="圖片檔案不存在")

        os.remove(image_path)
        logger.info(f"🗑️ 已刪除圖片: {filename}")

        # 同時刪除相關的暫存檔案（OCR和AI暫存）
        try:
            from app.services.cache_service import cache_service
            cache_service.delete_ocr_cache(filename)
            cache_service.delete_ai_cache(filename)
        except Exception as e:
            logger.warning(f"刪除暫存檔案失敗: {str(e)}")

        return {
            "success": True,
            "deleted_image": filename,
            "message": f"已刪除圖片: {filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除圖片失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")


@app.delete("/receipts/{filename}")
async def delete_receipt(filename: str):
    """
    刪除收據檔案（包含圖片和CSV）

    Args:
        filename: 檔案名稱

    Returns:
        刪除結果
    """
    try:
        # 刪除上傳的圖片
        image_path = os.path.join(settings.upload_dir, filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        # 刪除相關的CSV檔案
        base_name = os.path.splitext(filename)[0]
        csv_patterns = [
            f"receipt_*{base_name}*.csv",
            f"detailed_receipt_*{base_name}*.csv",
        ]

        deleted_files = []
        for pattern in csv_patterns:
            for file in os.listdir(settings.output_dir):
                if file.endswith(".csv") and base_name in file:
                    csv_path = os.path.join(settings.output_dir, file)
                    os.remove(csv_path)
                    deleted_files.append(file)

        logger.info(f"刪除收據檔案: {filename}, 同時刪除CSV檔案: {deleted_files}")

        return {
            "success": True,
            "deleted_image": filename,
            "deleted_csv_files": deleted_files,
        }

    except Exception as e:
        logger.error(f"刪除收據檔案失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
