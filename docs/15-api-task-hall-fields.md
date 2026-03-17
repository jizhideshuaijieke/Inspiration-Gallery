生成任务 + 大厅接口字段

模式说明：MVP 默认单用户串行推理，不使用任务队列。

1. POST /tasks/style-transfer
   - Request: style_id(bigint, required), input_image_url(string, required)
   - Success data: task_id(bigint), status(pending|running)
   - Errors: 40001 40101 42201 50301
2. GET /tasks/{id}
   - Success data: id,status,error_msg,output_artwork_id,created_at,started_at,finished_at
   - Errors: 40101 40301 40401
3. POST /artworks
   - Request: task_id(bigint, required), title(string, optional)
   - Success data: artwork_id(bigint), visibility, created_at
   - Errors: 40001 40101 40301 40401 42201
4. GET /hall/feed
   - Query: page,size
   - Success data: list[] 每项含
     id,title,result_image_url,style(id,code,name),author(id,username,avatar_url),like_count,comment_count,download_count,hall_published_at
   - Errors: 40001
