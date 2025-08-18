import os
import csv
import json
from datetime import datetime
from typing import List, Dict
from loguru import logger
from app.config import settings
from app.models.receipt import ReceiptData, ReceiptItem


class CSVService:
    """CSV檔案處理服務"""
    
    def __init__(self):
        self.output_dir = settings.output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """確保輸出目錄存在"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_receipt_to_csv(self, receipt_data: ReceiptData, filename: str = None) -> str:
        """
        將單個收據資料儲存到CSV檔案
        
        Args:
            receipt_data: 收據資料
            filename: 檔案名稱（可選）
            
        Returns:
            CSV檔案路徑
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipt_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 準備CSV資料
            csv_data = self._prepare_csv_data(receipt_data)
            
            # 寫入CSV檔案
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # 中文欄位名稱
                fieldnames = [
                    '商店名稱', '日期', '總金額', '小計', 
                    '稅額', '稅率', '稅金類型', '收據號碼', '付款方式',
                    '識別信心度', '處理時間', '來源圖片'
                ]
                
                # 對應的英文欄位名稱
                english_fieldnames = [
                    'store_name', 'date', 'total_amount', 'subtotal', 
                    'tax_amount', 'tax_rate', 'tax_type', 'receipt_number', 'payment_method',
                    'confidence_score', 'processing_time', 'source_image'
                ]
                
                # 創建中文標題行
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                
                # 寫入資料行
                row_data = [csv_data[field] for field in english_fieldnames]
                writer.writerow(row_data)
            
            logger.info(f"收據資料已儲存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"儲存CSV檔案失敗: {str(e)}")
            raise
    
    def save_receipts_to_csv(self, receipts: List[ReceiptData], filename: str = None) -> str:
        """
        將多個收據資料儲存到CSV檔案（收據摘要）
        
        Args:
            receipts: 收據資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            CSV檔案路徑
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipts_summary_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 準備CSV資料
            csv_data_list = [self._prepare_csv_data(receipt) for receipt in receipts]
            
            # 寫入CSV檔案
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # 中文欄位名稱
                fieldnames = [
                    '商店名稱', '日期', '總金額', '小計', 
                    '稅額', '稅率', '稅金類型', '收據號碼', '付款方式',
                    '識別信心度', '處理時間', '來源圖片'
                ]
                
                # 對應的英文欄位名稱
                english_fieldnames = [
                    'store_name', 'date', 'total_amount', 'subtotal', 
                    'tax_amount', 'tax_rate', 'tax_type', 'receipt_number', 'payment_method',
                    'confidence_score', 'processing_time', 'source_image'
                ]
                
                # 創建中文標題行
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                
                # 寫入資料行
                for csv_data in csv_data_list:
                    row_data = [csv_data[field] for field in english_fieldnames]
                    writer.writerow(row_data)
            
            logger.info(f"收據摘要已儲存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"儲存CSV檔案失敗: {str(e)}")
            raise

    def save_consolidated_csv(self, receipts: List[ReceiptData], filename: str = None) -> Dict[str, str]:
        """
        創建整合的CSV檔案，包含收據摘要和詳細商品明細
        
        Args:
            receipts: 收據資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            包含兩個CSV檔案路徑的字典
        """
        try:
            # 類型檢查和轉換
            safe_receipts = []
            for receipt in receipts:
                if isinstance(receipt, dict):
                    logger.warning(f"發現字典類型數據，嘗試轉換: {type(receipt)}")
                    # 嘗試從字典創建ReceiptData對象
                    try:
                        from app.models.receipt import ReceiptItem
                        from datetime import datetime as dt
                        
                        # 創建ReceiptItem列表
                        items = []
                        for item_data in receipt.get('items', []):
                            if isinstance(item_data, dict):
                                item = ReceiptItem(
                                    name=item_data.get('name', ''),
                                    name_japanese=item_data.get('name_japanese', ''),
                                    name_chinese=item_data.get('name_chinese', ''),
                                    price=float(item_data.get('price', 0)),
                                    quantity=int(item_data.get('quantity', 1)),
                                    tax_included=item_data.get('tax_included', True),
                                    tax_amount=float(item_data.get('tax_amount', 0)) if item_data.get('tax_amount') else None
                                )
                                items.append(item)
                        
                        # 創建ReceiptData對象
                        receipt_obj = ReceiptData(
                            store_name=receipt.get('store_name', ''),
                            date=receipt.get('date', dt.now()),
                            total_amount=float(receipt.get('total_amount', 0)),
                            items=items,
                            source_image=receipt.get('source_image', ''),
                            confidence_score=float(receipt.get('confidence_score', 0.9)),
                            processing_time=float(receipt.get('processing_time', 1.0))
                        )
                        safe_receipts.append(receipt_obj)
                        logger.info(f"成功轉換字典為ReceiptData對象")
                    except Exception as e:
                        logger.error(f"轉換失敗: {e}")
                        continue
                elif isinstance(receipt, ReceiptData):
                    safe_receipts.append(receipt)
                else:
                    logger.warning(f"未知類型: {type(receipt)}")
                    continue
            
            if not safe_receipts:
                raise Exception("沒有有效的收據數據")
            
            logger.info(f"成功處理 {len(safe_receipts)} 個收據數據")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. 收據摘要CSV
            summary_filename = f"receipts_summary_{timestamp}.csv" if not filename else f"summary_{filename}"
            summary_path = self.save_receipts_to_csv(safe_receipts, summary_filename)
            
            # 2. 詳細商品明細CSV
            details_filename = f"receipts_details_{timestamp}.csv" if not filename else f"details_{filename}"
            details_path = self.save_detailed_items_csv(safe_receipts, details_filename)
            
            logger.info(f"整合CSV檔案已創建:")
            logger.info(f"   收據摘要: {summary_path}")
            logger.info(f"   商品明細: {details_path}")
            
            return {
                "summary_csv": summary_path,
                "details_csv": details_path
            }
            
        except Exception as e:
            logger.error(f"創建整合CSV失敗: {str(e)}")
            raise

    def save_detailed_items_csv(self, receipts: List[ReceiptData], filename: str = None) -> str:
        """
        將所有收據的商品明細儲存到一個CSV檔案
        
        Args:
            receipts: 收據資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            CSV檔案路徑
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipts_details_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 寫入詳細商品明細CSV檔案
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 寫入標題行
                writer.writerow([
                    '商店名稱', '收據日期', '商品名稱（原始）', 
                    '商品名稱（日文）', '商品名稱（中文）', '單價', '數量', '含稅', '稅額', '小計'
                ])
                
                # 寫入每個收據的商品明細
                for receipt in receipts:
                    for item in receipt.items:
                        tax_status = "含稅" if item.tax_included else "不含稅"
                        writer.writerow([
                            receipt.store_name,    # 商店名稱
                            receipt.date,          # 收據日期
                            item.name,             # 商品名稱（原始）
                            item.name_japanese or '',  # 商品名稱（日文）
                            item.name_chinese or '',   # 商品名稱（中文）
                            item.price,            # 單價
                            item.quantity,         # 數量
                            tax_status,            # 含稅狀態
                            item.tax_amount or '', # 稅額
                            item.price * item.quantity  # 小計
                        ])
            
            logger.info(f"詳細商品明細已儲存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"儲存詳細商品明細CSV失敗: {str(e)}")
            raise
    
    def _prepare_csv_data(self, receipt_data: ReceiptData) -> Dict:
        """
        準備CSV資料格式
        
        Args:
            receipt_data: 收據資料
            
        Returns:
            CSV格式的字典資料
        """
        return {
            'store_name': receipt_data.store_name,
            'date': receipt_data.date,
            'total_amount': receipt_data.total_amount,
            'subtotal': receipt_data.subtotal or '',
            'tax_amount': receipt_data.tax_amount or '',
            'tax_rate': receipt_data.tax_rate or '',
            'tax_type': receipt_data.tax_type or '',
            'receipt_number': receipt_data.receipt_number or '',
            'payment_method': receipt_data.payment_method or '',
            'confidence_score': receipt_data.confidence_score,
            'processing_time': receipt_data.processing_time,
            'source_image': receipt_data.source_image
        }
    
    def save_detailed_csv(self, receipt_data: ReceiptData, filename: str = None) -> str:
        """
        儲存詳細的CSV檔案，包含商品明細
        
        Args:
            receipt_data: 收據資料
            filename: 檔案名稱（可選）
            
        Returns:
            CSV檔案路徑
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipt_detailed_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 寫入詳細CSV檔案
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # 寫入收據基本資訊
                writer = csv.writer(csvfile)
                writer.writerow(['收據基本資訊'])
                writer.writerow(['商店名稱', receipt_data.store_name])
                writer.writerow(['日期', receipt_data.date])
                writer.writerow(['總金額', receipt_data.total_amount])
                writer.writerow(['小計', receipt_data.subtotal or ''])
                writer.writerow(['稅額', receipt_data.tax_amount or ''])
                writer.writerow(['稅率', receipt_data.tax_rate or ''])
                writer.writerow(['收據號碼', receipt_data.receipt_number or ''])
                writer.writerow(['付款方式', receipt_data.payment_method or ''])
                writer.writerow(['信心度', receipt_data.confidence_score])
                writer.writerow(['處理時間', receipt_data.processing_time])
                writer.writerow(['來源圖片', receipt_data.source_image])
                writer.writerow([])  # 空行
                
                # 寫入商品明細
                if receipt_data.items:
                    writer.writerow(['商品明細'])
                    writer.writerow(['商品名稱（原始）', '商品名稱（日文）', '商品名稱（中文）', '價格', '數量', '含稅', '稅額', '小計'])
                    
                    for item in receipt_data.items:
                        subtotal = item.price * item.quantity
                        tax_status = "含稅" if item.tax_included else "不含稅"
                        writer.writerow([
                            item.name, 
                            item.name_japanese or '', 
                            item.name_chinese or '', 
                            item.price, 
                            item.quantity, 
                            tax_status,
                            item.tax_amount or '',
                            subtotal
                        ])
            
            logger.info(f"詳細收據資料已儲存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"儲存詳細CSV檔案失敗: {str(e)}")
            raise
    
    def load_receipts_from_csv(self, filepath: str) -> List[ReceiptData]:
        """
        從CSV檔案載入收據資料
        
        Args:
            filepath: CSV檔案路徑
            
        Returns:
            收據資料列表
        """
        try:
            receipts = []
            
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # 檢查檔案類型（收據摘要或商品明細）
                fieldnames = reader.fieldnames
                is_summary_csv = '商店名稱' in fieldnames and '日期' in fieldnames
                is_details_csv = '收據日期' in fieldnames and '商品名稱（原始）' in fieldnames
                
                if is_summary_csv:
                    # 處理收據摘要CSV
                    for row in reader:
                        try:
                            # 解析日期
                            date_str = row.get('日期', '')
                            if date_str:
                                try:
                                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                                        try:
                                            parsed_date = datetime.strptime(date_str, fmt)
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        parsed_date = datetime.now()
                                except:
                                    parsed_date = datetime.now()
                            else:
                                parsed_date = datetime.now()
                            
                            receipt_data = ReceiptData(
                                store_name=row.get('商店名稱', ''),
                                date=parsed_date,
                                total_amount=float(row.get('總金額', 0)),
                                subtotal=float(row.get('小計', 0)) if row.get('小計') else None,
                                tax_amount=float(row.get('稅額', 0)) if row.get('稅額') else None,
                                tax_rate=float(row.get('稅率', 0)) if row.get('稅率') else None,
                                tax_type=row.get('稅金類型', ''),
                                receipt_number=row.get('收據號碼', ''),
                                payment_method=row.get('付款方式', ''),
                                confidence_score=float(row.get('識別信心度', 0)),
                                processing_time=float(row.get('處理時間', 0)),
                                source_image=row.get('來源圖片', ''),
                                items=[]  # 商品項目需要從詳細CSV載入
                            )
                            receipts.append(receipt_data)
                        except Exception as e:
                            logger.error(f"解析收據摘要資料失敗: {str(e)}, 行: {row}")
                            continue
                            
                elif is_details_csv:
                    # 處理商品明細CSV - 按收據來源分組
                    receipt_groups = {}
                    
                    for row in reader:
                        try:
                            store_name = row.get('商店名稱', '')
                            
                            # 解析日期
                            date_str = row.get('收據日期', '')
                            if date_str:
                                try:
                                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                                        try:
                                            parsed_date = datetime.strptime(date_str, fmt)
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        parsed_date = datetime.now()
                                except:
                                    parsed_date = datetime.now()
                            else:
                                parsed_date = datetime.now()
                            
                            # 創建商品項目
                            tax_included = row.get('含稅', '') == '含稅'
                            tax_amount = float(row.get('稅額', 0)) if row.get('稅額', '') else None
                            
                            item = ReceiptItem(
                                name=row.get('商品名稱（原始）', ''),
                                name_japanese=row.get('商品名稱（日文）', ''),
                                name_chinese=row.get('商品名稱（中文）', ''),
                                price=float(row.get('單價', 0)),
                                quantity=int(row.get('數量', 1)),
                                tax_included=tax_included,
                                tax_amount=tax_amount
                            )
                            
                            # 按商店名稱和日期分組
                            receipt_key = f"{store_name}_{date_str}"
                            if receipt_key not in receipt_groups:
                                receipt_groups[receipt_key] = {
                                    'store_name': store_name,
                                    'date': parsed_date,
                                    'items': [],
                                    'total_amount': 0
                                }
                            
                            receipt_groups[receipt_key]['items'].append(item)
                            receipt_groups[receipt_key]['total_amount'] += item.price * item.quantity
                            
                        except Exception as e:
                            logger.error(f"解析商品明細資料失敗: {str(e)}, 行: {row}")
                            continue
                    
                    # 創建收據資料
                    for receipt_key, group_data in receipt_groups.items():
                        receipt_data = ReceiptData(
                            store_name=group_data['store_name'],
                            date=group_data['date'],
                            total_amount=group_data['total_amount'],
                            items=group_data['items'],
                            source_image=receipt_key,  # 使用receipt_key作為source_image
                            confidence_score=0.9,  # 預設值
                            processing_time=1.0    # 預設值
                        )
                        receipts.append(receipt_data)
                else:
                    logger.warning(f"未知的CSV格式: {filepath}")
                    return []
            
            logger.info(f"從CSV檔案載入了 {len(receipts)} 筆收據資料")
            return receipts
            
        except Exception as e:
            logger.error(f"載入CSV檔案失敗: {str(e)}")
            return []
    
    def get_csv_summary(self, filepath: str) -> Dict:
        """
        獲取CSV檔案的摘要資訊
        
        Args:
            filepath: CSV檔案路徑
            
        Returns:
            摘要資訊字典
        """
        try:
            receipts = self.load_receipts_from_csv(filepath)
            
            total_amount = sum(receipt.total_amount for receipt in receipts)
            avg_amount = total_amount / len(receipts) if receipts else 0
            store_count = len(set(receipt.store_name for receipt in receipts))
            
            return {
                'total_receipts': len(receipts),
                'total_amount': total_amount,
                'average_amount': avg_amount,
                'unique_stores': store_count,
                'date_range': {
                    'earliest': min(receipt.date for receipt in receipts) if receipts else None,
                    'latest': max(receipt.date for receipt in receipts) if receipts else None
                }
            }
            
        except Exception as e:
            logger.error(f"獲取CSV摘要失敗: {str(e)}")
            raise
    
    def export_to_json(self, receipts: List[ReceiptData], filename: str = None) -> str:
        """
        將收據資料匯出為JSON格式
        
        Args:
            receipts: 收據資料列表
            filename: 檔案名稱（可選）
            
        Returns:
            JSON檔案路徑
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"receipts_{timestamp}.json"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 轉換為JSON格式
            json_data = []
            for receipt in receipts:
                receipt_dict = receipt.dict()
                # 處理日期格式
                receipt_dict['date'] = receipt.date
                json_data.append(receipt_dict)
            
            # 寫入JSON檔案
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.info(f"收據資料已匯出到JSON: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"匯出JSON檔案失敗: {str(e)}")
            raise


# 全域CSV服務實例
csv_service = CSVService()
