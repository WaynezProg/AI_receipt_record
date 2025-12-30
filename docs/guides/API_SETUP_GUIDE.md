# API金鑰設定指南

## 🔧 快速設定

### 1. 複製環境變數範本
```bash
cp env.example .env
```

### 2. 編輯.env檔案
```bash
nano .env
```

### 3. 填入您的API金鑰
```env
# Azure Computer Vision API設定
# 注意：端點URL不要包含尾隨斜線（/）
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_VISION_KEY=your_azure_vision_key_here

# Claude API設定
CLAUDE_API_KEY=your_claude_api_key_here

# 應用程式設定
DEBUG=True
LOG_LEVEL=INFO

# 檔案路徑設定
UPLOAD_DIR=./data/receipts
OUTPUT_DIR=./data/output

# 服務設定
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
```

## 📊 成本估算

### 每月使用100張收據的成本：

| 服務 | 使用量 | 成本 |
|------|--------|------|
| Azure Vision (F0) | 100次 | $0 (免費額度內) |
| Claude API | 100次 | $1-5 |
| **總計** | | **$1-5/月** |

### 每月使用1000張收據的成本：

| 服務 | 使用量 | 成本 |
|------|--------|------|
| Azure Vision (S1) | 1000次 | $1 |
| Claude API | 1000次 | $10-50 |
| **總計** | | **$11-51/月** |

## 🔄 替代方案

### OCR服務替代：
1. **Google Cloud Vision API**
   - 每月1000次免費
   - 之後每1000次$1.50

2. **AWS Textract**
   - 每月1000頁免費
   - 之後每1000頁$1.50

3. **Tesseract OCR** (免費)
   - 開源OCR引擎
   - 需要自行部署

### AI服務替代：
1. **OpenAI GPT-4**
   - 每1000個token約$0.03-0.06
   - 需要信用卡驗證

2. **本地AI模型**
   - 使用開源模型如Llama
   - 需要GPU資源

## 🧪 測試API金鑰

設定完成後，可以使用以下命令測試：

```bash
# 測試OCR服務
python test_ocr.py

# 測試完整流程
curl -X POST http://localhost:8000/process \
  -F "filename=test_receipt.jpg" \
  -F "enhance_image=true" \
  -F "save_detailed_csv=true"
```

## ⚠️ 注意事項

1. **安全性**：不要將API金鑰提交到Git
2. **額度監控**：定期檢查API使用量
3. **備份**：保存API金鑰的安全備份
4. **測試**：先在測試環境驗證

## 🆘 常見問題

### Q: 免費額度用完怎麼辦？
A: 可以升級到付費方案，或切換到其他服務

### Q: API金鑰洩露怎麼辦？
A: 立即在對應平台重新生成金鑰

### Q: 處理速度慢怎麼辦？
A: 可以調整圖片品質或使用更快的模型
