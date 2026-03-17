本地启动顺序（MVP，单用户串行推理模式）

1. 启动基础依赖
- PostgreSQL
- MinIO（或其他对象存储）
验收：两者均可连接

2. 准备模型权重
- 确认模型权重位于 transfer-models/checkpoints
- 确认 MODEL_ROOT 指向上述目录
验收：按风格可映射到对应权重文件

3. 启动后端 server
验收：
- 健康检查接口可访问（如 /health）
- 能连上 DB/Storage
- 能读取 MODEL_ROOT 指定的权重目录

4. 执行数据库迁移
验收：
- 核心表存在：users/styles/generation_tasks/artworks/artwork_likes/comments/follows

5. 初始化 styles 字典
- vangogh / ink / cezanne / monet / ukiyoe
验收：styles 表有 5 条启用记录

6. 启动 web-user
验收：
- 登录页可打开
- 可请求后端接口

7. 启动 web-admin
验收：
- 管理登录与管理页面可打开
- 管理接口可访问（管理员 token）

最小联调流程（必须跑通）
1. 注册并登录普通用户
2. 提交风格转换任务
3. 轮询任务直到 success（同一服务内串行推理，无任务队列）
4. 保存作品到仓库
5. 发布作品到大厅
6. 另一个用户点赞+评论+关注
7. 管理员下架作品/删除评论（任一）
