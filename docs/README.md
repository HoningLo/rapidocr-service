# RapidOCR Service Documentation

這裡包含了 RapidOCR Service 專案的所有文檔。

## 📚 文檔目錄

### 📖 專案概覽
- [README.md](../README.md) - 專案主要說明文檔

### 🏗️ 架構和結構
- [專案結構說明](./PROJECT_STRUCTURE.md) - 詳細的專案目錄結構說明
- [架構優化報告](./ARCHITECTURE_OPTIMIZATION_REPORT.md) - FastAPI 架構優化的完整報告

### 🔧 配置和設置
- [UV 轉換報告](./UV_CONVERSION_REPORT.md) - 從 Rye 轉換到 UV 的詳細過程
- [Uvicorn 配置](./UVICORN_CONFIGURATION.md) - 從 FastAPI CLI 回到 Uvicorn 的配置說明

## 🚀 快速開始

1. **安裝依賴**
   ```bash
   uv sync --dev
   ```

2. **運行開發服務器**
   ```bash
   make run
   # 或
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **運行測試**
   ```bash
   make test
   ```

4. **代碼檢查**
   ```bash
   make check-all
   ```

## 📝 API 文檔

啟動服務後，可以通過以下 URL 訪問 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker 部署

```bash
# 構建映像
docker build -t rapidocr-service .

# 運行容器
docker run -p 8000:80 rapidocr-service

# 使用 docker-compose
docker-compose up -d
```

## 🔍 健康檢查

- **基本健康檢查**: http://localhost:8000/health/
- **詳細統計信息**: http://localhost:8000/health/stats

## 📊 專案統計

- **語言**: Python 3.13
- **框架**: FastAPI
- **包管理**: UV
- **測試**: pytest
- **類型檢查**: MyPy
- **代碼格式**: Black + Ruff
- **容器化**: Docker + Docker Compose

## 🤝 貢獻指南

1. 確保所有測試通過：`make check-all`
2. 遵循代碼風格：pre-commit hooks 會自動檢查
3. 添加適當的類型標注
4. 更新相關文檔

---

**更多詳細信息請參閱各個文檔文件。** 📖
