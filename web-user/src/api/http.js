//Axios 是前端最常用的用来向后端服务器发送网络请求（GET, POST 等）的工具。
import axios from 'axios'

const http = axios.create({
  //在发请求时，如果你写 http.get('/users')，Axios 会自动把 baseURL 拼接到前面。

  //process 是 Node.js 中的一个全局对象，它代表了当前正在运行的 Node.js 进程
  //process.env.VUE_APP_API_BASE_URL 是一个环境变量，存储在 .env 文件中
  //它的值可以根据不同的环境（开发、生产等）进行配置。
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 10000
})


//axios实例发出的每个网络请求，在发送之前都会先经过这个函数
http.interceptors.request.use((config) => {
  //去浏览器的本地存储（localStorage）中寻找名字叫 token 的数据。
  // 通常，用户 /login 页面登录成功后，前端会把后端返回的 Token（身份令牌，类似门禁卡）存在这里。
  const token = localStorage.getItem('token')

  //如果找到了 Token，就在请求的 headers（请求头）里加一个 Authorization 字段，
  //格式为 Bearer + Token字符串。
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default http
