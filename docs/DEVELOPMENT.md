# 開發環境

## 環境需求

- Python 3.13+
- UV 套件管理器
- Git

## 快速設置

```bash
# 1. 克隆專案
git clone <repository-url>
cd rapidocr-service

# 2. 安裝依賴
uv sync

# 3. 啟動開發服務器
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 開發命令

### 依賴管理
```bash
# 安裝新套件
uv add <package-name>

# 安裝開發依賴
uv add --dev <package-name>

# 更新依賴
uv sync --upgrade

# 移除套件
uv remove <package-name>
```

### 代碼品質
```bash
# 格式化代碼
uv run black app/ tests/
uv run isort app/ tests/

# 檢查語法
uv run ruff check app/ tests/

# 類型檢查
uv run mypy app/

# 運行測試
uv run pytest

# 測試覆蓋率
uv run pytest --cov=app tests/
```

### 開發工具

#### 安裝 Pre-commit
```bash
uv add --dev pre-commit
uv run pre-commit install
```

#### VS Code 設置
在 `.vscode/settings.json` 中配置：
```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true
}
```

## 專案結構

```
app/
├── main.py           # FastAPI 應用入口
├── config.py         # 配置管理
├── models.py         # Pydantic 模型
├── dependencies.py   # 依賴注入
├── routers/          # API 路由
│   ├── health.py
│   └── ocr.py
├── ocr_service.py    # OCR 服務
├── file_manager.py   # 檔案管理
├── gpu_utils.py      # GPU 工具
└── logging_config.py # 日誌配置
```

## API 開發

### 新增端點
1. 在 `app/models.py` 定義請求/回應模型
2. 在 `app/routers/` 新增路由檔案
3. 在 `app/main.py` 註冊路由
4. 撰寫測試檔案

### 範例：新增健康檢查端點
```python
# app/routers/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {"status": "healthy"}
```

## 測試

### 單元測試
```bash
# 執行所有測試
uv run pytest

# 執行特定測試
uv run pytest tests/test_main.py

# 顯示詳細輸出
uv run pytest -v
```

### API 測試
```bash
# 啟動服務
uv run uvicorn app.main:app --reload

# 測試端點
curl http://localhost:8000/health/
curl -X POST http://localhost:8000/ocr/ -F "files=@test_image.jpg"
```

## 除錯

### 日誌設置
```python
# app/config.py
LOG_LEVEL = "DEBUG"  # 開發時使用 DEBUG
```

### 使用除錯器
```python
import pdb; pdb.set_trace()  # Python 內建除錯器
# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

### FastAPI 除錯模式
```python
# app/main.py
app = FastAPI(debug=True)  # 僅開發環境
```