# 部署指南

## Docker Compose 部署（推薦）

```bash
# 克隆專案
git clone <repository-url>
cd rapidocr-service

# 啟動服務
docker compose up -d --build

# 檢查狀態
docker compose ps
curl http://localhost:8200/health/
```

## Docker 手動部署

```bash
# 構建鏡像
docker build -t rapidocr-service .

# 運行容器
docker run -d \
  --name rapidocr-service \
  -p 8200:80 \
  -v ./temp:/app/temp \
  -v ./logs:/app/logs \
  rapidocr-service
```

## 本地開發

```bash
# 安裝依賴
uv sync

# 啟動開發服務器
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 訪問 API 文檔
open http://localhost:8000/docs
```

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `LOG_LEVEL` | INFO | 日誌等級 |
| `TEMP_DIR` | /app/temp | 暫存目錄 |
| `MAX_FILE_SIZE` | 10MB | 檔案大小限制 |
| `MAX_FILES` | 10 | 最大檔案數量 |

## GPU 支援

確保主機已安裝 NVIDIA Docker Runtime：

```bash
# 安裝 NVIDIA Container Runtime
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 驗證 GPU 可用
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 健康檢查

- **基本狀態**: `GET /health/`
- **API 文檔**: `GET /docs`
- **容器日誌**: `docker logs rapidocr-service-rapidocr-service-1`

## 故障排除

### 權限問題
```bash
# 修正目錄權限
sudo chown -R 1000:1000 temp logs
```

### GPU 不可用
```bash
# 檢查 GPU 狀態
nvidia-smi

# 檢查 Docker GPU 支援
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### 服務無法啟動
```bash
# 檢查日誌
docker compose logs rapidocr-service

# 重新構建
docker compose down
docker compose up -d --build
```