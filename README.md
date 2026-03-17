# 灵感画廊 Inspiration Gallery

## 项目简介

本项目为毕业设计作品，定位为一个面向图像风格迁移与作品分享的 Web 平台。用户可以上传本地图片，生成不同艺术风格的图像，并将结果保存到个人仓库或发布到大厅进行展示和互动。除用户端外，系统还提供基础管理后台，用于处理作品下架、评论管理和用户封禁等操作。

## 技术选型

1. **前端框架**：使用 Vue 2 与 Vue Router 构建单页应用，完成创作页、大厅页、作品详情页、个人主页和后台管理页面的开发。
2. **接口通信**：使用 Axios 统一处理前后端请求，并结合 Token 完成登录态保持与接口鉴权。
3. **后端服务**：使用 FastAPI 提供认证、生成任务、作品管理、社交互动和后台审核等业务接口。
4. **数据存储**：使用 SQLAlchemy 管理账号、作品、评论、关注关系与生成任务等核心业务数据，并通过 Alembic 维护表结构。
5. **模型推理**：风格迁移部分基于 CycleGAN 图像转换框架实现，结合本地风格权重生成不同艺术风格的图像结果。

## 本地运行

### 安装前端依赖

```powershell
cd "D:\Desktop\Graduation Project\web-user"
npm install
```

### 安装后端依赖

```powershell
cd "D:\Desktop\Graduation Project\server"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 准备模型环境

```powershell
cd "D:\Desktop\Graduation Project\transfer-models"
conda env create -f environment.yml
conda activate pytorch-img2img
```

### 初始化数据库

```powershell
cd "D:\Desktop\Graduation Project\server"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts\seed_styles.py
```

### 启动后端服务

```powershell
cd "D:\Desktop\Graduation Project\server"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 启动前端服务

```powershell
cd "D:\Desktop\Graduation Project\web-user"
npm run serve
```

## 管理员体验账号

```text
用户ID：admin1433223
密码：admin1433223
```

## 常用命令

### 前端开发

```powershell
cd "D:\Desktop\Graduation Project\web-user"
npm run serve
```

### 前端构建

```powershell
cd "D:\Desktop\Graduation Project\web-user"
npm run build
```

### 前端检查

```powershell
cd "D:\Desktop\Graduation Project\web-user"
npm run lint
```

## 未来展望

1. 增加更多风格类型，丰富用户可选择的生成效果。
2. 完善推荐与发现功能，提升大厅内容的浏览效率。
3. 继续优化移动端适配，改善不同设备下的使用体验。
4. 补充更细致的后台管理能力，提高平台内容治理效率。
