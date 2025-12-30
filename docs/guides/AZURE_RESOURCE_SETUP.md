# Azure Computer Vision 資源建立指南

本指南將詳細說明如何在 Azure Portal 上建立 Computer Vision 資源，並取得 API 端點 URL 和 API 金鑰。

## 📋 前置需求

- Microsoft Azure 帳戶（個人帳戶或工作/學校帳戶都可以）
- 瀏覽器（建議使用 Chrome、Edge 或 Safari）
- 信用卡（用於驗證，免費層級不會收費）

## 🚀 步驟 1: 登入 Azure Portal

1. 前往 [Azure Portal](https://portal.azure.com/)
2. 使用您的 Microsoft 帳戶登入
3. 如果出現帳戶選擇，選擇個人帳戶或工作帳戶

## 🔍 步驟 2: 建立 Computer Vision 資源

### 方法 A: 從市場搜尋建立（推薦）

1. **搜尋 Computer Vision**
   - 在 Azure Portal 頂部的搜尋欄輸入「Computer Vision」
   - 選擇「Computer Vision」服務（來自 Microsoft）

2. **建立資源**
   - 點擊「建立」按鈕（Create）
   - 或點擊「開始使用」（Get started）

### 方法 B: 從資源建立選單

1. 點擊左上角的「建立資源」（Create a resource）
2. 在搜尋欄輸入「Computer Vision」
3. 選擇「Computer Vision」服務
4. 點擊「建立」（Create）

## ⚙️ 步驟 3: 填寫資源設定

在「建立 Computer Vision」頁面，填寫以下資訊：

### 訂閱（Subscription）
- 選擇您的 Azure 訂閱
- 如果沒有訂閱，可以選擇「免費試用」或「隨用隨付」

### 資源群組（Resource Group）
- **選項 1（推薦）**：建立新的資源群組
  - 點擊「建立新項目」（Create new）
  - 輸入名稱，例如：`receipt-ocr-resources`
- **選項 2**：使用現有資源群組
  - 從下拉選單選擇現有資源群組

### 區域（Region）
- 選擇離您最近的區域，例如：
  - **東亞**（East Asia）- 適合台灣、香港
  - **東南亞**（Southeast Asia）- 適合新加坡
  - **美國東部**（East US）- 適合美國東部

### 名稱（Name）
- 輸入資源名稱，例如：`receipt-ocr-vision`
- 名稱必須：
  - 全球唯一（不能與其他 Azure 用戶重複）
  - 只能包含小寫字母、數字和連字號
  - 長度 2-64 個字元
- 建議格式：`yourname-receipt-ocr` 或 `receipt-ocr-vision`

### 定價層（Pricing Tier）
- **選擇 F0（免費層）**（如果可用）
  - 每月 5,000 次交易免費
  - 每分鐘最多 20 次請求
  - 功能完整，適合個人使用
- **或選擇 S1（標準層）**
  - 沒有免費額度，按使用量計費
  - $1.00 per 1,000 transactions
  - 適合商業使用

### 其他設定
- **應用程式名稱**：可選，留空即可
- **確認我已檢閱並同意條款和條件**：勾選此選項

### 完成設定
- 點擊頁面底部的「檢閱 + 建立」（Review + create）按鈕
- 系統會驗證設定，確認無誤後點擊「建立」（Create）

## ⏳ 步驟 4: 等待部署完成

1. 系統會開始部署資源，通常需要 1-2 分鐘
2. 您會看到「您的部署正在進行中」的訊息
3. 部署完成後，點擊「前往資源」（Go to resource）按鈕

## 🔑 步驟 5: 取得 API 端點和金鑰

資源建立完成後，您需要取得兩個重要資訊：

### 5.1 取得端點 URL

1. 在資源的左側選單中找到「資源管理」（Resource Management）區塊
2. 點擊「金鑰和端點」（Keys and Endpoint）
3. 您會看到「端點」（Endpoint）欄位
4. 點擊端點 URL 旁邊的「複製到剪貼簿」圖示（📋）
5. 端點 URL 格式應該是：
   ```
   https://your-resource-name.cognitiveservices.azure.com
   ```
   ⚠️ **重要**：不要包含尾隨斜線 `/`

### 5.2 取得 API 金鑰

在同一個「金鑰和端點」頁面：

1. 您會看到兩個金鑰：
   - **KEY 1**
   - **KEY 2**（備用金鑰）

2. 點擊 KEY 1 旁邊的「複製到剪貼簿」圖示（📋）

3. ⚠️ **安全提示**：
   - 金鑰只會顯示一次（或需要重新生成才能看到）
   - 請立即複製並保存在安全的地方
   - 不要將金鑰分享給他人或提交到 Git

## 📝 步驟 6: 更新 .env 檔案

將取得的資訊填入專案的 `.env` 檔案：

1. 打開專案根目錄的 `.env` 檔案

2. 更新以下兩個欄位：

```env
# Azure Computer Vision API設定
# 注意：端點URL不要包含尾隨斜線（/）
AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
AZURE_VISION_KEY=your_api_key_here
```

3. 替換說明：
   - `https://your-resource-name.cognitiveservices.azure.com` → 貼上您複製的端點 URL
   - `your_api_key_here` → 貼上您複製的 API 金鑰（KEY 1）

4. 儲存檔案

## ✅ 步驟 7: 驗證設定

### 方法 1: 使用 API 狀態檢查端點

1. 啟動您的應用程式：
   ```bash
   python start.py
   ```

2. 在瀏覽器中訪問：
   ```
   http://localhost:8000/api-status
   ```

3. 查看回應，確認：
   - `azure_vision.configured` 為 `true`
   - `azure_vision.endpoint` 顯示正確的端點
   - `azure_vision.key_set` 為 `true`
   - `azure_vision.test_mode` 為 `false`

### 方法 2: 測試 OCR 功能

1. 訪問應用程式主頁：
   ```
   http://localhost:8000
   ```

2. 上傳一張測試收據圖片

3. 點擊「開始識別」

4. 如果設定正確，應該能夠成功處理圖片

## 🎯 完整範例

假設您建立的資源名稱是 `receipt-ocr-vision`，那麼：

### 端點 URL
```
https://receipt-ocr-vision.cognitiveservices.azure.com
```

### .env 檔案內容
```env
# Azure Computer Vision API設定
AZURE_VISION_ENDPOINT=https://receipt-ocr-vision.cognitiveservices.azure.com
AZURE_VISION_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

## ⚠️ 常見問題

### Q: 資源名稱已被使用怎麼辦？
**A**: Azure 資源名稱必須全球唯一。嘗試：
- 加上數字或日期，例如：`receipt-ocr-vision-2024`
- 加上您的名稱，例如：`john-receipt-ocr`
- 使用更獨特的名稱

### Q: 找不到「金鑰和端點」頁面？
**A**: 
1. 確認您已進入資源的詳細頁面（不是資源列表）
2. 在左側選單中尋找「資源管理」區塊
3. 點擊「金鑰和端點」

### Q: 金鑰顯示為星號（****）？
**A**: 
- 這是正常的安全措施
- 點擊「顯示金鑰」按鈕即可看到完整金鑰
- 或使用「重新產生」功能產生新金鑰

### Q: 免費層級不可用？
**A**: 
- 每個訂閱只能有一個免費層（F0）資源
- 如果已有免費層資源，需要刪除舊的或使用 S1 付費層
- 或使用不同的訂閱建立新的免費層資源

### Q: 需要信用卡驗證嗎？
**A**: 
- 免費層（F0）通常不需要信用卡
- 某些地區或帳戶類型可能需要信用卡驗證
- 如果使用免費層，不會產生費用

### Q: 端點 URL 格式錯誤？
**A**: 正確格式：
- ✅ `https://your-resource-name.cognitiveservices.azure.com`
- ❌ `https://your-resource-name.cognitiveservices.azure.com/`（不要尾隨斜線）
- ❌ `https://your-resource-name.cognitiveservices.azure.com/vision/v3.2/read/analyze`（不要包含 API 路徑）

## 🔒 安全建議

1. **保護 API 金鑰**
   - 不要將 `.env` 檔案提交到 Git
   - 確保 `.env` 在 `.gitignore` 中
   - 不要將金鑰分享給他人

2. **使用 KEY 2 作為備用**
   - 如果 KEY 1 洩露，可以立即使用 KEY 2
   - 然後重新生成 KEY 1

3. **定期輪換金鑰**
   - 定期重新生成 API 金鑰
   - 更新 `.env` 檔案

4. **監控使用量**
   - 定期檢查「配額和使用量」頁面
   - 設定使用量警示

## 📊 下一步

資源建立完成後，您可以：

1. **測試 OCR 功能**：上傳收據圖片測試識別功能
2. **監控使用量**：查看 API 使用情況和成本
3. **優化設定**：根據需求調整資源配置
4. **閱讀更多文檔**：
   - [API 設定指南](./API_SETUP_GUIDE.md)
   - [Azure 成本指南](./AZURE_COST_GUIDE.md)
   - [Azure 金鑰管理](./AZURE_KEY_MANAGEMENT.md)

## 🔗 相關連結

- [Azure Portal](https://portal.azure.com/)
- [Azure Computer Vision 文件](https://docs.microsoft.com/azure/cognitive-services/computer-vision/)
- [定價資訊](https://azure.microsoft.com/pricing/details/cognitive-services/computer-vision/)
- [快速入門指南](https://docs.microsoft.com/azure/cognitive-services/computer-vision/quickstarts-sdk/client-library)

---

**最後更新**: 2025-12-30  
**版本**: 1.0.0

