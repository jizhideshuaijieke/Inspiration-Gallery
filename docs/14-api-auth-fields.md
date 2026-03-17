认证接口字段定义

1. `POST /auth/register`
   - Request:
     - `username` string, required, 3-32, `^[a-zA-Z0-9_]+$`
     - `password` string, required, 6-20
   - Success data:
     - `user.id` bigint
     - `user.account_code` string, 固定 12 位，格式 `lghl` + 8 位数字
     - `user.username` string
     - `user.role` string
     - `token` string
   - Errors:
     - `40001` 参数错误
     - `40901` 用户名已存在

2. `POST /auth/login`
   - Request:
     - `account_code` string, optional, 与 `username` 二选一
       - 普通用户格式：`lghl` + 8 位数字
       - 默认管理员格式：`admin1433223`
     - `username` string, optional
     - `password` string, required
   - Success data:
     - `user.id` bigint
     - `user.account_code` string
     - `user.username` string
     - `user.role` string
     - `token` string
   - Errors:
     - `40001` 参数错误
     - `40101` 账号编号/用户名或密码错误
     - `40301` 账号被禁用

3. 默认管理员账号
   - `account_code`: `admin1433223`
   - `password`: `admin1433223`
   - 登录成功后应进入管理端，不进入普通用户大厅
