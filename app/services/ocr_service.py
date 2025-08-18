import os
import time
import requests
import json
from typing import Dict, List, Optional, Tuple
from loguru import logger
from app.config import settings
import asyncio
from app.services.azure_usage_tracker import azure_usage_tracker


class OCRService:
    """Azure Computer Vision OCR服務"""
    
    def __init__(self):
        self.endpoint = settings.azure_vision_endpoint
        self.key = settings.azure_vision_key
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-Type': 'application/octet-stream'
        }
        
        # 檢查是否為測試模式
        self.test_mode = (
            'your-resource.cognitiveservices.azure.com' in self.endpoint or
            'your_azure_vision_key_here' in self.key or
            not self.endpoint or
            not self.key
        )
        
        if self.test_mode:
            logger.warning("🔧 OCR服務運行在測試模式 - 使用模擬數據")

    async def extract_text(self, image_path: str) -> Dict:
        """
        從圖片中提取文字
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            包含文字和位置資訊的字典
        """
        if self.test_mode:
            return self._get_mock_ocr_result(image_path)
            
        try:
            start_time = time.time()
            
            # 讀取圖片檔案
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # 檢查圖片大小限制
            image_size = len(image_data)
            if image_size > azure_usage_tracker.max_image_size:
                logger.warning(f"圖片大小超過4MB限制: {image_size / (1024*1024):.2f}MB")
            
            # 發送OCR請求
            logger.info(f"發送OCR請求到Azure: {image_path}")
            response = requests.post(
                f"{self.endpoint}/vision/v3.2/read/analyze",
                headers=self.headers,
                data=image_data
            )
            
            if response.status_code == 202:
                # 獲取操作位置
                operation_location = response.headers['Operation-Location']
                
                # 等待處理完成
                logger.info("等待OCR處理完成...")
                while True:
                    await asyncio.sleep(1)
                    result_response = requests.get(operation_location, headers=self.headers)
                    
                    if result_response.status_code == 200:
                        result = result_response.json()
                        if result['status'] == 'succeeded':
                            processing_time = time.time() - start_time
                            logger.info("OCR處理完成")
                            
                            # 記錄API使用量
                            azure_usage_tracker.record_api_call(
                                image_size=image_size,
                                processing_time=processing_time,
                                success=True
                            )
                            
                            return self._parse_ocr_result(result, processing_time)
                        elif result['status'] == 'failed':
                            processing_time = time.time() - start_time
                            
                            # 記錄失敗的API調用
                            azure_usage_tracker.record_api_call(
                                image_size=image_size,
                                processing_time=processing_time,
                                success=False
                            )
                            
                            raise Exception(f"OCR處理失敗: {result.get('error', {}).get('message', '未知錯誤')}")
                    else:
                        raise Exception(f"獲取OCR結果失敗: {result_response.status_code}")
            else:
                raise Exception(f"OCR請求失敗: {response.status_code} - {response.text}")
                
        except Exception as e:
            error_msg = str(e)
            
            # 特殊處理429錯誤（請求頻率超限）
            if "429" in error_msg:
                logger.warning(f"Azure API請求頻率超限 (429)，需要等待重試: {error_msg}")
                # 拋出特殊的429錯誤，讓調用方知道需要等待
                raise Exception(f"RATE_LIMIT_EXCEEDED: {error_msg}")
            else:
                logger.error(f"OCR處理錯誤: {error_msg}")
                raise

    def _get_mock_ocr_result(self, image_path: str) -> Dict:
        """返回模擬的OCR結果"""
        logger.info("使用模擬OCR數據")
        
        # 模擬日文收據的OCR結果
        mock_result = {
            "status": "succeeded",
            "analyzeResult": {
                "readResults": [
                    {
                        "page": 1,
                        "lines": [
                            {
                                "boundingBox": [10, 10, 100, 20],
                                "text": "セブン-イレブン",
                                "words": [{"text": "セブン-イレブン", "confidence": 0.95}]
                            },
                            {
                                "boundingBox": [10, 30, 80, 40],
                                "text": "2024年8月17日",
                                "words": [{"text": "2024年8月17日", "confidence": 0.92}]
                            },
                            {
                                "boundingBox": [10, 50, 60, 60],
                                "text": "14:30",
                                "words": [{"text": "14:30", "confidence": 0.89}]
                            },
                            {
                                "boundingBox": [10, 80, 120, 90],
                                "text": "おにぎり 税込 120円",
                                "words": [
                                    {"text": "おにぎり", "confidence": 0.88},
                                    {"text": "税込", "confidence": 0.85},
                                    {"text": "120円", "confidence": 0.90}
                                ]
                            },
                            {
                                "boundingBox": [10, 110, 120, 120],
                                "text": "コーヒー 税込 150円",
                                "words": [
                                    {"text": "コーヒー", "confidence": 0.87},
                                    {"text": "税込", "confidence": 0.85},
                                    {"text": "150円", "confidence": 0.91}
                                ]
                            },
                            {
                                "boundingBox": [10, 150, 80, 160],
                                "text": "合計 270円",
                                "words": [
                                    {"text": "合計", "confidence": 0.86},
                                    {"text": "270円", "confidence": 0.93}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        return self._parse_ocr_result(mock_result, time.time())

    def _parse_ocr_result(self, result: Dict, processing_time: float) -> Dict:
        """
        解析OCR結果
        
        Args:
            result: OCR API返回的結果
            processing_time: 處理時間
            
        Returns:
            解析後的文字資料
        """
        try:
            if result.get('status') != 'succeeded':
                raise Exception(f"OCR處理未成功: {result.get('status')}")
            
            analyze_result = result.get('analyzeResult', {})
            read_results = analyze_result.get('readResults', [])
            
            if not read_results:
                raise Exception("OCR結果中沒有找到文字")
            
            # 提取所有文字
            all_text = []
            all_words = []
            
            for page in read_results:
                for line in page.get('lines', []):
                    line_text = line.get('text', '')
                    all_text.append(line_text)
                    
                    for word in line.get('words', []):
                        all_words.append({
                            'text': word.get('text', ''),
                            'confidence': word.get('confidence', 0.0),
                            'boundingBox': word.get('boundingBox', [])
                        })
            
            return {
                'success': True,
                'text': '\n'.join(all_text),
                'words': all_words,
                'processing_time': processing_time,
                'confidence': sum(w.get('confidence', 0) for w in all_words) / len(all_words) if all_words else 0.0
            }
            
        except Exception as e:
            logger.error(f"解析OCR結果失敗: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'words': [],
                'processing_time': processing_time,
                'confidence': 0.0
            }
    
    def extract_structured_data(self, ocr_result: Dict) -> Dict:
        """
        從OCR結果中提取結構化資料
        
        Args:
            ocr_result: OCR處理結果
            
        Returns:
            結構化資料
        """
        if not ocr_result.get('success'):
            return {}
        
        text = ocr_result.get('text', '')
        words = ocr_result.get('words', [])
        
        # 提取數字（金額）
        import re
        numbers = []
        for word in words:
            word_text = word.get('text', '')
            # 匹配日圓金額格式
            yen_matches = re.findall(r'(\d+)円', word_text)
            numbers.extend([int(match) for match in yen_matches])
        
        # 提取日期
        dates = []
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    dates.append(f"{match[0]}-{match[1].zfill(2)}-{match[2].zfill(2)}")
        
        # 提取時間
        times = []
        time_patterns = [
            r'(\d{1,2}):(\d{2})',
            r'(\d{1,2})時(\d{2})分'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 2:
                    times.append(f"{match[0].zfill(2)}:{match[1]}")
        
        # 提取商店名稱（通常是第一行或包含特定關鍵字的行）
        store_names = []
        lines = text.split('\n')
        for line in lines[:3]:  # 檢查前3行
            if any(keyword in line for keyword in ['セブン', 'イレブン', 'ファミマ', 'ローソン', 'コンビニ', 'スーパー']):
                store_names.append(line.strip())
        
        return {
            'numbers': numbers,
            'dates': dates,
            'times': times,
            'store_names': store_names,
            'total_amount': max(numbers) if numbers else 0,
            'items_count': len([w for w in words if '円' in w.get('text', '')])
        }
    
    def _extract_numbers(self, words: List[Dict]) -> List[float]:
        """提取數字"""
        numbers = []
        for word in words:
            text = word['text']
            # 移除日圓符號和逗號，提取數字
            cleaned_text = text.replace('¥', '').replace(',', '').replace('円', '')
            try:
                if cleaned_text.replace('.', '').isdigit():
                    numbers.append(float(cleaned_text))
            except ValueError:
                continue
        return numbers
    
    def _extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        import re
        # 日文日期格式：2024年1月1日、2024/1/1、2024-01-01等
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}/\d{1,2}/\d{1,2}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    def _extract_store_names(self, text: str) -> List[str]:
        """提取可能的商店名稱"""
        # 簡單的商店名稱提取邏輯
        # 可以根據實際需求優化
        lines = text.split('\n')
        store_names = []
        
        for line in lines:
            line = line.strip()
            # 排除包含數字的行（通常是價格）
            if line and not any(char.isdigit() for char in line):
                # 排除常見的非商店名稱詞彙
                exclude_words = ['合計', '小計', '税', '税込', '現金', 'カード', 'ポイント']
                if not any(word in line for word in exclude_words):
                    store_names.append(line)
        
        return store_names[:3]  # 返回前3個可能的商店名稱


# 全域OCR服務實例
ocr_service = OCRService()
