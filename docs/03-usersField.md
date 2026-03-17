| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| id | bigint | 是 | 自增 | 主键 | 内部用户主键，供关联表使用 |
| account_code | varchar(12) | 是 | 自动生成 | 唯一索引 | 面向用户的账号编号，格式为 `lghl` + 8 位数字 |
| username | varchar(32) | 是 | - | 唯一 | 用户名 |
| password_hash | varchar(255) | 是 | - | - | 哈希后的密码 |
| role | enum('user','admin') | 是 | 'user' | 枚举 | 角色 |
| status | enum('active','blocked') | 是 | 'active' | 枚举 | 账号状态 |
| avatar_url | varchar(255) | 否 | null | - | 头像地址 |
| created_at | datetime | 是 | 当前时间 | - | 创建时间 |
| updated_at | datetime | 是 | 当前时间 | 自动更新 | 最后修改时间 |
