# IDOR漏洞基础理论

## 🎯 学习目标
深入理解IDOR漏洞的原理、分类、危害和挖掘技巧。

---

## 1. IDOR定义

**IDOR (Insecure Direct Object Reference)**
不安全的直接对象引用

### 官方定义（OWASP）
> 当应用程序基于用户提供的输入直接访问对象，且未进行适当的权限检查时，就会发生IDOR漏洞。攻击者可以通过修改输入参数来访问未授权的对象。

### 通俗解释
```
你登录了银行网站查看自己的账户：
https://bank.com/account?id=123

你发现把ID改成124就能看到别人的账户信息：
https://bank.com/account?id=124

这就是IDOR漏洞。
```

---

## 2. IDOR漏洞原理

### 2.1 正常的授权流程

```
用户请求 → 认证检查 → 授权检查 → 返回数据
         (是谁？)     (能访问吗？)
```

**代码示例（安全）：**
```python
@app.route('/api/order/<order_id>')
def get_order(order_id):
    # 1. 认证：检查用户是否登录
    if not current_user.is_authenticated:
        return "401 Unauthorized"

    # 2. 授权：检查订单是否属于当前用户
    order = Order.query.get(order_id)
    if order.user_id != current_user.id:
        return "403 Forbidden"

    # 3. 返回数据
    return jsonify(order.to_dict())
```

### 2.2 存在IDOR的代码

```python
@app.route('/api/order/<order_id>')
def get_order(order_id):
    # 1. 认证：检查用户是否登录 ✅
    if not current_user.is_authenticated:
        return "401 Unauthorized"

    # 2. 授权：缺少权限检查！ ❌
    order = Order.query.get(order_id)

    # 3. 直接返回数据 ❌
    return jsonify(order.to_dict())
```

**问题：**
- 验证了用户已登录（认证）
- 但没有验证用户是否有权访问该订单（授权）
- 任何登录用户都可以访问任意订单

---

## 3. IDOR分类

### 3.1 按操作类型分类

#### 1. 查看型IDOR（最常见）
**描述：** 未授权查看他人数据

**示例：**
```http
GET /api/user/profile?userId=456
GET /api/invoice/download?id=789
GET /api/private-message/123
```

**危害：**
- 信息泄露
- 隐私侵犯
- 敏感数据暴露

**真实案例：**
- Facebook漏洞：通过修改相册ID查看他人私密照片
- Uber漏洞：通过修改行程ID查看他人行程记录

#### 2. 修改型IDOR
**描述：** 未授权修改他人数据

**示例：**
```http
PUT /api/user/456
Body: {"email": "hacker@evil.com", "phone": "123456"}

POST /api/order/789/cancel
PATCH /api/profile/456 {"bio": "Hacked!"}
```

**危害：**
- 数据篡改
- 账户接管
- 业务逻辑破坏

**真实案例：**
- Instagram漏洞：修改他人账号密码
- PayPal漏洞：修改他人收款地址

#### 3. 删除型IDOR
**描述：** 未授权删除他人资源

**示例：**
```http
DELETE /api/post/456
DELETE /api/file/789
POST /api/account/123/delete
```

**危害：**
- 数据丢失
- 服务中断
- 恶意破坏

#### 4. 创建型IDOR（较少见）
**描述：** 以他人身份创建资源

**示例：**
```http
POST /api/create-order
Body: {"userId": 456, "items": [...]}

POST /api/send-message
Body: {"fromUserId": 789, "message": "..."}
```

**危害：**
- 身份伪造
- 栽赃陷害
- 业务欺诈

### 3.2 按ID类型分类

#### 1. 数字ID（最常见）

**特征：**
- 连续递增：1, 2, 3, 4...
- 容易预测和遍历

**示例：**
```
/api/user/123
/order/456
/file/download?id=789
```

**测试方法：**
```
ID + 1: 124
ID - 1: 122
ID * 10: 1230
随机数: 999, 1000, 5000
```

#### 2. UUID/GUID

**特征：**
- 唯一标识符：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- 看似不可预测

**示例：**
```
/api/user/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**测试方法：**
```
1. 信息泄露：在页面源码、API响应中查找其他用户的UUID
2. 响应中泄露：/api/users/list 可能返回所有用户的UUID
3. 博客评论：用户头像链接包含UUID
4. 邮件/通知：包含UUID的链接
```

**仍可能存在IDOR：**
- UUID虽然不可预测，但如果能获取到，依然可以测试IDOR

#### 3. 哈希ID

**特征：**
- MD5、SHA1等：`5d41402abc4b2a76b9719d911017c592`
- 看似随机

**示例：**
```
/api/invoice/5d41402abc4b2a76b9719d911017c592
```

**测试方法：**
```
1. 哈希碰撞：如果是MD5(user_id)，可以计算其他用户的哈希
2. 彩虹表：常见ID的哈希值预计算
3. 信息泄露：在其他地方找到哈希值
```

**示例：**
```
如果ID是MD5(user_id)：
用户123: MD5("123") = 202cb962ac59075b964b07152d234b70
可以计算其他用户：
用户124: MD5("124") = c8ffe9a587b126f152ed3d89a146b445
```

#### 4. Base64编码

**特征：**
- 看似随机：`dXNlcjoxMjM=`
- 实际是编码后的明文

**示例：**
```
/api/user/dXNlcjoxMjM=
解码后: user:123
```

**测试方法：**
```
1. Base64解码
2. 修改明文
3. Base64重新编码
4. 发送请求
```

**示例：**
```bash
# 解码
echo "dXNlcjoxMjM=" | base64 -d
# 输出: user:123

# 修改为 user:456 后编码
echo -n "user:456" | base64
# 输出: dXNlcjo0NTY=

# 使用新的ID发送请求
GET /api/user/dXNlcjo0NTY=
```

#### 5. 自定义格式

**特征：**
- 企业自定义：`ORD-2024-00123`
- 混合格式：`user_123_profile`

**示例：**
```
/api/order/ORD-2024-00123
/api/file/doc_456_final
```

**测试方法：**
```
1. 分析格式规律
2. 修改数字部分
3. 保持格式不变
```

---

## 4. IDOR常见场景

### 4.1 用户信息类

```
场景：查看/修改用户资料

请求示例：
GET /api/user/profile?id=123
PUT /api/user/123/settings
GET /avatar?userId=456

测试点：
- 个人资料
- 头像/照片
- 邮箱/手机号
- 地址信息
- 账号设置
```

### 4.2 订单/交易类

```
场景：查看/修改订单信息

请求示例：
GET /api/order/789
GET /order/details?orderId=456
POST /api/order/123/refund

测试点：
- 订单详情
- 交易记录
- 发票下载
- 物流信息
- 退款操作
```

### 4.3 文件/资源类

```
场景：下载/删除文件

请求示例：
GET /api/download?fileId=abc123
GET /file/view/document_456.pdf
DELETE /api/file/789

测试点：
- 文档下载
- 图片查看
- 视频访问
- 备份文件
- 私密资源
```

### 4.4 消息/通知类

```
场景：查看私密消息

请求示例：
GET /api/message/123
GET /api/conversation?chatId=456
POST /api/message/789/delete

测试点：
- 私信内容
- 聊天记录
- 系统通知
- 评论管理
```

### 4.5 管理功能类

```
场景：管理员功能越权

请求示例：
GET /api/admin/users
POST /api/admin/user/456/ban
GET /api/dashboard/stats

测试点：
- 用户管理
- 权限设置
- 系统配置
- 数据统计
```

---

## 5. IDOR危害等级

### 5.1 危害评估矩阵

| 操作类型 | 敏感数据 | 危害等级 | CVSS评分参考 |
|---------|---------|---------|-------------|
| 查看 | 公开信息 | 低 | 3.0-4.0 |
| 查看 | 个人信息 | 中 | 4.0-6.9 |
| 查看 | 敏感信息（身份证、银行卡） | 高 | 7.0-8.9 |
| 修改 | 个人资料 | 高 | 7.0-8.9 |
| 修改 | 账号密码/邮箱 | 严重 | 9.0-10.0 |
| 删除 | 用户数据 | 高 | 7.0-8.9 |
| 删除 | 系统数据 | 严重 | 9.0-10.0 |

### 5.2 业务影响

**1. 信息泄露**
- 用户隐私暴露
- 商业机密泄露
- 合规风险（GDPR、个人信息保护法）

**2. 账户接管**
- 修改邮箱后重置密码
- 修改手机号接管账号
- 修改认证信息

**3. 财产损失**
- 修改收款地址
- 取消他人订单
- 非法交易

**4. 声誉损害**
- 用户信任丧失
- 品牌形象受损
- 法律诉讼风险

---

## 6. IDOR vs 其他漏洞

### 6.1 IDOR vs 越权漏洞（Broken Access Control）

**关系：**
- IDOR是越权漏洞的一种
- 越权漏洞是更广泛的概念

**区别：**
```
IDOR：
- 通过修改对象引用（ID）实现越权
- 水平越权为主（同级别用户间）
- 示例：user123访问user456的数据

其他越权：
- 垂直越权：普通用户访问管理员功能
- 功能层面的权限绕过
- 示例：普通用户访问 /admin/dashboard
```

### 6.2 IDOR vs 信息泄露

**IDOR是主动攻击：**
```
攻击者需要：
1. 猜测或枚举ID
2. 主动修改请求
3. 尝试访问
```

**信息泄露是被动：**
```
示例：
- API返回过多信息
- 错误信息泄露路径
- 源码泄露
```

---

## 7. 防御措施（开发者视角）

### 7.1 核心原则

**永远不要信任用户输入的ID！**

### 7.2 代码层防御

#### 1. 服务端权限验证（必须）

```python
# 方案1：直接验证所属关系
def get_order(order_id):
    order = Order.query.get(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return order

# 方案2：查询时带上用户条件
def get_order(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    return order
```

#### 2. 使用不可预测的ID

```python
# 使用UUID代替自增ID
import uuid

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

#### 3. 间接对象引用

```python
# 不直接暴露数据库ID
# 使用映射表或Token

user_token_map = {
    "token_abc": user_id_123,
    "token_xyz": user_id_456
}

def get_profile(token):
    user_id = user_token_map.get(token)
    # 验证并返回
```

#### 4. 接口限流

```python
# 防止批量遍历
@limiter.limit("10 per minute")
def get_user_profile(user_id):
    # ...
```

### 7.3 架构层防御

```
1. 统一权限中间件
   所有请求必须经过权限检查

2. API网关
   在网关层做统一鉴权

3. 最小权限原则
   用户只能访问必要的数据
```

---

## 8. 挖掘技巧总结

### 8.1 识别阶段

```
1. 寻找包含ID的请求
   - URL参数：?id=123
   - 路径参数：/user/123
   - 请求体：{"userId": 123}
   - Cookie：userId=123

2. 关注敏感功能
   - 个人中心
   - 订单查询
   - 文件下载
   - 消息查看
   - 删除/修改操作

3. 分析ID类型
   - 数字、UUID、哈希、编码
```

### 8.2 测试阶段

```
1. 手动测试
   - Repeater修改ID
   - 观察响应变化
   - 对比自己和他人数据

2. 批量测试
   - Intruder遍历ID
   - 分析状态码和响应长度
   - 提取关键信息

3. 深度测试
   - 测试不同HTTP方法
   - 测试编码/哈希变种
   - 测试边界值
```

### 8.3 确认阶段

```
1. 验证数据真实性
   - 确认返回的是他人数据
   - 不是虚假/测试数据

2. 评估危害
   - 泄露了什么信息
   - 能否修改/删除
   - 业务影响程度

3. 编写PoC
   - 完整的请求/响应
   - 复现步骤
   - 截图证明
```

---

## 9. 真实案例学习

### 案例1：Facebook相册IDOR
**漏洞描述：**
- 通过修改相册ID查看他人私密照片

**技术细节：**
```http
GET /api/album/photos?album_id=123456
→ 返回当前用户相册

修改为：
GET /api/album/photos?album_id=789012
→ 返回他人私密相册
```

**根本原因：**
- 仅验证用户登录状态
- 未验证相册所属权

**赏金：** $10,000

### 案例2：Uber行程信息泄露
**漏洞描述：**
- 通过UUID获取他人行程详情

**技术细节：**
```http
GET /api/trip/abc-def-123
→ 包含起点、终点、时间、司机信息
```

**UUID获取途径：**
- 分享链接泄露
- 客服邮件包含UUID

**根本原因：**
- UUID虽不可预测，但可通过其他途径获取
- 获取后无权限验证

**赏金：** $3,000

### 案例3：PayPal修改收款地址
**漏洞描述：**
- 修改他人账户的收款邮箱

**技术细节：**
```http
PUT /api/user/settings
Body: {
  "userId": 789,
  "paypal_email": "hacker@evil.com"
}
```

**根本原因：**
- 信任客户端传来的userId
- 未验证userId与当前用户的关系

**赏金：** $10,500

---

## 10. 练习题

### 练习1：代码审计
识别以下代码的IDOR漏洞：

```python
@app.route('/api/delete-comment/<comment_id>')
def delete_comment(comment_id):
    if not current_user.is_authenticated:
        return "Login required", 401

    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return "Deleted", 200
```

<details>
<summary>答案</summary>

**漏洞：**
- 没有验证comment是否属于当前用户
- 任何登录用户都可以删除任意评论

**修复：**
```python
comment = Comment.query.get(comment_id)
if comment.author_id != current_user.id:
    return "Forbidden", 403
```
</details>

### 练习2：绕过测试
如何测试以下ID格式的IDOR？

```
/api/invoice/INV-2024-00123
```

<details>
<summary>答案</summary>

**测试方法：**
```
1. 递增数字部分：INV-2024-00124
2. 递减：INV-2024-00122
3. 跨年份：INV-2023-00123
4. 大幅跳跃：INV-2024-00200
```
</details>

---

## 11. 学习资源

**在线靶场：**
- PortSwigger Academy - Access Control专题
- OWASP WebGoat - Access Control
- HackTheBox - 多个靶机包含IDOR
- PentesterLab - IDOR Badge

**博客文章：**
- OWASP Testing Guide - IDOR
- HackerOne公开报告（搜索IDOR）
- Bugcrowd漏洞披露

**视频教程：**
- YouTube: "IDOR Explained"
- YouTube: "Bugbounty IDOR tricks"

---

## 12. 下一步

完成本文档后，你应该：
- ✅ 理解IDOR漏洞原理
- ✅ 知道IDOR的分类和场景
- ✅ 掌握基本的挖掘思路

**第一周剩余任务：**
- 📖 复习HTTP协议基础
- 🔧 练习BurpSuite操作
- 🎯 完成PortSwigger Labs（至少3个）

**第二周预告：**
- 手工挖掘技巧
- 高级绕过方法
- 批量测试技巧

继续加油！🚀
