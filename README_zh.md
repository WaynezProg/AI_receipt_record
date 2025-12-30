# 📄 日本收據AI識別系統

[![Demo Video](https://img.youtube.com/vi/Ur5AVAt0oT4/0.jpg)](https://youtu.be/Ur5AVAt0oT4)

> 💡 **點擊上圖觀看完整示範影片**，展示應用程式的完整工作流程。

> 🇬🇧 [English Version](./README.md) | 🇹🇼 [繁體中文版本](./README_zh.md)

一個基於AI的日本收據識別和數據提取系統，能夠自動處理收據圖片並生成結構化的CSV數據。整合 **Azure Computer Vision API** 進行文字識別，使用 **Claude 4.5 Sonnet** 進行智能結構化數據提取。

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

#### 方法一：使用快速啟動腳本（推薦）
```bash
./start.sh
```

#### 方法二：使用 Python 啟動腳本
```bash
python start.py
```

#### 啟動選項
```bash
# 使用自訂端口
./start.sh -p 8080

# 生產模式（禁用自動重載）
./start.sh --prod

# 查看所有選項
./start.sh --help
```

訪問 http://localhost:8000 開始使用

## 📋 核心功能

- **OCR 文字識別**: 使用 Azure Computer Vision API 進行高精度收據圖片文字提取
- **AI 數據提取**: 使用 Claude 4.5 Sonnet 進行智能結構化數據提取與解析
- **CSV 匯出**: 自動生成中文標題的 CSV 檔案（摘要與明細報表）
- **批量處理**: 支援單檔、多檔或資料夾批次處理
- **智能快取**: OCR 與 AI 結果快取，支援中斷續傳，節省 API 成本
- **檔案管理**: 自動清理已處理圖片，支援手動刪除
- **Web 界面**: 友善的使用者界面，即時進度追蹤與結果視覺化

## 📚 文檔

### 🔧 使用指南
- **[Azure資源建立指南](./docs/guides/AZURE_RESOURCE_SETUP.md)** - 如何在Azure上建立Computer Vision資源並取得URL和Key（**新用戶必讀**）
- **[API設定指南](./docs/guides/API_SETUP_GUIDE.md)** - 如何設定Azure和Claude API
- **[Azure成本指南](./docs/guides/AZURE_COST_GUIDE.md)** - 成本控制和優化建議
- **[Azure金鑰管理](./docs/guides/AZURE_KEY_MANAGEMENT.md)** - 如何在Azure Portal查看和管理API金鑰
- **[使用說明](./docs/guides/USAGE.md)** - 詳細的使用指南

### 🎯 功能特性
- **[檔案管理功能](./docs/features/FILE_MANAGEMENT_SUMMARY.md)** - 自動檔案清理和管理
- **[性能優化](./docs/features/PERFORMANCE_OPTIMIZATION_SUMMARY.md)** - 系統性能優化詳情
- **[稅金處理功能](./docs/features/TAX_FEATURES_SUMMARY.md)** - 日本稅金識別和處理

### 🔧 開發設定
- **[GitHub設定](./docs/setup/GITHUB_SETUP.md)** - GitHub專案設定和上傳指南

### 🐛 修復記錄
- **[修復文檔概覽](./docs/fixes/README.md)** - 快速了解所有修復
- **[系統修復總結](./docs/fixes/INTEGRATED_FIXES.md)** - 所有問題修復記錄（包含詳細技術說明）

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
- **AI服務**: Azure Computer Vision, Claude 4.5 Sonnet
- **前端**: HTML, JavaScript
- **數據處理**: Pandas, CSV
- **圖片處理**: Pillow, OpenCV

## ⚡ 技術亮點

### 🔗 整合 AI 服務
- **Azure Computer Vision**: 高精度 OCR 文字識別
- **Claude 4.5 Sonnet**: 先進 AI 進行結構化數據提取與智能解析

### 🚀 性能與可靠性
- **FastAPI 後端**: 高效能異步框架，自動生成 API 文檔
- **智能快取**: OCR 與 AI 結果快取，支援中斷續傳
- **檔案管理**: 自動清理已處理圖片，支援手動刪除
- **性能優化**: 並行處理控制、API 頻率限制管理

### 💡 核心特色
- **智能快取**: 避免重複處理，節省 API 成本
- **批量處理**: 高效處理大量圖片
- **錯誤恢復**: 中斷後可從快取恢復處理
- **生產就緒**: 支援生產模式，優化設定

## 🎯 應用場景

- **個人財務管理**: 日常收據整理與支出追蹤
- **企業發票處理**: 批量發票處理與數據分析
- **會計與審計**: 自動化收據處理與財務記錄
- **報稅準備**: 自動提取收據中的稅務相關資訊

## 🤝 貢獻

歡迎提交Issue和Pull Request！

## 📄 授權

MIT License

---

**最後更新**: 2025-12-30  
**版本**: 1.1.0
