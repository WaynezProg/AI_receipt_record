#!/bin/bash

# 日本收據識別系統 - 快速啟動腳本
# 使用方法: ./start.sh [選項]

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設設定
HOST="0.0.0.0"
PORT="8000"
RELOAD="true"
LOG_LEVEL="info"

# 顯示幫助信息
show_help() {
    echo -e "${BLUE}日本收據識別系統 - 快速啟動腳本${NC}"
    echo ""
    echo "使用方法:"
    echo "  ./start.sh [選項]"
    echo ""
    echo "選項:"
    echo "  -h, --help          顯示幫助信息"
    echo "  -p, --port PORT     指定端口號 (預設: 8000)"
    echo "  -H, --host HOST     指定主機地址 (預設: 0.0.0.0)"
    echo "  --no-reload         禁用自動重載 (生產環境)"
    echo "  --prod              生產模式 (禁用重載，使用 info 日誌級別)"
    echo ""
    echo "範例:"
    echo "  ./start.sh                    # 使用預設設定啟動"
    echo "  ./start.sh -p 8080            # 在端口 8080 啟動"
    echo "  ./start.sh --prod             # 生產模式啟動"
    echo ""
}

# 解析命令行參數
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD="false"
            shift
            ;;
        --prod)
            RELOAD="false"
            LOG_LEVEL="info"
            shift
            ;;
        *)
            echo -e "${RED}❌ 未知選項: $1${NC}"
            echo "使用 ./start.sh --help 查看幫助"
            exit 1
            ;;
    esac
done

# 檢查 Python
check_python() {
    echo -e "${BLUE}🔍 檢查 Python 環境...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 未安裝${NC}"
        echo "請先安裝 Python 3.8 或更高版本"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
}

# 檢查依賴
check_dependencies() {
    echo -e "${BLUE}🔍 檢查依賴套件...${NC}"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ 找不到 requirements.txt${NC}"
        exit 1
    fi
    
    # 檢查是否已安裝主要依賴
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  依賴套件未完全安裝${NC}"
        echo -e "${BLUE}📦 正在安裝依賴套件...${NC}"
        pip3 install -r requirements.txt
    else
        echo -e "${GREEN}✅ 依賴套件已安裝${NC}"
    fi
}

# 檢查環境變數檔案
check_env() {
    echo -e "${BLUE}🔍 檢查環境設定...${NC}"
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            echo -e "${YELLOW}⚠️  找不到 .env 檔案${NC}"
            echo -e "${BLUE}📝 正在從 env.example 創建 .env 檔案...${NC}"
            cp env.example .env
            echo -e "${YELLOW}⚠️  請編輯 .env 檔案並填入您的 API 金鑰${NC}"
            echo ""
            read -p "按 Enter 繼續（請確保已設定 API 金鑰）..."
        else
            echo -e "${RED}❌ 找不到 .env 或 env.example 檔案${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 找到 .env 檔案${NC}"
    fi
}

# 檢查目錄結構
check_directories() {
    echo -e "${BLUE}📁 檢查目錄結構...${NC}"
    
    DIRS=("data/receipts" "data/output" "data/cache" "logs")
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✅ 創建目錄: $dir${NC}"
        else
            echo -e "${GREEN}✅ 目錄存在: $dir${NC}"
        fi
    done
}

# 顯示啟動信息
show_startup_info() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}🚀 日本收據識別系統${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📱 服務地址:${NC} http://${HOST}:${PORT}"
    echo -e "${BLUE}📚 API文檔:${NC} http://${HOST}:${PORT}/docs"
    echo -e "${BLUE}🔧 重載模式:${NC} $RELOAD"
    echo -e "${BLUE}📊 日誌級別:${NC} $LOG_LEVEL"
    echo ""
    echo -e "${YELLOW}💡 提示: 按 Ctrl+C 停止服務${NC}"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
}

# 主函數
main() {
    clear
    echo -e "${BLUE}🚀 啟動日本收據識別系統${NC}"
    echo ""
    
    # 執行檢查
    check_python
    check_dependencies
    check_env
    check_directories
    
    # 顯示啟動信息
    show_startup_info
    
    # 構建 uvicorn 命令
    UVICORN_CMD="uvicorn app.main:app --host $HOST --port $PORT --log-level $LOG_LEVEL"
    
    if [ "$RELOAD" = "true" ]; then
        UVICORN_CMD="$UVICORN_CMD --reload"
    fi
    
    # 啟動服務
    echo -e "${GREEN}✅ 系統準備完成，正在啟動服務...${NC}"
    echo ""
    
    # 使用 Python 啟動（確保環境變數正確載入）
    # 將 shell 變數轉換為 Python 布林值
    if [ "$RELOAD" = "true" ]; then
        RELOAD_PYTHON="True"
    else
        RELOAD_PYTHON="False"
    fi
    
    python3 -c "
import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

# 啟動 uvicorn
import uvicorn
uvicorn.run(
    'app.main:app',
    host='$HOST',
    port=$PORT,
    reload=$RELOAD_PYTHON,
    log_level='$LOG_LEVEL'
)
"
}

# 執行主函數
main

