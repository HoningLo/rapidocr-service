# 專案結構

## 概覽
基於 FastAPI 和 UV 的 RapidOCR 服務專案。

## 目錄配置

```
rapidocr-service/
├── app/                      # 應用程式碼
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 設定管理
│   ├── models.py            # 資料模型
│   ├── dependencies.py      # 依賴注入
│   ├── routers/             # API 路由
│   │   ├── health.py        # 健康檢查
│   │   └── ocr.py          # OCR 端點
│   ├── ocr_service.py       # OCR 服務
│   ├── file_manager.py      # 檔案管理
│   ├── gpu_utils.py         # GPU 工具
│   └── logging_config.py    # 日誌設定
├── tests/                   # 測試檔案
├── docs/                    # 文檔
├── temp/                    # 暫存檔案
├── logs/                    # 日誌檔案
├── pyproject.toml          # 專案設定
├── uv.lock                 # 依賴鎖定
├── Dockerfile              # Docker 設定
└── docker-compose.yml      # 容器編排
```

## 核心元件

### FastAPI 應用 (`app/main.py`)
```python
from fastapi import FastAPI
from app.routers import health, ocr

app = FastAPI(title="RapidOCR Service")
app.include_router(health.router)
app.include_router(ocr.router)
```

### 設定管理 (`app/config.py`)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    log_level: str = "INFO"
    temp_dir: Path = Path("temp")
    max_file_size: int = 10 * 1024 * 1024
```

### OCR 服務 (`app/ocr_service.py`)
```python
class OCRService:
    def __init__(self):
        self._ocr_engine = RapidOCR()
    
    async def process_image(self, file_path: Path):
        result = self._ocr_engine(str(file_path))
        return result.txts if result else ""
```

## 常用命令

```bash
# 依賴管理
uv sync                    # 安裝依賴
uv add <package>          # 新增套件
uv remove <package>       # 移除套件

# 開發
uv run uvicorn app.main:app --reload  # 啟動開發服務器
uv run pytest                         # 執行測試
uv run black app/ tests/              # 格式化程式碼

# 部署
docker compose up -d --build         # 容器化部署
```
