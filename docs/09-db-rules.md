1. 约束规则
   - users.username 唯一
   - artwork_likes (artwork_id,user_id) 联合主键（防重复点赞）
   - follows (follower_id,followee_id) 联合主键
   - follows 自关注禁止：follower_id <> followee_id
   - artworks.like_count/comment_count/download_count >= 0
   - 评论删除采用“状态删除”（status='deleted'），不做物理删
2. 索引建议
   - artworks (visibility, hall_published_at desc)
   - artworks (author_id, created_at desc)
   - generation_tasks (user_id, created_at desc)
   - comments (artwork_id, created_at asc)
   - follows (followee_id, created_at desc)
   - follows (follower_id, created_at desc)