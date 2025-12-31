#!/usr/bin/env python3
"""
测试注册功能修复效果
"""

import sys
import os
import time
import requests
import json

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from landppt.core.config import app_config

def test_register_api():
    """测试注册API"""
    print("=== 测试注册API ===")
    
    # 测试数据
    test_username = f"test_user_{int(time.time())}"
    test_password = "test123456"
    test_email = f"test_{int(time.time())}@example.com"
    
    print(f"测试用户名: {test_username}")
    print(f"测试邮箱: {test_email}")
    
    try:
        # 准备请求数据
        data = {
            'username': test_username,
            'password': test_password,
            'email': test_email
        }
        
        # 发送注册请求
        print("发送注册请求...")
        response = requests.post(
            'http://localhost:8000/api/auth/register',
            data=data,
            allow_redirects=False  # 不自动跟随重定向
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✓ 收到302重定向响应")
            location = response.headers.get('Location')
            print(f"重定向地址: {location}")
            
            # 检查是否有会话cookie
            session_cookie = response.cookies.get('session_id')
            if session_cookie:
                print(f"✓ 收到会话cookie: {session_cookie[:20]}...")
            else:
                print("⚠ 未收到会话cookie")
                
        elif response.status_code == 200:
            print("收到200响应（注册失败）")
            try:
                result = response.json()
                print(f"错误信息: {result.get('message', '未知错误')}")
            except:
                print(f"响应内容: {response.text}")
        else:
            print(f"✗ 意外状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
        return response.status_code == 302
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务正在运行")
        return False
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        return False

def test_user_in_database():
    """检查用户是否在数据库中"""
    print("\n=== 检查数据库中的用户 ===")
    
    try:
        import sqlite3
        
        if "sqlite:///" in app_config.database_url:
            db_path = app_config.database_url.replace("sqlite:///", "")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取最新用户
            cursor.execute("""
                SELECT id, username, email, is_active, created_at 
                FROM users 
                ORDER BY id DESC 
                LIMIT 5
            """)
            
            recent_users = cursor.fetchall()
            
            if recent_users:
                print("最近5个用户:")
                for user in recent_users:
                    print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}, 创建时间: {user[4]}")
            else:
                print("数据库中没有用户")
            
            # 统计用户数量
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            print(f"用户总数: {total_users}")
            
            conn.close()
            return True
        else:
            print("非SQLite数据库，跳过检查")
            return False
            
    except Exception as e:
        print(f"数据库检查失败: {e}")
        return False

def test_login_after_register():
    """测试注册后登录"""
    print("\n=== 测试注册后登录 ===")
    
    test_username = f"test_login_{int(time.time())}"
    test_password = "test123456"
    test_email = f"test_login_{int(time.time())}@example.com"
    
    try:
        # 1. 注册
        print("1. 注册用户...")
        register_data = {
            'username': test_username,
            'password': test_password,
            'email': test_email
        }
        
        register_response = requests.post(
            'http://localhost:8000/api/auth/register',
            data=register_data,
            allow_redirects=False
        )
        
        if register_response.status_code != 302:
            print(f"✗ 注册失败，状态码: {register_response.status_code}")
            return False
        
        print("✓ 注册成功")
        
        # 2. 尝试登录
        print("2. 尝试登录...")
        login_data = {
            'username': test_username,
            'password': test_password
        }
        
        login_response = requests.post(
            'http://localhost:8000/api/auth/login',
            data=login_data
        )
        
        print(f"登录响应状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            try:
                result = login_response.json()
                if result.get('success'):
                    print("✓ 登录成功")
                    print(f"会话ID: {result.get('session_id', '未知')}")
                    return True
                else:
                    print(f"✗ 登录失败: {result.get('message', '未知错误')}")
                    return False
            except:
                print(f"登录响应解析失败: {login_response.text}")
                return False
        else:
            print(f"✗ 登录请求失败，状态码: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        return False
    except Exception as e:
        print(f"✗ 登录测试出错: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试注册功能修复效果...")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: API注册
    print("\n" + "="*50)
    register_ok = test_register_api()
    
    # 测试2: 数据库检查
    print("\n" + "="*50)
    db_ok = test_user_in_database()
    
    # 测试3: 注册后登录
    print("\n" + "="*50)
    login_ok = test_login_after_register()
    
    # 总结
    print("\n" + "="*50)
    print("=== 测试结果总结 ===")
    print(f"注册API测试: {'✓ 通过' if register_ok else '✗ 失败'}")
    print(f"数据库检查: {'✓ 通过' if db_ok else '✗ 失败'}")
    print(f"注册后登录: {'✓ 通过' if login_ok else '✗ 失败'}")
    
    if all([register_ok, db_ok, login_ok]):
        print("\n🎉 所有测试通过！注册功能修复成功")
    else:
        print("\n⚠ 部分测试失败，需要进一步检查")
    
    print("\n测试完成。")

if __name__ == "__main__":
    main()