# UV 管理的專案目錄結構

## 專案概覽
這是一個使用 UV 管理的 FastAPI RapidOCR 服務專案。

## 目錄結構
```
.
├── app/                    # 主要應用程式代碼
│   ├── __init__.py
│   ├── main.py            # FastAPI 應用程式入口
│   ├── config.py          # 配置管理
│   ├── models.py          # Pydantic 模型
│   ├── ocr_service.py     # OCR 服務邏輯
│   ├── file_manager.py    # 文件管理
│   ├── gpu_utils.py       # GPU 工具
│   └── logging_config.py  # 日誌配置
├── tests/                 # 測試文件
├── temp/                  # 臨時文件目錄
├── logs/                  # 日誌文件目錄
├── pyproject.toml         # 專案配置和依賴
├── uv.lock               # UV 鎖定文件
├── .python-version       # Python 版本定義
├── .env.example          # 環境變數範例
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
└── README.md             # 專案說明

```

## UV 命令

### 安裝依賴
```bash
uv sync
```

### 添加新依賴
```bash
uv add <package>
```

### 添加開發依賴
```bash
uv add --dev <package>
```

### 運行應用程式
```bash
uv run python -m uvicorn app.main:app --reload
```

### 運行測試
```bash
uv run pytest
```

### 代碼格式化
```bash
uv run black app/ tests/
uv run isort app/ tests/
```

### 類型檢查
```bash
uv run mypy app/
```

### Linting
```bash
uv run ruff check app/ tests/
```
