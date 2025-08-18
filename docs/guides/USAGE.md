# 日本收據識別系統 - 使用說明

## 🚀 快速開始

### 1. 環境準備

#### 安裝Python依賴
```bash
pip install -r requirements.txt
```

#### 設定環境變數
1. 複製環境變數範例檔案：
```bash
cp env.example .env
```

2. 編輯 `.env` 檔案，填入您的API金鑰：
```env
# Azure Computer Vision API設定
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_VISION_KEY=your_azure_vision_key_here

# Claude API設定
CLAUDE_API_KEY=your_claude_api_key_here
```

### 2. 獲取API金鑰

#### Azure Computer Vision API
1. 前往 [Azure Portal](https://portal.azure.com/)
2. 建立新的 Computer Vision 資源
3. 在資源的「金鑰和端點」頁面獲取金鑰和端點URL

#### Claude API
1. 前往 [Anthropic Console](https://console.anthropic.com/)
2. 建立API金鑰
3. 複製金鑰到 `.env` 檔案

### 3. 啟動系統

#### 方法一：使用啟動腳本（推薦）
```bash
python start.py
```

#### 方法二：直接啟動
```bash
python app/main.py
```

#### 方法三：使用uvicorn
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 使用系統

1. 開啟瀏覽器訪問：http://localhost:8000
2. 上傳日本收據圖片
3. 點擊「開始識別」
4. 查看識別結果和下載CSV檔案

## 📋 功能特色

### 支援的檔案格式
- **圖片格式**：JPG、JPEG、PNG
- **文件格式**：PDF
- **檔案大小**：最大 10MB

### 識別內容
- 🏪 商店名稱
- 📅 收據日期
- 💰 總金額、小計、稅額
- 🛒 商品明細
- 📊 收據號碼、付款方式

### 輸出格式
- **CSV檔案**：標準格式，包含所有識別資訊
- **詳細CSV**：包含商品明細的完整資訊
- **JSON格式**：結構化資料輸出

## 🔧 API端點

### 主要端點
- `GET /` - Web介面
- `GET /docs` - API文檔
- `GET /health` - 健康檢查

### 收據處理
- `POST /upload` - 上傳收據圖片
- `POST /process` - 處理收據識別
- `GET /receipts` - 獲取已處理的收據列表
- `GET /download/{filename}` - 下載CSV檔案

### 系統管理
- `GET /summary` - 獲取系統摘要
- `DELETE /receipts/{filename}` - 刪除收據檔案

## 🧪 測試系統

### 運行測試腳本
```bash
python test_ocr.py
```

### 測試要求
1. 確保API金鑰已正確設定
2. 將測試收據圖片命名為 `test_receipt.jpg` 並放在專案根目錄
3. 運行測試腳本檢查OCR和AI服務

## 📁 專案結構

```
receipt_record/
├── app/                    # 主要應用程式
│   ├── main.py            # FastAPI主程式
│   ├── config.py          # 設定檔
│   ├── services/          # 服務層
│   │   ├── ocr_service.py # OCR服務
│   │   ├── ai_service.py  # AI服務
│   │   └── csv_service.py # CSV服務
│   ├── models/            # 資料模型
│   └── utils/             # 工具函數
├── data/                  # 資料目錄
│   ├── receipts/          # 上傳的收據圖片
│   └── output/            # 輸出的CSV檔案
├── static/                # 靜態檔案
│   └── index.html         # Web介面
├── tests/                 # 測試檔案
├── logs/                  # 日誌檔案
├── requirements.txt       # Python依賴
├── env.example           # 環境變數範例
├── start.py              # 啟動腳本
├── test_ocr.py           # 測試腳本
└── README.md             # 專案說明
```

## 💡 使用技巧

### 提高識別準確性
1. **圖片品質**：確保圖片清晰、光線充足
2. **角度**：盡量正面拍攝，避免傾斜
3. **大小**：圖片不要太小，建議至少 800x600 像素
4. **格式**：優先使用JPG格式，檔案大小控制在5MB以內

### 最佳實踐
1. **批量處理**：可以連續上傳多張收據
2. **定期備份**：定期下載CSV檔案作為備份
3. **檢查結果**：識別完成後檢查結果的準確性
4. **清理檔案**：定期清理不需要的圖片檔案

### 故障排除

#### 常見問題
1. **API金鑰錯誤**
   - 檢查 `.env` 檔案中的金鑰是否正確
   - 確認API服務是否正常運作

2. **圖片上傳失敗**
   - 檢查檔案格式是否支援
   - 確認檔案大小是否超過限制

3. **識別結果不準確**
   - 嘗試重新拍攝圖片
   - 檢查圖片品質和角度

4. **服務無法啟動**
   - 檢查Python版本（建議3.8+）
   - 確認所有依賴已正確安裝

#### 日誌查看
```bash
# 查看應用程式日誌
tail -f logs/app.log

# 查看錯誤日誌
grep "ERROR" logs/app.log
```

## 🔒 安全性注意事項

1. **API金鑰保護**：不要將 `.env` 檔案提交到版本控制系統
2. **檔案權限**：確保資料目錄有適當的讀寫權限
3. **網路安全**：在生產環境中使用HTTPS
4. **資料備份**：定期備份重要的收據資料

## 📞 支援

如果遇到問題，請檢查：
1. 日誌檔案中的錯誤訊息
2. API服務的狀態
3. 網路連接是否正常
4. 環境設定是否正確

## 🚀 未來規劃

- [ ] 支援更多語言（中文、英文等）
- [ ] 批量處理功能
- [ ] 移動端APP
- [ ] 雲端部署支援
- [ ] 更多輸出格式支援
