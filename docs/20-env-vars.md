环境变量清单（MVP，单用户串行推理模式）

1. web-user（用户端）
- VUE_APP_API_BASE_URL（必填）示例：http://localhost:8000
职责：用户端请求后端 API 地址

2. web-admin（管理端）
- VUE_APP_API_BASE_URL（必填）示例：http://localhost:8000
职责：管理端请求后端 API 地址

3. server（后端）
- APP_HOST（必填）示例：0.0.0.0
- APP_PORT（必填）示例：8000
- APP_ENV（必填）示例：dev
- JWT_SECRET（必填）示例：your-very-strong-secret
- JWT_EXPIRE_MINUTES（必填）示例：10080
- DB_URL（必填）示例：postgresql://user:pass@localhost:5432/inspiration_gallery
- STORAGE_ENDPOINT（必填）示例：http://localhost:9000
- STORAGE_ACCESS_KEY（必填）示例：minioadmin
- STORAGE_SECRET_KEY（必填）示例：minioadmin
- STORAGE_BUCKET（必填）示例：inspiration-gallery
- CORS_ORIGINS（必填）示例：http://localhost:8080,http://localhost:8081
- MODEL_ROOT（必填）示例：D:/Desktop/Graduation Project/transfer-models/checkpoints
- MODEL_DEVICE（必填）示例：cpu（或 cuda）
- MAX_CONCURRENCY（必填）示例：1（单用户模式建议固定为 1）
