# HTTP协议基础 - IDOR学习系列

## 📚 学习目标
理解HTTP协议的基本概念，特别是与IDOR漏洞挖掘相关的认证、授权机制。

---

## 1. HTTP协议概述

**什么是HTTP？**
- HTTP (HyperText Transfer Protocol) 超文本传输协议
- 客户端-服务器模型：浏览器发送请求，服务器返回响应
- 无状态协议：每次请求都是独立的（需要通过Cookie/Session/Token维持状态）

**HTTP vs HTTPS**
- HTTP：明文传输，端口80
- HTTPS：加密传输（TLS/SSL），端口443

---

## 2. HTTP请求结构

一个完整的HTTP请求包含：

```http
GET /api/user/123 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Cookie: sessionid=abc123xyz
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{"key": "value"}
```

### 请求组成部分：

1. **请求行** (Request Line)
   - 方法：GET、POST、PUT、DELETE等
   - 路径：/api/user/123
   - 协议版本：HTTP/1.1

2. **请求头** (Headers)
   - Host: 目标服务器
   - Cookie: 身份凭证
   - Authorization: 认证信息
   - Content-Type: 数据类型

3. **请求体** (Body)
   - POST/PUT等方法携带的数据
   - JSON、XML、表单数据等

---

## 3. HTTP响应结构

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: sessionid=abc123xyz; HttpOnly; Secure
Access-Control-Allow-Origin: *

{
  "id": 123,
  "username": "alice",
  "email": "alice@example.com"
}
```

### 响应组成部分：

1. **状态行**
   - 协议版本：HTTP/1.1
   - 状态码：200
   - 状态消息：OK

2. **响应头**
   - Content-Type: 返回数据类型
   - Set-Cookie: 设置Cookie
   - Cache-Control: 缓存策略

3. **响应体**
   - 实际返回的数据（HTML、JSON、XML等）

---

## 4. HTTP方法（与IDOR相关）

| 方法 | 说明 | IDOR场景 | 示例 |
|------|------|----------|------|
| **GET** | 获取资源 | 查看他人信息 | `GET /api/user/456` |
| **POST** | 创建资源 | 较少见IDOR | `POST /api/order` |
| **PUT** | 更新资源 | 修改他人数据 | `PUT /api/user/456` |
| **DELETE** | 删除资源 | 删除他人资源 | `DELETE /api/order/789` |
| **PATCH** | 部分更新 | 修改他人字段 | `PATCH /api/profile/456` |

**IDOR重点：**
- GET方法：最常见的IDOR场景，通过修改ID查看他人数据
- PUT/DELETE：危害更大，可能修改或删除他人资源

---

## 5. 重要的HTTP Headers

### 5.1 认证相关Headers（IDOR核心）

**Cookie**
```http
Cookie: sessionid=abc123; userid=123
```
- 服务器通过Set-Cookie设置
- 浏览器自动携带
- 用于维持会话状态

**Authorization**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```
- Bearer Token：JWT令牌（常见）
- Basic Auth：用户名密码Base64编码

**自定义认证Header**
```http
X-API-Key: sk_live_abc123
X-Auth-Token: custom_token_here
X-User-Id: 123
```

### 5.2 其他重要Headers

**User-Agent**
- 标识客户端类型
- 有时服务器会根据此判断返回不同内容

**Referer**
- 请求来源页面
- 某些网站用于验证请求来源（不安全）

**Content-Type**
```
application/json - JSON数据
application/x-www-form-urlencoded - 表单数据
multipart/form-data - 文件上传
```

---

## 6. Cookie、Session、Token机制

### 6.1 Cookie-Session机制

**工作流程：**
```
1. 用户登录
   POST /login
   Body: {"username": "alice", "password": "pass123"}

2. 服务器验证并创建Session
   Response:
   Set-Cookie: sessionid=abc123xyz; HttpOnly; Secure

3. 后续请求自动携带Cookie
   GET /api/user/profile
   Cookie: sessionid=abc123xyz

4. 服务器根据sessionid识别用户
```

**Cookie属性：**
- `HttpOnly`: JavaScript无法读取（防XSS）
- `Secure`: 仅HTTPS传输
- `SameSite`: 防CSRF攻击
- `Domain/Path`: 作用域

**IDOR关联：**
服务器需要验证：sessionid对应的用户是否有权访问请求的资源ID

### 6.2 Token机制（JWT）

**JWT (JSON Web Token) 结构：**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMywidXNlcm5hbWUiOiJhbGljZSJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

分为三部分（用.分隔）：
1. Header（算法和类型）
2. Payload（用户数据）
3. Signature（签名）
```

**Payload示例（Base64解码后）：**
```json
{
  "userId": 123,
  "username": "alice",
  "exp": 1735689600
}
```

**使用方式：**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**IDOR关联：**
- 服务器从JWT中提取userId
- 验证请求的资源ID是否属于该userId
- 如果不验证，就存在IDOR漏洞

### 6.3 三者对比

| 特性 | Cookie-Session | JWT Token | API Key |
|------|----------------|-----------|---------|
| 存储位置 | 服务器Session存储 | 客户端存储 | 数据库存储 |
| 状态 | 有状态 | 无状态 | 有状态 |
| 性能 | 需查询Session | 无需查询 | 需查询数据库 |
| 安全性 | 较高 | 需注意Payload泄露 | 需妥善保管 |

---

## 7. HTTP状态码

### 常见状态码

**2xx 成功**
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 成功但无返回内容

**3xx 重定向**
- `301 Moved Permanently`: 永久重定向
- `302 Found`: 临时重定向

**4xx 客户端错误**
- `400 Bad Request`: 请求格式错误
- `401 Unauthorized`: 未认证（未登录）⚠️
- `403 Forbidden`: 已认证但无权限 ⚠️
- `404 Not Found`: 资源不存在
- `405 Method Not Allowed`: 方法不允许

**5xx 服务器错误**
- `500 Internal Server Error`: 服务器错误
- `502 Bad Gateway`: 网关错误
- `503 Service Unavailable`: 服务不可用

### IDOR相关的状态码

**正常情况：**
```
访问自己的资源: 200 OK
访问他人资源: 403 Forbidden (拒绝访问)
```

**存在IDOR漏洞：**
```
访问他人资源: 200 OK (返回了他人数据！)
```

**状态码误判：**
```
返回403但响应体包含数据 - 仍可能是漏洞
返回404但资源确实存在 - 可能是混淆手段
```

---

## 8. IDOR与HTTP协议的关系

### 8.1 认证 vs 授权

**认证 (Authentication)：你是谁？**
- 验证用户身份
- 通过Cookie/Token确认登录状态
- 对应状态码：401 Unauthorized

**授权 (Authorization)：你能做什么？**
- 验证用户权限
- 检查是否有权访问特定资源
- 对应状态码：403 Forbidden

**IDOR漏洞本质：**
```
应用完成了认证（知道你是alice）
但没有完成授权（没检查你是否能访问bob的数据）
```

### 8.2 典型IDOR场景分析

**场景1：查看用户信息**
```http
# Alice（用户ID=123）的请求
GET /api/user/123 HTTP/1.1
Cookie: sessionid=alice_session
→ 200 OK (返回Alice的信息)

# Alice修改ID尝试查看Bob的信息
GET /api/user/456 HTTP/1.1
Cookie: sessionid=alice_session
→ 应该返回403 Forbidden
→ 如果返回200 OK并显示Bob的信息 = IDOR漏洞
```

**场景2：修改用户资料**
```http
PUT /api/user/456/profile HTTP/1.1
Cookie: sessionid=alice_session
Content-Type: application/json

{
  "email": "hacker@evil.com"
}

→ 应该返回403 Forbidden
→ 如果返回200 OK并修改成功 = 严重IDOR漏洞
```

**场景3：下载文件**
```http
GET /api/download/invoice/789 HTTP/1.1
Cookie: sessionid=alice_session

→ 应该验证invoice_789是否属于Alice
→ 如果不验证直接返回文件 = IDOR漏洞
```

---

## 9. 实践练习（使用BurpSuite）

### 练习1：观察HTTP请求结构

1. 打开BurpSuite，设置浏览器代理
2. 访问任意网站（如PortSwigger Academy）
3. 在Proxy > HTTP history中观察：
   - 请求方法
   - 请求Headers（特别是Cookie、Authorization）
   - 响应状态码
   - 响应Headers（Set-Cookie）

### 练习2：手动修改请求

1. 找到一个包含ID参数的请求（如 /user/123）
2. 右键 > Send to Repeater
3. 在Repeater中修改ID值
4. 观察响应的变化
5. 思考：服务器是否验证了你的权限？

### 练习3：分析认证机制

1. 登录一个测试网站
2. 在Proxy > HTTP history中找到登录请求
3. 观察：
   - 登录请求的方法和数据格式
   - 响应中的Set-Cookie或Token
   - 后续请求如何携带认证信息

### 练习4：PortSwigger Labs

访问：https://portswigger.net/web-security/access-control

完成以下实验室（按顺序）：
1. Unprotected admin functionality
2. User role controlled by request parameter
3. User ID controlled by request parameter

---

## 10. 下一步学习

完成本文档学习后，你应该：

- ✅ 理解HTTP请求和响应的结构
- ✅ 知道Cookie、Session、Token的工作原理
- ✅ 理解认证与授权的区别
- ✅ 知道IDOR漏洞与HTTP协议的关系

**接下来：**
- 📖 学习IDOR漏洞的详细分类和挖掘技巧
- 🔧 练习使用BurpSuite进行IDOR测试
- 💻 编写Python脚本辅助测试

---

## 11. 参考资料

- [MDN - HTTP概述](https://developer.mozilla.org/zh-CN/docs/Web/HTTP)
- [PortSwigger - Access Control漏洞](https://portswigger.net/web-security/access-control)
- [OWASP - IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [JWT.io](https://jwt.io/) - JWT解码工具

---

**学习建议：**
- 不要只看理论，一定要用BurpSuite实际操作
- 每个概念都尝试在真实网站中找到对应的例子
- 做笔记记录你的发现和疑问
- 完成PortSwigger的实验室练习

加油！🚀
