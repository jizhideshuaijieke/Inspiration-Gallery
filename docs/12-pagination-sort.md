接口列表翻页排序规则

1. 分页请求参数
   - page：页码，从 1 开始，默认 1
   - size：每页条数，默认 20，最大 50
2. 列表响应结构

```
{  "code": 0,  "message": "ok",  "data": {    "list": [],    "page": 1,    "size": 20,    "total": 0,    "has_more": false  },  "request_id": "uuid" } 
```

1. 排序规则（默认）
   - 大厅流 /hall/feed：hall_published_at desc, id desc
   - 用户作品 /users/{id}/artworks：created_at desc, id desc
   - 评论 /artworks/{id}/comments：created_at asc, id asc
   - 管理作品列表 /admin/artworks：created_at desc, id desc
2. 参数校验
   - page < 1 或 size < 1 或 size > 50  -> 40001
   - 不支持的排序字段 -> 40001