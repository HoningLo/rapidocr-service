# RapidOCR Service - 回到 Uvicorn 配置

## 🔄 配置變更完成

根據您的要求，我們已經成功將專案配置從 FastAPI CLI 回到使用傳統的 Uvicorn 服務器。

## 📦 依賴變更

### 之前 (FastAPI CLI)
```toml
dependencies = [
    "fastapi[standard]>=0.104.0",
    # ...其他依賴
]
```

### 現在 (Uvicorn)
```toml
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.6",
    # ...其他依賴
]
```

## 🚀 運行方式

### 開發模式
```bash
# 使用 Makefile
make run

# 直接使用 uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生產模式
```bash
# 使用 Makefile
make run-prod

# 直接使用 uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 80
```

## 🐳 Docker 配置

### Dockerfile 變更
```dockerfile
# 之前
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]

# 現在
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

## ✅ 驗證結果

- ✅ **Uvicorn 啟動**：正常工作
- ✅ **開發模式**：支持 `--reload` 熱重載
- ✅ **生產模式**：正常運行
- ✅ **所有測試**：12/12 通過
- ✅ **類型檢查**：MyPy 無錯誤
- ✅ **代碼風格**：Ruff + Black 通過
- ✅ **Docker 構建**：配置已更新

## 🎯 優勢

1. **更熟悉的工具**：使用傳統的 Uvicorn 服務器
2. **完全控制**：對服務器配置有更多控制權
3. **穩定性**：成熟的 Uvicorn 生態系統
4. **相容性**：與現有工具鏈完全相容
5. **靈活性**：可以更容易地自定義服務器配置

## 📚 常用命令

```bash
# 開發環境 - 熱重載
make run
# 或
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生產環境
make run-prod
# 或
uv run uvicorn app.main:app --host 0.0.0.0 --port 80

# 自定義工作進程數 (生產環境)
uv run uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 4

# 測試
make test

# 代碼檢查
make check-all
```

## 🔧 主要特性保持不變

- 模組化架構 (routers, dependencies)
- 完整的類型安全
- 異步生命週期管理
- 請求日誌和追蹤
- 全局異常處理
- CORS 支持
- 健康檢查端點

---

**專案現在使用 Uvicorn 作為 ASGI 服務器，保持了所有現代化架構的優勢！** 🚀
