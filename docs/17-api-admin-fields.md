管理员接口字段

1. `GET /admin/artworks`
   - Query: `page,size,visibility(optional),author_id(optional),keyword(optional)`
   - Success data:
     - `list[]` 每项包含
       - `id`
       - `title`
       - `visibility`
       - `author(id,username)`
       - `style(id,name)`
       - `like_count`
       - `comment_count`
       - `created_at`
       - `hall_published_at`
   - Errors: `40101 40301 40001`

2. `PATCH /admin/artworks/{id}/hide`
   - Request: `reason(string, required, 1-200)`
   - Success data:
     - `id`
     - `visibility='hidden'`
     - `updated_at`
   - Errors: `40101 40301 40401 42201`

3. `DELETE /admin/comments/{id}`
   - Request: `reason(string, optional)`
   - Success data:
     - `id`
     - `status='deleted'`
     - `updated_at`
   - Errors: `40101 40301 40401`

4. `GET /admin/users`
   - Query: `page,size,keyword(optional),status(optional)`
   - Success data:
     - `list[]` 每项包含
       - `id`
       - `account_code`
       - `username`
       - `role`
       - `status`
       - `avatar_url`
       - `created_at`
       - `updated_at`
       - `followers_count`
       - `following_count`
       - `artworks_count`
   - Errors: `40101 40301 40001`
   - Note:
     - 列表默认排除所有管理员账号，只显示普通用户

5. `PATCH /admin/users/{id}/block`
   - Request: 无
   - Success data:
     - `id`
     - `status='blocked'`
     - `updated_at`
   - Errors: `40101 40301 40401 42201`

6. `PATCH /admin/users/{id}/unblock`
   - Request: 无
   - Success data:
     - `id`
     - `status='active'`
     - `updated_at`
   - Errors: `40101 40301 40401 42201`
