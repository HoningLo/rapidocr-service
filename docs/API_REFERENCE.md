# API 參考

## 基礎資訊

- **Base URL**: `http://localhost:8200`
- **API 文檔**: `http://localhost:8200/docs`
- **內容類型**: `application/json` (回應), `multipart/form-data` (上傳)

## 端點

### 健康檢查

#### `GET /health/`
檢查服務狀態

**回應**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gpu_available": true,
  "uptime": 123.45
}
```

### OCR 處理

#### `POST /ocr/`
上傳圖片進行 OCR 文字識別

**請求**:
- `files`: 一或多個圖片檔案 (支援: jpg, png, bmp, tiff, webp)
- 檔案大小限制: 10MB
- 同時最多: 10 個檔案

**範例**:
```bash
# 單檔案
curl -X POST "http://localhost:8200/ocr/" \
  -F "files=@image.jpg"

# 多檔案
curl -X POST "http://localhost:8200/ocr/" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png"
```

**回應**:
```json
{
  "results": [
    {
      "FileName": "image.jpg",
      "UUID": "550e8400-e29b-41d4-a716-446655440000",
      "Context": "識別出的文字內容"
    }
  ],
  "processing_time": 1.23,
  "gpu_used": true
}
```

## 錯誤處理

### HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 成功 |
| 400 | 請求錯誤 |
| 413 | 檔案過大 |
| 422 | 格式錯誤 |
| 500 | 伺服器錯誤 |

### 錯誤回應格式
```json
{
  "detail": "錯誤描述"
}
```

### 常見錯誤

#### 檔案格式不支援
```json
{
  "detail": "File type not supported: .pdf"
}
```

#### 檔案過大
```json
{
  "detail": "File size exceeds limit: 10MB"
}
```

#### 檔案數量超限
```json
{
  "detail": "Too many files. Maximum allowed: 10"
}
```

## 使用範例

### Python (requests)
```python
import requests

# 健康檢查
response = requests.get("http://localhost:8200/health/")
print(response.json())

# OCR 處理
files = {"files": open("image.jpg", "rb")}
response = requests.post("http://localhost:8200/ocr/", files=files)
print(response.json())
```

### JavaScript (fetch)
```javascript
// 健康檢查
fetch("http://localhost:8200/health/")
  .then(response => response.json())
  .then(data => console.log(data));

// OCR 處理
const formData = new FormData();
formData.append("files", fileInput.files[0]);

fetch("http://localhost:8200/ocr/", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL
```bash
# 健康檢查
curl http://localhost:8200/health/

# OCR 處理
curl -X POST http://localhost:8200/ocr/ \
  -H "accept: application/json" \
  -F "files=@image.jpg;type=image/jpeg"

# 多檔案處理
curl -X POST http://localhost:8200/ocr/ \
  -H "accept: application/json" \
  -F "files=@image1.jpg;type=image/jpeg" \
  -F "files=@image2.png;type=image/png"
```

## 效能考量

### GPU 加速
- 自動檢測可用的 GPU
- 支援 CUDA 和 OpenCL
- CPU 作為備用選項

### 處理速度
- 單圖片: ~1-3 秒 (取決於圖片大小和複雜度)
- GPU 加速可提升 2-5 倍速度
- 批次處理有效率優勢

### 記憶體使用
- 圖片會載入到記憶體處理
- 處理完成後自動清理
- 建議單次不超過 10 個大型圖片