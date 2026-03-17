/artworks/{id}、点赞、评论、关注接口字段

1. GET /artworks/{id}
   - Success data:
     id,title,source_image_url,result_image_url,visibility,style(id,code,name),author(id,username,avatar_url),like_count,comment_count,download_count,created_at
   - Errors: 40401 42201（private/hidden 且非作者或管理员时返回不可见）
2. PATCH /artworks/{id}
   - Request: title(string, optional), visibility(enum: private/profile/hall, optional)
   - Success data: id,title,visibility,updated_at
   - Errors: 40001 40101 40301 40401 42201（已下架作品作者只能改标题，不能自行改可见性）
3. DELETE /artworks/{id}
   - Success data: id, deleted=true
   - Errors: 40101 40301 40401
4. POST /artworks/{id}/like
   - Success data: artwork_id, liked=true, like_count
   - Errors: 40101 40401 40901
5. DELETE /artworks/{id}/like
   - Success data: artwork_id, liked=false, like_count
   - Errors: 40101 40401
6. GET /artworks/{id}/comments
   - Query: page,size
   - Success data: list[] 每项含
     id,content,status,created_at,user(id,username,avatar_url),parent_id
   - Errors: 40001 40401 42201
7. POST /artworks/{id}/comments
   - Request: content(string, required, 1-500), parent_id(bigint, optional)
   - Success data: id,artwork_id,user_id,parent_id,content,status,created_at
   - Errors: 40001 40101 40401 42201
8. POST /users/{id}/follow 与 DELETE /users/{id}/follow
   - Success data: user_id, followed(true/false), followers_count
   - Errors: 40101 40401 40901（自己关注自己或重复关注）
9. GET /users/me/notices
   - Query: page,size
   - Success data: list[] 每项含
     id,type='admin',action,title,body,created_at,artwork_id?,action_label?,target_view?
   - 说明:
     hide_artwork 会返回作品下架通知，并带 `action_label='去仓库查看'`、`target_view='me'`
   - Errors: 40001 40101
