接口清单

| 模块 | 方法 | 路径 | 权限 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| 认证 | POST | /auth/register | 游客 | 用户名 + 密码注册，返回系统分配的账号编号 |
| 认证 | POST | /auth/login | 游客 | 使用账号编号或用户名登录并获取 token |
| 用户 | GET | /users/{id} | 游客 | 查看用户主页信息 |
| 用户 | PATCH | /users/me | 用户 | 修改自己的用户名/头像 |
| 用户 | POST | /users/me/avatar | 用户 | 上传头像图片并返回地址 |
| 用户 | GET | /users/me/notices | 用户 | 查看与自己相关的管理员通知 |
| 用户 | GET | /users/{id}/artworks | 游客 | 查看该用户公开作品 |
| 任务 | POST | /tasks/style-transfer | 用户 | 提交风格迁移任务 |
| 任务 | GET | /tasks/{id} | 用户 | 查询任务状态 |
| 作品 | POST | /artworks | 用户 | 保存作品到个人仓库 |
| 作品 | GET | /artworks/{id} | 游客 | 查看作品详情 |
| 作品 | PATCH | /artworks/{id} | 用户(作者) | 修改标题/可见性 |
| 作品 | DELETE | /artworks/{id} | 用户(作者) | 删除自己的作品 |
| 大厅 | GET | /hall/feed | 游客 | 大厅时间倒序流 |
| 互动 | POST | /artworks/{id}/like | 用户 | 点赞 |
| 互动 | DELETE | /artworks/{id}/like | 用户 | 取消点赞 |
| 互动 | GET | /artworks/{id}/comments | 游客 | 评论列表 |
| 互动 | POST | /artworks/{id}/comments | 用户 | 发表评论/回复 |
| 关注 | POST | /users/{id}/follow | 用户 | 关注作者 |
| 关注 | DELETE | /users/{id}/follow | 用户 | 取消关注 |
| 管理 | GET | /admin/artworks | 管理员 | 查看大厅全部作品 |
| 管理 | PATCH | /admin/artworks/{id}/hide | 管理员 | 下架作品 |
| 管理 | DELETE | /admin/comments/{id} | 管理员 | 删除违规评论 |
| 管理 | GET | /admin/users | 管理员 | 查看用户列表 |
| 管理 | PATCH | /admin/users/{id}/block | 管理员 | 封禁普通用户账号 |
| 管理 | PATCH | /admin/users/{id}/unblock | 管理员 | 解除普通用户封禁 |
