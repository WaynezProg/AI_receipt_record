import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional
from loguru import logger


class ImageUtils:
    """圖片處理工具類"""

    @staticmethod
    def validate_image(file_path: str, max_size: int = 10485760) -> bool:
        """
        驗證圖片檔案

        Args:
            file_path: 圖片檔案路徑
            max_size: 最大檔案大小（位元組）

        Returns:
            是否有效
        """
        try:
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                return False

            # 檢查檔案大小
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                logger.error(f"檔案太大: {file_size} bytes > {max_size} bytes")
                return False

            # 檢查檔案格式
            allowed_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext not in allowed_extensions:
                logger.error(f"不支援的檔案格式: {file_ext}")
                return False

            # 嘗試開啟圖片
            with Image.open(file_path) as img:
                img.verify()

            logger.info(f"圖片驗證成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"圖片驗證失敗: {str(e)}")
            return False

    @staticmethod
    def preprocess_image(file_path: str, output_path: Optional[str] = None) -> str:
        """
        預處理圖片以提高OCR準確性

        Args:
            file_path: 輸入圖片路徑
            output_path: 輸出圖片路徑（可選）

        Returns:
            處理後的圖片路徑
        """
        try:
            # 讀取圖片
            image = cv2.imread(file_path)
            if image is None:
                raise Exception("無法讀取圖片")

            # 轉換為灰度圖
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 應用高斯模糊減少雜訊
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 應用自適應閾值處理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # 形態學操作改善文字品質
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # 確定輸出路徑
            if output_path is None:
                base_name = os.path.splitext(file_path)[0]
                output_path = f"{base_name}_processed.jpg"

            # 儲存處理後的圖片
            cv2.imwrite(output_path, processed)

            logger.info(f"圖片預處理完成: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"圖片預處理失敗: {str(e)}")
            raise

    @staticmethod
    def enhance_image_quality(
        file_path: str, output_path: Optional[str] = None, max_size_mb: float = 4.0
    ) -> str:
        """
        增強圖片品質

        Args:
            file_path: 輸入圖片路徑
            output_path: 輸出圖片路徑（可選）
            max_size_mb: 最大檔案大小（MB）

        Returns:
            增強後的圖片路徑
        """
        try:
            # 檢查原始檔案大小
            original_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            logger.info(f"原始圖片大小: {original_size:.2f}MB")

            if original_size > max_size_mb:
                logger.warning(f"原始圖片已超過{max_size_mb}MB限制，跳過增強處理")
                return file_path

            # 使用PIL開啟圖片
            with Image.open(file_path) as img:
                # 轉換為RGB模式
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 增強對比度
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)

                # 增強銳度
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.2)

                # 增強亮度
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.1)

                # 確定輸出路徑
                if output_path is None:
                    base_name = os.path.splitext(file_path)[0]
                    output_path = f"{base_name}_enhanced.jpg"

                # 動態調整品質以控制檔案大小
                quality = 95
                while quality > 70:  # 最低品質限制
                    img.save(output_path, "JPEG", quality=quality, optimize=True)

                    # 檢查增強後的檔案大小
                    enhanced_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                    logger.info(
                        f"增強後圖片大小: {enhanced_size:.2f}MB (品質: {quality})"
                    )

                    # 如果檔案大小在限制內，使用這個版本
                    if enhanced_size <= max_size_mb:
                        logger.info(f"圖片品質增強完成: {output_path}")
                        return output_path

                    # 如果檔案太大，降低品質重試
                    quality -= 5
                    logger.info(f"檔案太大，降低品質到 {quality}")

                # 如果所有品質都太大，使用原始圖片
                logger.warning(f"無法在品質限制內達到檔案大小要求，使用原始圖片")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return file_path

        except Exception as e:
            logger.error(f"圖片品質增強失敗: {str(e)}")
            return file_path

    @staticmethod
    def resize_image(
        file_path: str,
        max_width: int = 1920,
        max_height: int = 1080,
        output_path: Optional[str] = None,
    ) -> str:
        """
        調整圖片大小

        Args:
            file_path: 輸入圖片路徑
            max_width: 最大寬度
            max_height: 最大高度
            output_path: 輸出圖片路徑（可選）

        Returns:
            調整後的圖片路徑
        """
        try:
            with Image.open(file_path) as img:
                # 獲取原始尺寸
                width, height = img.size

                # 計算縮放比例
                scale = min(max_width / width, max_height / height, 1.0)

                if scale < 1.0:
                    # 調整大小
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # 確定輸出路徑
                    if output_path is None:
                        base_name = os.path.splitext(file_path)[0]
                        output_path = f"{base_name}_resized.jpg"

                    # 儲存調整後的圖片
                    img.save(output_path, "JPEG", quality=95)

                    logger.info(f"圖片大小調整完成: {output_path}")
                    return output_path
                else:
                    # 圖片已經在允許範圍內，直接返回原路徑
                    logger.info("圖片大小已在允許範圍內")
                    return file_path

        except Exception as e:
            logger.error(f"圖片大小調整失敗: {str(e)}")
            raise

    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """
        獲取圖片資訊

        Args:
            file_path: 圖片檔案路徑

        Returns:
            圖片資訊字典
        """
        try:
            with Image.open(file_path) as img:
                info = {
                    "filename": os.path.basename(file_path),
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "file_size": os.path.getsize(file_path),
                }

                # 嘗試獲取EXIF資訊
                try:
                    exif = img._getexif()
                    if exif:
                        info["has_exif"] = True
                        # 提取拍攝時間
                        if 36867 in exif:  # DateTimeOriginal
                            info["capture_time"] = exif[36867]
                except:
                    info["has_exif"] = False

                return info

        except Exception as e:
            logger.error(f"獲取圖片資訊失敗: {str(e)}")
            raise

    @staticmethod
    def create_thumbnail(
        file_path: str,
        size: Tuple[int, int] = (200, 200),
        output_path: Optional[str] = None,
    ) -> str:
        """
        創建縮圖

        Args:
            file_path: 輸入圖片路徑
            size: 縮圖尺寸 (寬度, 高度)
            output_path: 輸出圖片路徑（可選）

        Returns:
            縮圖路徑
        """
        try:
            with Image.open(file_path) as img:
                # 轉換為RGB模式
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 創建縮圖
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # 確定輸出路徑
                if output_path is None:
                    base_name = os.path.splitext(file_path)[0]
                    output_path = f"{base_name}_thumb.jpg"

                # 儲存縮圖
                img.save(output_path, "JPEG", quality=85)

                logger.info(f"縮圖創建完成: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"縮圖創建失敗: {str(e)}")
            raise


# 全域圖片工具實例
image_utils = ImageUtils()
