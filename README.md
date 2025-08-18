# 📄 日本收據AI識別系統

一個基於AI的日本收據識別和數據提取系統，能夠自動處理收據圖片並生成結構化的CSV數據。

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 設定環境變數
複製 `.env.example` 到 `.env` 並填入您的API金鑰：
```bash
cp .env.example .env
```

### 啟動服務
```bash
python start.py
```

訪問 http://localhost:8000 開始使用

## 📋 主要功能

- 🔍 **智能OCR識別**: 使用Azure Computer Vision API進行文字識別
- 🤖 **AI數據提取**: 使用Claude AI進行結構化數據提取
- 📊 **CSV輸出**: 自動生成中文標題的CSV文件
- 🌐 **Web界面**: 友好的用戶界面，支援批量上傳
- ⚡ **批量處理**: 支援大量圖片的高效處理
- 💾 **快取機制**: 智能快取，避免重複處理
- 🗑️ **檔案管理**: 自動清理已處理的圖片

## 📚 文檔

### 🔧 使用指南
- **[API設定指南](./docs/guides/API_SETUP_GUIDE.md)** - 如何設定Azure和Claude API
- **[Azure成本指南](./docs/guides/AZURE_COST_GUIDE.md)** - 成本控制和優化建議
- **[使用說明](./docs/guides/USAGE.md)** - 詳細的使用指南

### 🎯 功能特性
- **[檔案管理功能](./docs/features/FILE_MANAGEMENT_SUMMARY.md)** - 自動檔案清理和管理
- **[性能優化](./docs/features/PERFORMANCE_OPTIMIZATION_SUMMARY.md)** - 系統性能優化詳情
- **[稅金處理功能](./docs/features/TAX_FEATURES_SUMMARY.md)** - 日本稅金識別和處理

### 🔧 開發設定
- **[GitHub設定](./docs/setup/GITHUB_SETUP.md)** - GitHub專案設定
- **[GitHub README](./docs/setup/README_GITHUB.md)** - GitHub專用說明

### 🐛 修復記錄
- **[系統修復總結](./docs/fixes/INTEGRATED_FIXES.md)** - 所有問題修復記錄
- **[批量處理修復](./docs/OPTIMIZED_BATCH_FIX_SUMMARY.md)** - 批量處理優化
- **[測試組織](./docs/TEST_ORGANIZATION_SUMMARY.md)** - 測試文件組織

## 🏗️ 系統架構

```
receipt_record/
├── app/                    # 主要應用程式
│   ├── main.py            # FastAPI主程式
│   ├── config.py          # 設定管理
│   ├── models/            # 數據模型
│   ├── services/          # 核心服務
│   └── utils/             # 工具函數
├── static/                # 前端文件
├── data/                  # 數據目錄
│   ├── receipts/          # 收據圖片
│   ├── output/            # CSV輸出
│   └── cache/             # 快取文件
├── tests/                 # 測試文件
└── docs/                  # 文檔目錄
```

## 🔧 技術棧

- **後端**: FastAPI, Python 3.8+
- **AI服務**: Azure Computer Vision, Claude 3.5 Sonnet
- **前端**: HTML, JavaScript
- **數據處理**: Pandas, CSV
- **圖片處理**: Pillow, OpenCV

## 📊 系統狀態

- ✅ 所有已知問題已修復
- ✅ 系統運行穩定
- ✅ 處理成功率: 100%
- ✅ 支援批量處理
- ✅ 智能快取機制

## 🤝 貢獻

歡迎提交Issue和Pull Request！

## 📄 授權

MIT License

---

**最後更新**: 2025-08-17  
**版本**: 1.0.0
