from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    """收據項目"""
    name: str = Field(..., description="商品名稱（原始）")
    name_japanese: Optional[str] = Field(None, description="商品名稱（日文原名）")
    name_chinese: Optional[str] = Field(None, description="商品名稱（繁體中文翻譯）")
    price: float = Field(..., description="商品價格")
    quantity: Optional[int] = Field(1, description="數量")
    tax_included: Optional[bool] = Field(None, description="價格是否含稅")
    tax_amount: Optional[float] = Field(None, description="商品稅額")


class ReceiptData(BaseModel):
    """收據資料模型"""
    # 基本資訊
    store_name: str = Field(..., description="商店名稱")
    date: datetime = Field(..., description="收據日期")
    total_amount: float = Field(..., description="總金額")
    
    # 詳細資訊
    subtotal: Optional[float] = Field(None, description="小計")
    tax_amount: Optional[float] = Field(None, description="稅額")
    tax_rate: Optional[float] = Field(None, description="稅率")
    tax_type: Optional[str] = Field(None, description="稅金類型：內含稅/外加稅")
    
    # 商品明細
    items: List[ReceiptItem] = Field(default_factory=list, description="商品明細")
    
    # 其他資訊
    receipt_number: Optional[str] = Field(None, description="收據號碼")
    payment_method: Optional[str] = Field(None, description="付款方式")
    
    # 處理資訊
    confidence_score: float = Field(..., description="識別信心度")
    processing_time: float = Field(..., description="處理時間(秒)")
    source_image: str = Field(..., description="來源圖片檔案名")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReceiptResponse(BaseModel):
    """收據識別回應"""
    success: bool = Field(..., description="處理是否成功")
    data: Optional[ReceiptData] = Field(None, description="收據資料")
    error: Optional[str] = Field(None, description="錯誤訊息")
    processing_time: float = Field(..., description="總處理時間")


class ReceiptListResponse(BaseModel):
    """收據列表回應"""
    receipts: List[ReceiptData] = Field(..., description="收據列表")
    total_count: int = Field(..., description="總數量")
