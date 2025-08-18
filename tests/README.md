# 🧪 測試檔案目錄

這個資料夾包含了所有與收據識別系統相關的測試檔案。

## 📋 測試檔案列表

### 🔧 核心功能測試
- **`test_ocr.py`** - OCR服務測試
- **`test_ai_parsing_fix.py`** - AI解析修復測試
- **`test_tax_features.py`** - 稅金功能測試
- **`test_japanese_translation.py`** - 日文翻譯功能測試

### 📊 CSV功能測試
- **`test_csv_creation.py`** - CSV創建功能測試
- **`test_consolidated_csv.py`** - 整合CSV功能測試

### 🔄 批量處理測試
- **`test_batch_processing.py`** - 批量處理功能測試
- **`test_batch_debug.py`** - 批量處理除錯測試
- **`test_simple_batch.py`** - 簡單批量處理測試
- **`test_upload_and_batch.py`** - 上傳和批量處理測試
- **`test_33_images.py`** - 33張圖片批量處理測試

### 🗂️ 檔案處理測試
- **`test_folder_upload.py`** - 資料夾上傳功能測試
- **`test_failed_files.py`** - 失敗檔案重新處理測試

### 🔐 API和系統測試
- **`test_api_keys.py`** - API金鑰測試
- **`test_azure_usage.py`** - Azure使用量追蹤測試
- **`test_cache_system.py`** - 快取系統測試
- **`test_complete_flow.py`** - 完整流程測試
- **`test_fixes.py`** - 修復功能測試

### 🎨 前端測試
- **`test_frontend.html`** - 前端功能測試

### 🛠️ 工具和輔助檔案
- **`create_test_image.py`** - 創建測試圖片
- **`create_better_test_images.py`** - 創建更好的測試圖片
- **`test_basic.py`** - 基本功能測試

## 🚀 執行測試

### 單個測試
```bash
# 執行特定測試
python tests/test_tax_features.py
python tests/test_ocr.py
python tests/test_batch_processing.py
```

### 所有測試
```bash
# 執行所有測試（需要手動執行每個檔案）
for test_file in tests/test_*.py; do
    echo "執行: $test_file"
    python "$test_file"
    echo "完成: $test_file"
    echo "---"
done
```

## 📝 測試分類

### 功能測試
- OCR文字識別
- AI數據解析
- 稅金類型識別
- 日文翻譯
- CSV輸出

### 性能測試
- 批量處理
- 檔案大小限制
- API使用量追蹤
- 快取系統

### 整合測試
- 完整流程
- 前端後端整合
- 錯誤處理

### 工具測試
- API金鑰驗證
- 圖片創建
- 檔案處理

## 🔍 測試重點

1. **稅金功能**：內含稅/外加稅識別
2. **批量處理**：大量圖片處理能力
3. **錯誤處理**：失敗檔案的重新處理
4. **CSV輸出**：數據格式和完整性
5. **前端顯示**：用戶界面功能
6. **API整合**：外部服務連接

## 📊 測試結果

每個測試檔案都會輸出詳細的測試結果，包括：
- ✅ 成功項目
- ❌ 失敗項目
- 📊 統計信息
- 🔧 修復建議

## 🛠️ 維護說明

- 新增測試時，請在此README中更新
- 測試檔案命名規範：`test_功能名稱.py`
- 保持測試檔案的獨立性和可重複性
- 定期執行測試以確保系統穩定性
