| 字段       | 类型                               | 必填 | 默认值    | 约束                | 说明                 |
| :--------- | :--------------------------------- | :--- | :-------- | :------------------ | :------------------- |
| id         | bigint                             | 是   | 自增      | 主键                | 评论ID               |
| artwork_id | bigint                             | 是   | -         | 外键 -> artworks.id | 所属作品             |
| user_id    | bigint                             | 是   | -         | 外键 -> users.id    | 评论人               |
| parent_id  | bigint                             | 否   | null      | 外键 -> comments.id | 父评论（回复时使用） |
| content    | varchar(500)                       | 是   | -         | -                   | 评论内容             |
| status     | enum('visible','hidden','deleted') | 是   | 'visible' | 枚举                | 评论状态             |
| created_at | datetime                           | 是   | 当前时间  | -                   | 创建时间             |
| updated_at | datetime                           | 是   | 当前时间  | 自动更新            | 最后修改时间         |