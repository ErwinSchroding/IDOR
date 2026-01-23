# BurpSuite实践指南 - IDOR测试专用

## 🎯 目标
掌握使用BurpSuite进行IDOR漏洞测试的核心技巧。

---

## 1. BurpSuite核心模块（IDOR相关）

### 1.1 Proxy（代理）
**作用：** 拦截和查看浏览器与服务器之间的所有HTTP流量

**关键功能：**
- HTTP history：查看所有请求历史
- Intercept：拦截请求，手动修改后再发送
- WebSockets history：查看WebSocket通信

**IDOR使用技巧：**
```
1. 关注包含ID的请求：
   /api/user/123
   /order/details?orderId=456
   /download?fileId=789

2. 观察认证方式：
   Cookie: sessionid=...
   Authorization: Bearer ...

3. 寻找模式：
   用户操作 -> 请求中的ID -> 响应数据
```

### 1.2 Repeater（重放器）
**作用：** 手动修改并重复发送请求，观察响应变化

**快捷键：**
- 发送请求：`Ctrl/Cmd + R`
- 切换请求/响应视图：`Ctrl/Cmd + Space`

**IDOR测试流程：**
```
1. 在Proxy中找到目标请求
2. 右键 > Send to Repeater
3. 修改请求中的ID参数
4. 点击Send观察响应
5. 对比原始请求的响应
```

**实例：**
```http
原始请求（查看自己的订单）：
GET /api/order/123 HTTP/1.1
Cookie: sessionid=alice_session

响应：200 OK
{"orderId": 123, "user": "alice", "total": 99.99}

修改后（尝试查看他人订单）：
GET /api/order/124 HTTP/1.1
Cookie: sessionid=alice_session

如果响应：200 OK
{"orderId": 124, "user": "bob", "total": 199.99}
→ 存在IDOR漏洞！
```

### 1.3 Intruder（入侵者）
**作用：** 自动化批量修改参数，适合遍历ID

**攻击类型：**
1. **Sniper（狙击手）** - 单个参数位置，逐一替换
2. **Battering ram** - 多个位置使用相同payload
3. **Pitchfork** - 多个位置使用对应的payload
4. **Cluster bomb** - 所有payload组合

**IDOR常用：Sniper模式**

**步骤：**
```
1. Send to Intruder
2. 在Positions标签中，清除所有标记（Clear §）
3. 选中ID值，点击Add § 标记攻击位置
4. 在Payloads标签中设置payload：
   - Payload type: Numbers
   - From: 1  To: 1000  Step: 1
5. 点击Start attack
6. 分析结果：查看状态码、响应长度、响应内容
```

**过滤技巧：**
```
在结果中点击列标题排序：
- Status: 找出返回200的请求
- Length: 不同长度可能表示不同响应
- 添加Grep规则提取特定内容
```

### 1.4 Comparer（比较器）
**作用：** 对比两个请求或响应的差异

**使用场景：**
```
对比访问自己资源和他人资源的响应差异：
1. 请求1：GET /api/user/123 (自己的ID)
2. 请求2：GET /api/user/456 (他人的ID)
3. 将两个响应Send to Comparer
4. 对比差异，确认是否泄露他人信息
```

### 1.5 Logger（日志）
**作用：** 更强大的请求历史查看工具（Burp Suite 2023+版本）

**过滤技巧：**
```
Filter by:
- Method: GET, POST, PUT, DELETE
- Status code: 200, 403, 404
- Search: 搜索包含特定关键词的请求
- Extension: .json, .xml
```

---

## 2. BurpSuite配置（IDOR测试优化）

### 2.1 代理设置

**浏览器代理配置：**
```
地址: 127.0.0.1
端口: 8080
```

**HTTPS证书安装：**
```
1. 浏览器访问 http://burp
2. 下载CA证书
3. 安装到浏览器受信任的根证书
```

### 2.2 Proxy拦截规则

**建议设置（减少干扰）：**
```
Proxy > Options > Intercept Client Requests

仅拦截特定域名：
- 勾选 "And URL Is in target scope"

不拦截静态资源：
- 添加规则：File extension matches: css|js|png|jpg|gif|svg
```

### 2.3 Target Scope（目标范围）

**添加目标网站到scope：**
```
1. 在Proxy > HTTP history中找到目标请求
2. 右键 > Add to scope
3. Target > Site map 中只显示scope内的请求
```

**好处：**
- 过滤无关请求
- 集中分析目标网站
- Intruder攻击时更安全

---

## 3. IDOR测试工作流程

### 工作流程图
```
1. 正常使用应用，观察流量
   ↓
2. 识别包含ID的请求
   ↓
3. 标记可疑请求
   ↓
4. Repeater手动测试
   ↓
5. Intruder批量测试
   ↓
6. 分析结果，确认漏洞
   ↓
7. 编写PoC和报告
```

### 3.1 识别可疑请求

**关键词识别：**
```
URL参数：
?id=123
?userId=456
?orderId=789
?fileId=abc
?documentId=xyz

路径参数：
/api/user/123
/order/456/details
/file/download/789

请求体：
{"userId": 123}
{"resourceId": "abc-def-ghi"}
```

**关注的请求类型：**
```
✅ 查看个人信息: GET /api/profile
✅ 查看订单详情: GET /api/order/{id}
✅ 下载文件: GET /api/download/{id}
✅ 查看私密消息: GET /api/message/{id}
✅ 修改个人资料: PUT /api/user/{id}
✅ 删除资源: DELETE /api/resource/{id}
```

### 3.2 手动测试步骤

**步骤1：建立基线**
```
1. 用账号A登录，访问自己的资源
2. 记录请求和响应
3. 注意ID值和返回的数据
```

**步骤2：尝试越权**
```
1. 保持账号A的Session
2. 修改ID为账号B的资源ID
3. 发送请求
4. 分析响应
```

**步骤3：判断漏洞**
```
响应分析：

200 OK + 返回他人数据 → IDOR漏洞确认 ✅
403 Forbidden → 正常，有权限验证 ❌
404 Not Found → 可能有验证，或资源不存在 ⚠️
500 Error → 可能是ID格式错误 ⚠️
200 OK + 返回空数据 → 需进一步分析 ⚠️
```

**注意事项：**
```
1. 检查响应体，不只看状态码
   有些应用返回200但响应体中有错误信息

2. 注意响应长度
   长度差异可能表示数据泄露

3. 检查响应头
   某些敏感信息可能在Headers中
```

### 3.3 批量测试（Intruder）

**场景：遍历用户ID 1-1000**

**配置Intruder：**
```http
GET /api/user/§123§ HTTP/1.1
Host: example.com
Cookie: sessionid=alice_session
```

**Payload设置：**
```
Payload type: Numbers
From: 1
To: 1000
Step: 1

可选：添加Payload Processing
- Add prefix: 可能ID有前缀
- Encode: URL编码、Base64等
```

**结果分析：**
```
1. 按Status排序，找200响应
2. 按Length排序，找异常长度
3. 使用Grep提取关键信息：
   Options > Grep - Extract
   添加规则提取 "username", "email" 等字段
```

**节流设置（防止被封）：**
```
Resource pool > Maximum concurrent requests: 1-5
添加延迟：每个请求间隔500-1000ms
```

---

## 4. 高级技巧

### 4.1 Match and Replace

**自动修改请求：**
```
Proxy > Options > Match and Replace

示例：自动替换Cookie
Type: Request header
Match: Cookie: sessionid=.*
Replace: Cookie: sessionid=test_session
```

### 4.2 使用Extensions（插件）

**推荐IDOR相关插件：**

1. **Autorize**
   - 自动化权限测试
   - 用两个不同权限账号测试

2. **Auto Repeater**
   - 自动重放请求并修改参数

3. **Logger++**
   - 增强日志记录功能

**安装方式：**
```
Extensions > BApp Store > 搜索 > Install
```

### 4.3 Session Handling Rules

**场景：Token自动刷新**
```
Project options > Sessions > Session Handling Rules

添加规则：
1. Scope: 选择目标域名
2. Rule Actions: 运行宏自动获取新Token
```

### 4.4 使用Collaborator（带外测试）

**场景：盲IDOR检测**
```
某些IDOR不直接返回数据，但会触发通知

测试方法：
1. 修改email参数为Collaborator地址
2. 检查是否收到请求
3. 确认是否可以接管他人账号
```

---

## 5. 实战演练（PortSwigger Labs）

### Lab 1: User ID controlled by request parameter
**目标：** 访问他人的API密钥

**步骤：**
```
1. 登录自己的账号（wiener）
2. 访问 My Account 页面
3. BurpSuite观察请求: GET /my-account?id=wiener
4. Send to Repeater
5. 修改 id=carlos
6. 发送请求，获取carlos的API密钥
7. 提交答案
```

**学习点：**
- 通过URL参数控制用户ID
- 无权限验证

### Lab 2: User ID controlled by request parameter with unpredictable user IDs
**目标：** 找到carlos的GUID并访问

**步骤：**
```
1. 登录账号
2. 观察请求: GET /my-account?id=a1b2c3d4-...
3. 在博客文章中找到carlos的链接
4. 提取carlos的GUID
5. 修改请求访问carlos的账户
```

**学习点：**
- 不可预测的ID（GUID、UUID）
- 但可以通过其他途径泄露

### Lab 3: User ID controlled by request parameter with data leakage in redirect
**目标：** 从重定向响应中获取数据

**步骤：**
```
1. 访问 /my-account?id=carlos
2. 服务器返回302重定向
3. 但在Repeater中查看原始响应
4. 302响应体中包含carlos的数据
```

**学习点：**
- 重定向前泄露数据
- 不要只看浏览器显示，要看原始响应

---

## 6. 测试清单

**每次测试IDOR时，检查以下项目：**

```
□ 是否识别了所有包含ID的请求？
□ 是否测试了GET/POST/PUT/DELETE等不同方法？
□ 是否测试了路径参数和查询参数？
□ 是否测试了请求体中的ID？
□ 是否尝试了ID+1、ID-1、ID*10等变化？
□ 是否测试了不同格式的ID（数字、UUID、Hash）？
□ 是否检查了响应体、响应头、状态码？
□ 是否对比了访问自己资源和他人资源的差异？
□ 是否测试了批量遍历ID？
□ 是否记录了测试结果和PoC？
```

---

## 7. 常见问题

**Q1: Intruder攻击很慢？**
```
A: 免费版Burp有速度限制
   解决方案：
   1. 使用Professional版
   2. 手动用Python脚本测试
   3. 减少payload数量
```

**Q2: 请求被服务器拦截？**
```
A: 可能触发了WAF或限流
   解决方案：
   1. 降低请求速度
   2. 添加延迟
   3. 轮换User-Agent
   4. 使用代理IP
```

**Q3: 如何测试需要两个账号的场景？**
```
A: 使用两个浏览器或浏览器配置文件
   1. Chrome正常模式：账号A
   2. Chrome隐身模式：账号B
   3. 分别配置Burp代理
   4. 或使用不同端口的Burp实例
```

---

## 8. 练习作业

**作业1：基础操作**
- 访问PortSwigger Academy
- 完成3个Access Control labs
- 使用Repeater和Intruder
- 截图记录过程

**作业2：真实网站分析（仅限授权）**
- 选择一个测试网站（自己的或有授权的）
- 识别10个包含ID的请求
- 测试是否存在IDOR
- 记录测试结果

**作业3：对比测试**
- 创建两个测试账号
- 用Comparer对比访问同一资源的响应
- 分析差异

---

## 9. 下一步

完成本指南后：
- ✅ 熟练使用BurpSuite核心功能
- ✅ 能够识别和测试IDOR漏洞
- ✅ 掌握手动和自动化测试方法

**继续学习：**
- 📖 IDOR漏洞详细分类
- 💻 编写Python自动化脚本
- 🎯 真实SRC漏洞挖掘

加油！🔥
