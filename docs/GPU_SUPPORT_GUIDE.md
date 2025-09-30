# GPU 支援指南

## 概述

RapidOCR 服務支援 GPU 加速，可提升 2-5 倍的 OCR 處理速度。

## 系統需求

- NVIDIA GPU (CUDA 支援)
- Docker >= 20.10
- NVIDIA Container Toolkit

## 安裝 NVIDIA Container Toolkit

### Ubuntu/Debian
```bash
# 安裝 NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/nvidia-docker/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-docker.gpg
echo "deb [signed-by=/usr/share/keyrings/nvidia-docker.gpg] https://nvidia.github.io/nvidia-docker/ubuntu$(lsb_release -rs)/nvidia-docker.list" | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 驗證安裝
```bash
# 測試 GPU 可用性
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 使用方式

### 啟動 GPU 加速服務
```bash
# 直接啟動 (自動偵測 GPU)
docker compose up -d --build

# 檢查 GPU 狀態
curl http://localhost:8200/health/
```

### 配置檔案
Docker Compose 已包含 GPU 設定：

```yaml
services:
  rapidocr-service:
    # GPU support configuration
    deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - CUDA_VISIBLE_DEVICES=all
```

## 驗證 GPU 支援

```bash
# 檢查健康狀態
curl http://localhost:8200/health/

# 預期回應
{
  "status": "healthy",
  "gpu_available": true,
  "uptime": 123.45
}

# OCR 處理會顯示 GPU 使用
curl -X POST http://localhost:8200/ocr/ -F "files=@image.jpg"
{
  "results": [...],
  "gpu_used": true
}
```

## 效能提升

| 模式 | 速度 | 適用場景 |
|------|------|----------|
| CPU | 1x | 開發/測試 |
| CUDA GPU | 3-5x | 生產環境 |

## 故障排除

### GPU 未偵測
```bash
# 檢查驅動
nvidia-smi

# 檢查 Docker GPU 支援
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### 記憶體不足
```bash
# 監控 GPU 記憶體使用
nvidia-smi -l 1
```

### 除錯模式
```yaml
environment:
  - LOG_LEVEL=DEBUG  # 查看詳細 GPU 偵測日誌
```
```

### Python 依賴

已添加 GPU 支援的 Python 套件：
- `onnxruntime-gpu>=1.15.0` - GPU 加速的 ONNX Runtime
- `pyopencl>=2024.1` - OpenCL 支援
- `numpy>=1.24.0` - 數值計算庫

## 🚀 使用方式

### 啟動 GPU 支援的服務

```bash
# 構建並啟動容器（GPU 支援）
docker compose up -d --build

# 檢查 GPU 狀態
docker compose exec rapidocr-service nvidia-smi

# 查看日誌確認 GPU 初始化
docker compose logs -f rapidocr-service
```

### 驗證 GPU 使用

```bash
# 檢查健康狀態（應顯示 GPU 可用）
curl http://localhost:8000/health/

# 預期回應：
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "gpu_available": true,
#   "uptime": xxx
# }
```

## 🔍 GPU 偵測邏輯

應用程式會自動偵測 GPU 可用性：

1. **CUDA 支援檢測**：檢查 CUDA 是否可用和 `nvidia-smi` 命令
2. **OpenCL 支援檢測**：檢查 `pyopencl` 是否安裝並可用
3. **自動回退**：如果 GPU 不可用，自動使用 CPU 模式

### GPU 配置優先級
1. CUDA GPU（最佳效能）
2. OpenCL GPU
3. CPU（回退選項）

## ⚡ 效能比較

| 處理模式 | 相對速度 | 記憶體使用 | 適用場景 |
|---------|---------|-----------|----------|
| CPU | 1x | 低 | 小檔案、開發環境 |
| OpenCL GPU | 3-5x | 中 | 中等工作負載 |
| CUDA GPU | 5-10x | 高 | 大量檔案、生產環境 |

## 🛠️ 故障排除

### 常見問題

#### 1. GPU 未被偵測
```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 檢查 Docker GPU 支援
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

#### 2. CUDA 版本不相容
- 確認 NVIDIA 驅動支援的 CUDA 版本
- 更新 `onnxruntime-gpu` 到相容版本

#### 3. 記憶體不足
```yaml
# 限制 GPU 記憶體使用
environment:
  - CUDA_MEMORY_LIMIT=4096  # MB
```

### 除錯模式

啟用除錯日誌以獲得更多資訊：

```yaml
environment:
  - LOG_LEVEL=DEBUG
  - CUDA_LAUNCH_BLOCKING=1
```

## 📊 監控 GPU 使用

### 即時監控
```bash
# GPU 使用率監控
watch -n 1 nvidia-smi

# 容器內的 GPU 狀態
docker compose exec rapidocr-service nvidia-smi
```

### 日誌監控
```bash
# 查看 GPU 相關日誌
docker compose logs rapidocr-service | grep -i gpu
```

## 🔒 安全考量

### GPU 存取控制
- 使用 `NVIDIA_VISIBLE_DEVICES` 限制可存取的 GPU
- 在多租戶環境中隔離 GPU 資源

### 資源限制
```yaml
deploy:
  resources:
    limits:
      memory: 8G
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # 只使用第一個 GPU
          capabilities: [gpu]
```

## 📈 最佳化建議

1. **批次處理**：一次處理多個檔案以充分利用 GPU
2. **記憶體管理**：監控 GPU 記憶體使用，避免 OOM 錯誤
3. **模型快取**：GPU 模型載入成本較高，適合長時間運行
4. **並行處理**：在多 GPU 環境中啟用並行處理

## 🔄 降級到 CPU 模式

如需暫時停用 GPU 支援：

```yaml
# docker-compose.yml
services:
  rapidocr-service:
    # 註解掉 GPU 配置
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
    environment:
      - FORCE_CPU=true  # 強制使用 CPU
```

---

## 📞 支援

如遇到 GPU 配置問題，請檢查：
1. NVIDIA 驅動程式版本
2. Docker 和 NVIDIA Container Toolkit 安裝
3. CUDA 相容性
4. 應用程式日誌中的錯誤訊息

**最後更新**：2025-09-30
