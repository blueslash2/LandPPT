#!/usr/bin/env python3
"""
验证登录API修复的脚本
用于在生产环境中测试/landppt/api/auth/login接口
"""

import requests
import json
import sys

def test_login_api_fix():
    """测试登录API修复效果"""
    print("=== 验证登录API修复 ===")
    
    # 测试URL - 请根据实际环境修改
    login_url = "http://localhost:8000/landppt/api/auth/login"
    
    print(f"测试URL: {login_url}")
    
    # 测试用例1: 错误的用户名密码（应该返回200）
    print("\n--- 测试1: 错误的用户名密码 ---")
    data1 = {"username": "wrong_user", "password": "wrong_password"}
    
    try:
        response = requests.post(login_url, data=data1, allow_redirects=False, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 状态码正确（200）")
            
            try:
                result = response.json()
                if result.get('success') == False and 'message' in result:
                    print(f"✓ 错误信息正确: {result['message']}")
                else:
                    print("✗ 响应格式不符合预期")
                    print(f"响应内容: {result}")
            except:
                print("✗ 无法解析JSON响应")
                print(f"原始响应: {response.text}")
        else:
            print(f"✗ 状态码不符合预期，期望200，实际: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试用例2: 尝试使用默认管理员账户（如果存在）
    print("\n--- 测试2: 默认管理员账户 ---")
    data2 = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(login_url, data=data2, allow_redirects=False, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ 状态码正确（302重定向）")
            
            # 检查重定向URL
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"✓ 重定向URL: {redirect_url}")
            else:
                print("✗ 未找到重定向URL")
            
            # 检查cookie
            if 'session_id' in response.cookies:
                print("✓ 成功设置session_id cookie")
            else:
                print("✗ 未设置session_id cookie")
                
        elif response.status_code == 200:
            print("✗ 管理员登录失败，返回200状态码")
            try:
                result = response.json()
                print(f"错误信息: {result.get('message', '未知错误')}")
            except:
                print(f"原始响应: {response.text}")
        else:
            print(f"✗ 意外的状态码: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    print("\n=== 验证完成 ===")
    print("\n预期行为总结:")
    print("- 登录失败: 返回200状态码 + JSON错误信息")
    print("- 登录成功: 返回302重定向 + 设置session_id cookie")
    print("\n如果以上测试都通过，说明登录API修复成功！")

if __name__ == "__main__":
    test_login_api_fix()