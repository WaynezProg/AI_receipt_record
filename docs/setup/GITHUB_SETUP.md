# GitHub 上傳指南

## 🚀 上傳到GitHub的步驟

### 1. 初始化Git倉庫

```bash
# 初始化Git倉庫
git init

# 添加所有檔案
git add .

# 提交初始版本
git commit -m "Initial commit: 日本收據識別系統"
```

### 2. 建立GitHub倉庫

1. 前往 [GitHub](https://github.com/)
2. 點擊 "New repository"
3. 填寫倉庫資訊：
   - Repository name: `receipt_record`
   - Description: `日本收據識別系統 - 基於OCR + AI的智能收據識別`
   - 選擇 Public 或 Private
   - 不要勾選 "Add a README file"（我們已經有了）
4. 點擊 "Create repository"

### 3. 連接並推送到GitHub

```bash
# 添加遠端倉庫（替換 YOUR_USERNAME 為您的GitHub用戶名）
git remote add origin https://github.com/YOUR_USERNAME/receipt_record.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 4. 設定GitHub Pages（可選）

如果您想要展示專案，可以設定GitHub Pages：

1. 前往倉庫設定頁面
2. 點擊 "Pages"
3. Source 選擇 "Deploy from a branch"
4. Branch 選擇 "main"
5. 點擊 "Save"

### 5. 設定GitHub Secrets（用於CI/CD）

如果您要使用GitHub Actions，需要設定以下Secrets：

1. 前往倉庫設定頁面
2. 點擊 "Secrets and variables" → "Actions"
3. 添加以下Secrets：
   - `AZURE_VISION_ENDPOINT`
   - `AZURE_VISION_KEY`
   - `CLAUDE_API_KEY`

## 📋 重要提醒

### ✅ 已包含的檔案
- `.gitignore` - 保護敏感資訊
- `LICENSE` - MIT授權
- `README_GITHUB.md` - GitHub專用README
- `.github/workflows/ci.yml` - CI/CD工作流程
- `tests/` - 測試檔案

### 🔒 已排除的檔案
- `.env` - 環境變數（包含API金鑰）
- `data/receipts/*` - 上傳的收據圖片
- `data/output/*` - 輸出的CSV檔案
- `logs/` - 日誌檔案
- `__pycache__/` - Python快取檔案

### 📝 上傳前檢查清單

- [ ] 確認 `.env` 檔案沒有被提交
- [ ] 確認API金鑰沒有出現在程式碼中
- [ ] 確認測試圖片沒有被提交
- [ ] 確認日誌檔案沒有被提交
- [ ] 更新 `README_GITHUB.md` 中的GitHub連結

## 🎯 後續步驟

### 1. 更新README連結
編輯 `README_GITHUB.md`，將以下連結替換為您的GitHub資訊：
- `https://github.com/yourusername/receipt_record.git`
- `your.email@example.com`
- `https://github.com/yourusername/receipt_record/issues`

### 2. 設定分支保護
1. 前往倉庫設定頁面
2. 點擊 "Branches"
3. 添加分支保護規則：
   - Branch name pattern: `main`
   - 勾選 "Require pull request reviews before merging"
   - 勾選 "Require status checks to pass before merging"

### 3. 設定Issue模板
建立 `.github/ISSUE_TEMPLATE/bug_report.md`：

```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**描述錯誤**
簡潔明瞭地描述錯誤。

**重現步驟**
1. 前往 '...'
2. 點擊 '....'
3. 滾動到 '....'
4. 看到錯誤

**預期行為**
簡潔明瞭地描述您預期的行為。

**截圖**
如果適用，添加截圖以幫助解釋您的問題。

**環境資訊**
- OS: [例如 Windows 10]
- Python版本: [例如 3.9]
- 瀏覽器: [例如 Chrome 90]

**其他資訊**
在此添加有關問題的任何其他上下文。
```

## 🔧 常用Git命令

```bash
# 查看狀態
git status

# 查看變更
git diff

# 添加檔案
git add <filename>

# 提交變更
git commit -m "描述變更"

# 推送到GitHub
git push

# 拉取最新變更
git pull

# 查看提交歷史
git log --oneline

# 建立新分支
git checkout -b feature/new-feature

# 切換分支
git checkout main

# 合併分支
git merge feature/new-feature
```

## 📞 遇到問題？

如果在上傳過程中遇到問題：

1. **權限錯誤**：確認GitHub帳戶設定正確
2. **檔案太大**：檢查是否有大檔案被意外包含
3. **API金鑰洩露**：立即撤銷並重新生成API金鑰
4. **CI/CD失敗**：檢查GitHub Actions日誌

## 🎉 完成！

成功上傳後，您的專案將在GitHub上公開展示，其他開發者可以：
- 查看程式碼
- 提交Issue
- 建立Pull Request
- 下載使用

記得定期更新專案，回應Issue，維護專案的活躍度！
