| 实体             | 主键                       | 外键                                                         | 说明                    |
| :--------------- | :------------------------- | :----------------------------------------------------------- | :---------------------- |
| users            | id                         | -                                                            | 用户（含角色）          |
| styles           | id                         | -                                                            | 风格字典（梵高/水墨等） |
| generation_tasks | id                         | user_id -> users.id, style_id -> styles.id, output_artwork_id -> artworks.id | 风格生成任务            |
| artworks         | id                         | author_id -> users.id, style_id -> styles.id                 | 作品主表                |
| artwork_likes    | (artwork_id, user_id)      | artwork_id -> artworks.id, user_id -> users.id               | 点赞关系                |
| comments         | id                         | artwork_id -> artworks.id, user_id -> users.id, parent_id -> comments.id | 评论/回复               |
| follows          | (follower_id, followee_id) | follower_id -> users.id, followee_id -> users.id             | 关注关系                |