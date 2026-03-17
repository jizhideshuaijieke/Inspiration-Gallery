鉴权与权限规则

1. 认证方式
   - Authorization: Bearer <token>
   - 未登录或 token 无效统一返回 40101
2. 角色权限矩阵
   - 游客：可看大厅、作品详情、评论列表、用户主页
   - 用户：游客权限 + 生成任务 + 点赞评论 + 关注 + 管理自己的作品 + 查看自己的管理员通知
   - 管理员：用户权限 + 管理接口（下架作品、删评论、查用户、封禁普通用户）
3. 归属校验（ownership）
   - PATCH/DELETE /artworks/{id}：仅作者本人或管理员
   - GET /artworks/{id}、GET /artworks/{id}/comments：private/hidden 作品仅作者本人或管理员可见
   - GET /tasks/{id}：仅任务发起人或管理员
   - DELETE /admin/comments/{id}：仅管理员
   - PATCH /admin/users/{id}/block：仅管理员，且不能封禁管理员账号
   - PATCH /admin/users/{id}/unblock：仅管理员，且不能操作管理员账号
   - GET /users/me/notices：仅当前登录用户本人
   - POST/DELETE /users/{id}/follow：禁止关注自己（冲突返回 40901）
4. 鉴权执行顺序
   - 先验 token -> 再验角色 -> 再验资源归属 -> 最后验业务状态
   - 任一步失败立即返回（40101/40301/40401/40901/42201）
