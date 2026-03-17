| 字段              | 类型                                         | 必填 | 默认值    | 约束                | 说明           |
| :---------------- | :------------------------------------------- | :--- | :-------- | :------------------ | :------------- |
| id                | bigint                                       | 是   | 自增      | 主键                | 任务ID         |
| user_id           | bigint                                       | 是   | -         | 外键 -> users.id    | 发起人         |
| style_id          | bigint                                       | 是   | -         | 外键 -> styles.id   | 目标风格       |
| input_image_url   | varchar(255)                                 | 是   | -         | -                   | 输入图片地址   |
| status            | enum('pending','running','success','failed') | 是   | 'pending' | 枚举                | 任务状态       |
| error_msg         | varchar(255)                                 | 否   | null      | -                   | 失败原因       |
| output_artwork_id | bigint                                       | 否   | null      | 外键 -> artworks.id | 成功后关联作品 |
| created_at        | datetime                                     | 是   | 当前时间  | -                   | 创建时间       |
| started_at        | datetime                                     | 否   | null      | -                   | 开始执行时间   |
| finished_at       | datetime                                     | 否   | null      | -                   | 完成时间       |