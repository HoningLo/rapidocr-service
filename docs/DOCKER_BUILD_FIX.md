# Docker 構建錯誤修復報告

## 🛠️ 問題解決

成功解決了 Docker 構建過程中遇到的系統依賴包問題。

## ❌ 原始錯誤

```
E: Package 'libgl1-mesa-glx' has no installation candidate
```

**原因**: 在較新的 Debian 版本 (trixie) 中，`libgl1-mesa-glx` 包已被移除或重命名。

## ✅ 解決方案

### 1. 更新系統依賴包

```dockerfile
# 修復前
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \        # ❌ 不再可用
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \         # ❌ 包名變更
    libgomp1 \
    libgcc-s1 \              # ❌ 不必要
    curl \
    && rm -rf /var/lib/apt/lists/*

# 修復後
RUN apt-get update && apt-get install -y \
    libgl1 \                 # ✅ 現代替代品
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \            # ✅ 正確包名
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### 2. 移除過時的 Docker Compose 版本宣告

```yaml
# 修復前
version: '3.8'              # ❌ 已過時，會產生警告

# 修復後
# (移除 version 行)         # ✅ 使用預設版本
```

### 3. 修復健康檢查 URL

```dockerfile
# 修復前
CMD curl -f http://localhost:80/health || exit 1    # ❌ 會產生 307 重定向

# 修復後
CMD curl -f http://localhost:80/health/ || exit 1   # ✅ 正確的端點
```

## 🧪 驗證結果

### Docker 構建
- ✅ **構建成功**: 所有依賴包正確安裝
- ✅ **UV 同步**: 依賴解析和安裝成功
- ✅ **用戶創建**: rapidocr 用戶創建成功
- ✅ **目錄創建**: temp 和 logs 目錄就緒

### 容器運行
- ✅ **服務啟動**: RapidOCR 服務正常啟動
- ✅ **OCR 引擎**: PP-OCRv4 模型載入成功
- ✅ **網絡監聽**: Uvicorn 在 0.0.0.0:80 監聽
- ✅ **健康檢查**: 端點回應正常
- ✅ **日誌記錄**: 結構化日誌正常輸出

### 環境適配
- ✅ **CPU 模式**: 在無 GPU 環境自動切換到 CPU
- ✅ **模型載入**: ONNX 模型正確載入
- ✅ **依賴解析**: 所有依賴庫正常工作

## 📦 最終配置

### 系統依賴
- `libgl1`: OpenGL 支援
- `libglib2.0-0`: GLib 核心庫
- `libsm6`: X11 會話管理
- `libxext6`: X11 擴展
- `libxrender1`: X11 渲染
- `libgomp1`: OpenMP 支援
- `curl`: 健康檢查工具

### 運行環境
- **基礎映像**: `python:3.13-slim`
- **包管理**: UV
- **用戶**: rapidocr (非 root)
- **工作目錄**: `/app`
- **暴露端口**: 80
- **健康檢查**: `/health/` 端點

## 🎯 重要改進

1. **現代化依賴**: 使用當前 Debian 版本支援的包
2. **安全性**: 非 root 用戶運行
3. **可觀測性**: 完整的健康檢查和日誌
4. **效能**: 最小化的系統依賴
5. **兼容性**: 支援 CPU 和 GPU 環境

---

**Docker 構建問題已完全解決，容器可正常運行！** 🐳✅
