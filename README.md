# IDOR漏洞挖掘学习计划

欢迎来到为期4周的IDOR漏洞挖掘学习之旅！

## 📚 学习目标

1. 掌握IDOR漏洞的原理和挖掘技巧
2. 能够在真实场景中发现IDOR漏洞
3. 开发一个自动化IDOR测试工具
4. 完成一篇技术论文

## 📅 学习计划（4周）

### 第一周：基础知识
**时间：** 第1周（当前周）

**学习内容：**
- [x] HTTP协议基础
- [ ] BurpSuite实践
- [ ] IDOR基础理论
- [ ] PortSwigger Labs练习

**学习文档：**
1. [01-HTTP协议基础.md](./01-HTTP协议基础.md)
2. [02-BurpSuite实践指南.md](./02-BurpSuite实践指南.md)
3. [03-IDOR基础理论.md](./03-IDOR基础理论.md)

**本周目标：**
- 理解HTTP请求/响应结构
- 掌握Cookie、Session、Token机制
- 理解认证与授权的区别
- 熟练使用BurpSuite Proxy、Repeater、Intruder
- 完成至少3个PortSwigger Access Control Labs

---

### 第二周：手工挖掘
**时间：** 第2周

**学习内容：**
- IDOR识别技巧
- 手工测试方法
- 不同ID类型的测试策略
- 绕过技巧（编码、哈希）

**实践目标：**
- 完成所有PortSwigger Access Control Labs
- 在DVWA或WebGoat中练习
- 建立自己的测试checklist

---

### 第三周：自动化 + Python脚本
**时间：** 第3周

**学习内容：**
- Python requests库
- 批量测试脚本编写
- 处理不同认证方式
- 结果分析和输出

**实践目标：**
- 编写基础的ID遍历脚本
- 实现Cookie/Token认证处理
- 自动化结果分析

---

### 第四周：工具开发 + SRC实战
**时间：** 第4周

**学习内容：**
- 工具架构设计
- 核心功能实现
- 真实SRC平台测试（需授权）
- 论文撰写

**交付成果：**
- 一个功能完整的IDOR自动化测试工具
- 实战测试报告（如果有SRC成果）
- 技术论文初稿

---

## 📖 学习文档导航

### 基础知识（第一周）
1. **HTTP协议基础**
   - HTTP请求/响应结构
   - 认证与授权机制
   - Cookie、Session、Token
   - [查看文档](./01-HTTP协议基础.md)

2. **BurpSuite实践指南**
   - 核心模块使用（Proxy、Repeater、Intruder）
   - IDOR测试工作流程
   - 实战演练
   - [查看文档](./02-BurpSuite实践指南.md)

3. **IDOR基础理论**
   - 漏洞原理和分类
   - 常见场景
   - 真实案例分析
   - [查看文档](./03-IDOR基础理论.md)

---

## 🎯 本周任务清单

### Day 1-2：HTTP协议学习
- [ ] 阅读《01-HTTP协议基础.md》
- [ ] 使用BurpSuite观察真实网站的HTTP流量
- [ ] 识别Cookie、Token等认证方式
- [ ] 理解认证与授权的区别

### Day 3-4：BurpSuite实践
- [ ] 阅读《02-BurpSuite实践指南.md》
- [ ] 配置BurpSuite和浏览器
- [ ] 练习使用Repeater修改请求
- [ ] 练习使用Intruder批量测试

### Day 5-6：IDOR理论学习
- [ ] 阅读《03-IDOR基础理论.md》
- [ ] 理解IDOR的各种分类
- [ ] 学习真实案例
- [ ] 总结IDOR测试方法

### Day 7：实战练习
- [ ] PortSwigger Lab: Unprotected admin functionality
- [ ] PortSwigger Lab: User role controlled by request parameter
- [ ] PortSwigger Lab: User ID controlled by request parameter
- [ ] 完成本周学习笔记

---

## 🔗 推荐资源

### 在线靶场
- [PortSwigger Academy](https://portswigger.net/web-security/access-control) - Access Control专题
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [DVWA](https://dvwa.co.uk/)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)

### 工具下载
- [BurpSuite Community Edition](https://portswigger.net/burp/communitydownload)
- [Python](https://www.python.org/downloads/)

### 学习材料
- [OWASP Testing Guide - IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [MDN - HTTP](https://developer.mozilla.org/zh-CN/docs/Web/HTTP)
- [HackerOne Hacktivity](https://hackerone.com/hacktivity) - 搜索IDOR案例

---

## 📝 学习笔记模板

建议创建一个学习笔记文件，记录：

```markdown
# IDOR学习笔记

## 日期：2026-01-XX

### 今日学习内容
-

### 重点知识点
-

### 实践练习
- Lab名称：
- 关键步骤：
- 学到的技巧：

### 疑问
-

### 明日计划
-
```

---

## 💡 学习建议

1. **循序渐进**
   - 不要跳过基础知识
   - 每个概念都要亲手实践
   - 不懂就问，及时解决疑问

2. **多实践**
   - 理论学习占30%，实践占70%
   - 完成所有推荐的Labs
   - 尝试在真实网站中识别IDOR（仅限授权测试）

3. **做笔记**
   - 记录学习心得
   - 整理测试技巧
   - 收集案例和PoC

4. **保持合法**
   - 只在授权范围内测试
   - 使用靶场练习
   - 遵守SRC平台规则

---

## 📧 进度追踪

| 周次 | 主题 | 状态 | 完成日期 |
|------|------|------|----------|
| 第1周 | 基础知识 | 进行中 | - |
| 第2周 | 手工挖掘 | 未开始 | - |
| 第3周 | 自动化脚本 | 未开始 | - |
| 第4周 | 工具开发 | 未开始 | - |

---

## 🎉 开始学习

从第一周的HTTP协议基础开始吧！

👉 [01-HTTP协议基础.md](./01-HTTP协议基础.md)

---

**祝学习顺利！有任何问题随时讨论。**
