| 字段              | 类型                                      | 必填 | 默认值       | 约束              | 说明           |
| :---------------- | :---------------------------------------- | :--- | :----------- | :---------------- | :------------- |
| id                | bigint                                    | 是   | 自增         | 主键              | 作品ID         |
| author_id         | bigint                                    | 是   | -            | 外键 -> users.id  | 作者           |
| style_id          | bigint                                    | 是   | -            | 外键 -> styles.id | 风格           |
| title             | varchar(100)                              | 是   | '未命名作品' | -                 | 作品标题       |
| source_image_url  | varchar(255)                              | 是   | -            | -                 | 原图地址       |
| result_image_url  | varchar(255)                              | 是   | -            | -                 | 生成图地址     |
| visibility        | enum('private','profile','hall','hidden') | 是   | 'private'    | 枚举              | 可见状态       |
| like_count        | int                                       | 是   | 0            | >=0               | 点赞数         |
| comment_count     | int                                       | 是   | 0            | >=0               | 评论数         |
| download_count    | int                                       | 是   | 0            | >=0               | 下载数         |
| hall_published_at | datetime                                  | 否   | null         | -                 | 发布到大厅时间 |
| created_at        | datetime                                  | 是   | 当前时间     | -                 | 创建时间       |
| updated_at        | datetime                                  | 是   | 当前时间     | 自动更新          | 最后修改时间   |