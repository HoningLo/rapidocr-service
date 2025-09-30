# RapidOCR FastAPI 服務

高性能 FastAPI 服務，基於 RapidOCR 提供 OCR 功能，支援 GPU 加速、全面日誌記錄和 UUID 檔案追蹤。

> 📖 **[English Version](./README_EN.md)** | **[中文版本](./README.md)**

## 功能特色

- 🚀 **FastAPI**: 現代化、高效的網頁框架，自動生成 API 文檔
- 🔥 **GPU 加速**: 自動檢測並使用 GPU 加速（如可用）
- 📝 **全面日誌**: 所有操作的結構化日誌記錄，包含唯一請求追蹤
- 🆔 **UUID 管理**: 為所有上傳檔案和處理結果分配唯一識別碼
- 📁 **智能檔案管理**: 臨時檔案儲存，具備自動清理功能
- 📷 **多圖片支援**: 單一請求可處理多張圖片
- 🔄 **JSON 回應**: 標準化回應格式，包含檔名、UUID 和提取文字
- 🐍 **Python 3.13+**: 使用現代 Python 和 uv 進行快速依賴管理

## 系統架構

本服務遵循以下核心原則：
- **API 優先設計**: 清晰的 RESTful 介面，具備型別安全
- **性能優化**: GPU 加速，CPU 作為備用選項
- **全面日誌記錄**: 所有操作的完整審計軌跡
- **穩健檔案管理**: 基於 UUID 的檔案追蹤與清理
- **資料完整性**: 從輸入到輸出的完整可追溯性

## 快速開始

### 系統需求

- Python 3.13+
- uv 套件管理器
- 可選：支援 CUDA 的 GPU（用於加速）

### 安裝步驟

1. 克隆專案庫：
```bash
git clone <repository-url>
cd rapidocr-service
```

2. 使用 uv 安裝依賴：
```bash
uv sync
```

3. 啟動服務：
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 使用 Docker 部署

```bash
# 建構並啟動服務
docker compose up -d --build

# 服務將在 http://localhost:8200 上運行
```

### API 使用方法

#### 單張圖片 OCR
```bash
curl -X POST "http://localhost:8200/ocr" \
  -F "file=@image.jpg"
```

#### 多張圖片 OCR
```bash
curl -X POST "http://localhost:8200/ocr" \
  -F "file=@image1.jpg" \
  -F "file=@image2.png"
```

#### 回應格式
```json
[
  {
    "FileName": "image1.jpg",
    "UUID": "550e8400-e29b-41d4-a716-446655440000",
    "Context": "從圖片中提取的文字內容..."
  }
]
```

## 📚 文檔資源

- **完整文檔**: 請參閱 [docs/](./docs/) 目錄獲取詳細文檔
- **API 文檔**:
  - Swagger UI: http://localhost:8200/docs
  - ReDoc: http://localhost:8200/redoc
- **健康檢查**: http://localhost:8200/health/

## 開發指南

### 執行測試
```bash
uv run pytest
```

### 程式碼格式化
```bash
uv run black .
uv run isort .
```

### 型別檢查
```bash
uv run mypy .
```

### 本地開發
```bash
# 開發模式啟動
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 系統配置

環境變數：
- `LOG_LEVEL`: 日誌等級 (DEBUG, INFO, WARNING, ERROR)
- `TEMP_DIR`: 暫存檔案儲存目錄
- `MAX_FILE_SIZE`: 檔案上傳大小限制（位元組）
- `CLEANUP_INTERVAL`: 檔案清理間隔時間（秒）
- `HOST`: 服務主機位址（預設：0.0.0.0）
- `PORT`: 服務埠號（預設：80）

## 專案狀態

✅ **服務已啟動**: 目前在 http://localhost:8200 運行  
✅ **GPU 支援**: 已啟用 GPU 加速功能  
✅ **Docker 部署**: 使用 Docker Compose 進行容器化部署  

## 授權條款

MIT License - 詳細內容請參閱 LICENSE 檔案。
