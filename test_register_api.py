#!/usr/bin/env python3
"""
测试注册API的完整脚本
"""

import requests
import json
import time
import sys

def test_register_api():
    """测试注册API"""
    
    base_url = "http://localhost:8000"
    
    # 生成测试数据
    timestamp = str(int(time.time()))
    test_username = f"testuser_{timestamp}"
    test_password = "test123456"
    test_email = f"{test_username}@example.com"
    
    print(f"测试注册API")
    print(f"用户名: {test_username}")
    print(f"邮箱: {test_email}")
    print("-" * 50)
    
    try:
        # 1. 测试注册API
        print("1. 测试注册API...")
        register_data = {
            'username': test_username,
            'password': test_password,
            'email': test_email
        }
        
        response = requests.post(
            f"{base_url}/api/auth/register",
            data=register_data,
            allow_redirects=False
        )
        
        print(f"注册响应状态码: {response.status_code}")
        print(f"注册响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ 注册成功 - 收到302重定向响应")
            print(f"重定向地址: {response.headers.get('Location')}")
            
            # 检查Cookie
            if 'session_id' in response.cookies:
                print("✅ 收到session_id cookie")
                session_id = response.cookies['session_id']
                print(f"会话ID: {session_id[:20]}...")
                
                # 2. 测试获取当前用户信息
                print("\n2. 测试获取当前用户信息...")
                me_response = requests.get(
                    f"{base_url}/api/auth/me",
                    cookies={'session_id': session_id}
                )
                
                print(f"获取用户信息响应状态码: {me_response.status_code}")
                if me_response.status_code == 200:
                    user_info = me_response.json()
                    print(f"当前用户信息:")
                    print(json.dumps(user_info, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ 获取用户信息失败: {me_response.text}")
                    
                # 3. 测试登录新注册的用户
                print("\n3. 测试登录新注册的用户...")
                login_data = {
                    'username': test_username,
                    'password': test_password
                }
                
                login_response = requests.post(
                    f"{base_url}/api/auth/login",
                    data=login_data
                )
                
                print(f"登录响应状态码: {login_response.status_code}")
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print("✅ 登录成功:")
                    print(json.dumps(login_result, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ 登录失败: {login_response.text}")
                    
            else:
                print("⚠️  未收到session_id cookie")
                
        elif response.status_code == 200:
            print("❌ 注册失败 - 收到200响应")
            try:
                error_data = response.json()
                print(f"错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"响应内容: {response.text}")
        else:
            print(f"❌ 注册失败 - 意外状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 - 请确保服务正在运行")
        print(f"尝试连接地址: {base_url}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False
        
    return True

def test_duplicate_registration():
    """测试重复注册"""
    
    base_url = "http://localhost:8000"
    
    # 使用相同的测试数据
    timestamp = str(int(time.time()))
    test_username = f"duplicate_user_{timestamp}"
    test_password = "test123456"
    test_email = f"{test_username}@example.com"
    
    print(f"\n测试重复注册")
    print(f"用户名: {test_username}")
    print("-" * 50)
    
    try:
        # 第一次注册
        print("1. 第一次注册...")
        register_data = {
            'username': test_username,
            'password': test_password,
            'email': test_email
        }
        
        response1 = requests.post(
            f"{base_url}/api/auth/register",
            data=register_data,
            allow_redirects=False
        )
        
        print(f"第一次注册状态码: {response1.status_code}")
        
        # 第二次注册（应该失败）
        print("2. 第二次注册（应该失败）...")
        response2 = requests.post(
            f"{base_url}/api/auth/register",
            data=register_data,
            allow_redirects=False
        )
        
        print(f"第二次注册状态码: {response2.status_code}")
        
        if response2.status_code == 200:
            try:
                error_data = response2.json()
                print(f"重复注册错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                if not error_data.get('success'):
                    print("✅ 重复注册正确被拒绝")
                else:
                    print("❌ 重复注册应该被拒绝")
            except:
                print(f"第二次注册响应: {response2.text}")
        else:
            print(f"❌ 第二次注册意外状态码: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ 测试重复注册时发生异常: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("开始注册API测试")
    print("=" * 60)
    
    # 测试基本注册功能
    success1 = test_register_api()
    
    # 测试重复注册
    success2 = test_duplicate_registration()
    
    print("\n" + "=" * 60)
    print("测试完成")
    if success1 and success2:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)