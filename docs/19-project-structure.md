项目目录设计

1. web-user/（用户端 Vue2）
- src/views：页面（登录、风格转换、仓库、大厅、详情）
- src/components：复用组件（作品卡片、评论列表、上传器）
- src/api：接口请求封装
- src/store：vuex 状态管理
- src/router：路由与守卫
职责：面向普通用户的功能与交互。

2. web-admin/（管理端 Vue2）
- src/views：管理页面（作品管理、评论管理、用户管理）
- src/components：管理通用组件（表格筛选、弹窗）
- src/api：管理接口请求
- src/store：管理员状态
- src/router：管理路由与权限校验
职责：面向管理员的审核与治理能力。

3. server/（后端 API）
- app/router：路由层（参数校验、返回格式）
- app/service：业务层（权限、状态流转、规则）
- app/repository：数据访问层
- app/models：数据库模型
- app/schemas：请求/响应 DTO
职责：提供统一业务 API 与权限控制。

4. docs/（设计文档归档）
- 01-业务范围
- 02-数据模型
- 03-接口规范
- 04-开发计划
职责：沉淀需求、设计与开发约束，保证可追踪。
