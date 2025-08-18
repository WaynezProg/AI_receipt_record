import json
import time
import httpx
from typing import Dict, Optional
from loguru import logger
from app.config import settings
from app.models.receipt import ReceiptData, ReceiptItem


class AIService:
    """Claude AI服務，用於文字整理和結構化"""
    
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # 檢查是否為測試模式
        self.test_mode = 'your_claude_api_key_here' in self.api_key
        
        if self.test_mode:
            logger.warning("🔧 AI服務運行在測試模式 - 使用模擬數據")

    async def process_receipt_text(self, ocr_data: Dict, structured_data: Dict) -> ReceiptData:
        """使用AI處理收據文字並結構化資料"""
        if self.test_mode:
            return self._get_mock_receipt_data(ocr_data, structured_data)
            
        try:
            # 構建提示詞
            prompt = self._build_receipt_prompt(ocr_data, structured_data)
            
            # 調用Claude API
            response_text = await self._call_claude_api(prompt)
            
            # 解析回應
            receipt_data = self._parse_ai_response(response_text, ocr_data)
            
            logger.info("AI處理完成")
            return receipt_data
            
        except Exception as e:
            logger.error(f"AI處理失敗: {str(e)}")
            raise

    def _get_mock_receipt_data(self, ocr_data: Dict, structured_data: Dict) -> ReceiptData:
        """返回模擬的收據數據"""
        logger.info("使用模擬AI數據")
        
        # 從OCR數據中提取信息
        text = ocr_data.get('text', '')
        numbers = structured_data.get('numbers', [])
        dates = structured_data.get('dates', [])
        times = structured_data.get('times', [])
        store_names = structured_data.get('store_names', [])
        
        # 創建模擬收據數據
        from datetime import datetime
        
        # 解析日期和時間
        receipt_date = datetime.now()
        if dates:
            try:
                receipt_date = datetime.strptime(dates[0], '%Y-%m-%d')
            except:
                pass
        
        receipt_time = "14:30"
        if times:
            receipt_time = times[0]
        
        # 解析商品項目
        items = []
        lines = text.split('\n')
        for line in lines:
            if '円' in line and any(keyword in line for keyword in ['おにぎり', 'コーヒー', 'パン', 'お茶']):
                # 簡單的商品解析
                if 'おにぎり' in line:
                    items.append(ReceiptItem(
                        name="おにぎり", 
                        name_japanese="おにぎり",
                        name_chinese="飯糰",
                        price=120.0, 
                        quantity=1,
                        tax_included=True,
                        tax_amount=12.0
                    ))
                elif 'コーヒー' in line:
                    items.append(ReceiptItem(
                        name="コーヒー", 
                        name_japanese="コーヒー",
                        name_chinese="咖啡",
                        price=150.0, 
                        quantity=1,
                        tax_included=True,
                        tax_amount=15.0
                    ))
                elif 'パン' in line:
                    items.append(ReceiptItem(
                        name="パン", 
                        name_japanese="パン",
                        name_chinese="麵包",
                        price=100.0, 
                        quantity=1,
                        tax_included=True,
                        tax_amount=10.0
                    ))
                elif 'お茶' in line:
                    items.append(ReceiptItem(
                        name="お茶", 
                        name_japanese="お茶",
                        name_chinese="茶",
                        price=80.0, 
                        quantity=1,
                        tax_included=True,
                        tax_amount=8.0
                    ))
        
        # 如果沒有解析到商品，添加默認商品
        if not items:
            items = [
                ReceiptItem(
                    name="おにぎり", 
                    name_japanese="おにぎり",
                    name_chinese="飯糰",
                    price=120.0, 
                    quantity=1,
                    tax_included=True,
                    tax_amount=12.0
                ),
                ReceiptItem(
                    name="コーヒー", 
                    name_japanese="コーヒー",
                    name_chinese="咖啡",
                    price=150.0, 
                    quantity=1,
                    tax_included=True,
                    tax_amount=15.0
                )
            ]
        
        # 計算總金額
        total_amount = sum(item.price * item.quantity for item in items)
        
        return ReceiptData(
            store_name=store_names[0] if store_names else "セブン-イレブン",
            date=receipt_date,
            total_amount=total_amount,
            items=items,
            payment_method="現金",
            receipt_number="TEST001",
            tax_amount=total_amount * 0.1,  # 假設10%稅
            subtotal=total_amount * 0.9,
            tax_type="內含稅",
            confidence_score=ocr_data.get('confidence', 0.85),
            processing_time=0.5,
            source_image="test_receipt.jpg"
        )

    def _build_receipt_prompt(self, ocr_data: Dict, structured_data: Dict) -> str:
        """構建AI提示詞"""
        text = ocr_data.get('text', '')
        confidence = ocr_data.get('confidence', 0.0)
        
        prompt = f"""
請分析以下日本收據的文字內容，並將其結構化為JSON格式。

收據文字內容：
{text}

識別信心度：{confidence:.2f}

請嚴格按照以下JSON格式返回，不要添加任何其他文字說明：

{{
  "store_name": "商店名稱",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 數字,
  "items": [
    {{
      "name": "原始商品名稱",
      "name_japanese": "日文原名",
      "name_chinese": "繁體中文翻譯",
      "price": 數字,
      "quantity": 數字,
      "tax_included": true/false,
      "tax_amount": 數字
    }}
  ],
  "payment_method": "支付方式",
  "receipt_number": "收據號碼",
  "tax_amount": 數字,
  "subtotal": 數字,
  "tax_type": "內含稅" 或 "外加稅"
}}

重要要求：
1. 必須是有效的JSON格式
2. tax_type 必須是字符串，不是對象
3. 所有數字欄位必須是數字，不是字符串
4. 不要包含任何註釋或說明文字
5. 確保JSON語法正確，沒有多餘的逗號
"""
        return prompt

    async def _call_claude_api(self, prompt: str) -> str:
        """調用Claude API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                                    json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['content'][0]['text']
                else:
                    raise Exception(f"Claude API調用失敗: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Claude API調用錯誤: {str(e)}")
            raise

    def _parse_ai_response(self, response: str, ocr_data: Dict) -> ReceiptData:
        """解析AI回應"""
        try:
            # 由於使用了JSON模式，直接解析整個回應
            try:
                data = json.loads(response)
            except json.JSONDecodeError as e:
                # 如果直接解析失敗，嘗試提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    data = json.loads(json_str)
                else:
                    raise Exception(f"無法找到有效的JSON格式: {str(e)}")
            
            # 安全的數值轉換函數
            def safe_float(value, default=0.0):
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                else:
                    return default
            
            def safe_int(value, default=1):
                if isinstance(value, (int, float)):
                    return int(value)
                elif isinstance(value, str):
                    try:
                        return int(float(value))
                    except (ValueError, TypeError):
                        return default
                else:
                    return default
            
            # 解析日期
            from datetime import datetime
            date_str = data.get('date', '')
            receipt_date = datetime.now()
            if date_str:
                try:
                    receipt_date = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    pass
            
            # 解析商品項目
            items = []
            for item_data in data.get('items', []):
                items.append(ReceiptItem(
                    name=item_data.get('name', ''),
                    name_japanese=item_data.get('name_japanese'),
                    name_chinese=item_data.get('name_chinese'),
                    price=safe_float(item_data.get('price', 0)),
                    quantity=safe_int(item_data.get('quantity', 1)),
                    tax_included=item_data.get('tax_included'),
                    tax_amount=safe_float(item_data.get('tax_amount', 0))
                ))
            
            # 處理tax_type，確保它是字符串
            tax_type = data.get('tax_type', '')
            if isinstance(tax_type, dict):
                # 如果是字典，嘗試提取有用信息
                if 'standard_rate' in tax_type:
                    tax_type = "內含稅"
                elif 'reduced_rate' in tax_type:
                    tax_type = "內含稅"
                else:
                    tax_type = "內含稅"
            elif not isinstance(tax_type, str):
                tax_type = str(tax_type) if tax_type else "內含稅"
            
            return ReceiptData(
                store_name=data.get('store_name', ''),
                date=receipt_date,
                total_amount=safe_float(data.get('total_amount', 0)),
                items=items,
                payment_method=data.get('payment_method', ''),
                receipt_number=data.get('receipt_number', ''),
                tax_amount=safe_float(data.get('tax_amount', 0)),
                subtotal=safe_float(data.get('subtotal', 0)),
                tax_type=tax_type,
                confidence_score=ocr_data.get('confidence', 0.0),
                processing_time=0.0,
                source_image=""
            )
            
        except Exception as e:
            logger.error(f"解析AI回應失敗: {str(e)}")
            raise

    async def validate_receipt_data(self, receipt_data: ReceiptData) -> Dict:
        """驗證收據數據"""
        if self.test_mode:
            return {"valid": True, "confidence": 0.9, "issues": []}
            
        try:
            # 構建驗證提示詞
            prompt = f"""
請驗證以下收據數據的合理性：

商店名稱：{receipt_data.store_name}
日期：{receipt_data.date}
總金額：{receipt_data.total_amount}円
商品數量：{len(receipt_data.items)}個

請檢查：
1. 金額是否合理
2. 日期是否有效
3. 商品價格是否正常
4. 是否有明顯錯誤

請以JSON格式返回驗證結果：
{{
    "valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["問題1", "問題2"]
}}
"""
            
            response_text = await self._call_claude_api(prompt)
            
            # 解析驗證結果
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"valid": True, "confidence": 0.8, "issues": []}
                
        except Exception as e:
            logger.error(f"驗證收據數據失敗: {str(e)}")
            return {"valid": True, "confidence": 0.7, "issues": ["驗證過程出現錯誤"]}

ai_service = AIService()
