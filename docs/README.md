# RapidOCR Service 文檔

本目錄包含 RapidOCR Service 的技術文檔。

## 📚 文檔索引

### 核心文檔
- [專案結構](./PROJECT_STRUCTURE.md) - 專案目錄結構說明
- [部署指南](./DEPLOYMENT_GUIDE.md) - Docker 部署和配置
- [GPU 支援](./GPU_SUPPORT_GUIDE.md) - GPU 加速配置

### 開發文檔
- [開發環境](./DEVELOPMENT.md) - 本地開發環境設置
- [API 參考](./API_REFERENCE.md) - API 端點和使用方法

## 🚀 快速開始

```bash
# 1. 安裝依賴
uv sync

# 2. 啟動服務
docker compose up -d --build

# 3. 測試服務
curl http://localhost:8200/health/
```

## � 重要連結

- **API 文檔**: http://localhost:8200/docs
- **健康檢查**: http://localhost:8200/health/
- **專案主頁**: [../README.md](../README.md)

## �️ 技術棧

| 組件 | 版本 | 說明 |
|------|------|------|
| Python | 3.13 | 程式語言 |
| FastAPI | Latest | Web 框架 |
| UV | Latest | 套件管理 |
| RapidOCR | Latest | OCR 引擎 |
| Docker | Latest | 容器化 |

---

**詳細信息請參閱各個文檔文件。**
