# 🇯🇵 日本收據識別系統

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基於OCR + AI的智能日本收據識別系統，能夠自動識別收據照片中的關鍵資訊並輸出為CSV格式。

## ✨ 功能特色

- 🖼️ **多格式支援**：JPG、PNG、PDF格式
- 🇯🇵 **日文優化**：專門針對日文收據設計
- 🤖 **AI驅動**：結合OCR和AI，提供高準確性識別
- 📊 **CSV輸出**：自動生成結構化資料
- 💰 **成本優化**：每次識別成本僅$0.002-0.0035
- 🌐 **Web介面**：現代化的響應式設計

## 🚀 快速開始

### 前置需求

- Python 3.8+
- Azure Computer Vision API 金鑰
- Claude API 金鑰

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/yourusername/receipt_record.git
cd receipt_record
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **設定環境變數**
```bash
cp env.example .env
# 編輯 .env 檔案，填入您的API金鑰
```

4. **啟動系統**
```bash
python start.py
```

5. **開啟瀏覽器**
訪問 http://localhost:8000

## 📋 識別內容

| 項目 | 說明 | 範例 |
|------|------|------|
| 🏪 商店名稱 | 收據上的商店名稱 | セブン-イレブン |
| 📅 日期 | 收據日期 | 2024-01-15 |
| 💰 總金額 | 收據總金額 | ¥1,250 |
| 🛒 商品明細 | 購買的商品清單 | コーヒー ¥150 |
| 📊 稅額 | 消費稅金額 | ¥125 |
| 💳 付款方式 | 付款方式 | 現金/カード |

## 🏗️ 技術架構

```
receipt_record/
├── app/                    # FastAPI應用程式
│   ├── services/          # 服務層
│   │   ├── ocr_service.py # Azure OCR服務
│   │   ├── ai_service.py  # Claude AI服務
│   │   └── csv_service.py # CSV處理服務
│   ├── models/            # 資料模型
│   └── utils/             # 工具函數
├── static/                # Web前端
├── data/                  # 資料目錄
└── tests/                 # 測試檔案
```

## 🔧 API端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | Web介面 |
| `/docs` | GET | API文檔 |
| `/upload` | POST | 上傳收據圖片 |
| `/process` | POST | 處理收據識別 |
| `/receipts` | GET | 獲取收據列表 |
| `/download/{filename}` | GET | 下載CSV檔案 |

## 💡 使用範例

### 上傳收據圖片
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@receipt.jpg"
```

### 處理收據識別
```bash
curl -X POST "http://localhost:8000/process" \
     -H "Content-Type: application/json" \
     -d '{"filename": "receipt_20240115_120000.jpg"}'
```

## 🧪 測試

運行測試腳本：
```bash
python test_ocr.py
```

## 📊 成本分析

| 服務 | 成本/次 | 說明 |
|------|---------|------|
| Azure OCR | $0.0015 | 文字識別 |
| Claude AI | $0.0005-0.002 | 語義理解 |
| **總計** | **$0.002-0.0035** | **每次識別** |

## 🔒 安全性

- ✅ API金鑰保護
- ✅ 檔案格式驗證
- ✅ 檔案大小限制
- ✅ 錯誤處理機制

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/receipt_record/issues)
- 📖 文檔: [USAGE.md](USAGE.md)

## 🙏 致謝

- [Azure Computer Vision](https://azure.microsoft.com/services/cognitive-services/computer-vision/) - OCR服務
- [Claude AI](https://www.anthropic.com/) - AI語義理解
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 資料驗證

---

⭐ 如果這個專案對您有幫助，請給我們一個星標！
