#!/usr/bin/env python3
"""
简化版调试脚本 - 使用内置SQLite
"""

import sqlite3
import os
import sys
import time
import hashlib

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from landppt.core.config import app_config

def check_database():
    """检查数据库文件和表结构"""
    print("=== 数据库检查 ===")
    print(f"数据库URL: {app_config.database_url}")
    
    # 提取数据库文件路径
    if "sqlite:///" in app_config.database_url:
        db_path = app_config.database_url.replace("sqlite:///", "")
        print(f"数据库文件路径: {db_path}")
        
        # 检查文件是否存在
        if os.path.exists(db_path):
            print("数据库文件存在")
            
            # 连接数据库
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"存在的表: {[table[0] for table in tables]}")
                
                # 检查users表
                if ('users',) in tables:
                    print("\n=== users表结构 ===")
                    cursor.execute("PRAGMA table_info(users)")
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  {col[1]}: {col[2]}")
                    
                    print("\n=== users表数据 ===")
                    cursor.execute("SELECT id, username, email, is_active, created_at FROM users")
                    users = cursor.fetchall()
                    print(f"用户数量: {len(users)}")
                    for user in users:
                        print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}, 创建时间: {user[4]}")
                
                # 检查user_sessions表
                if ('user_sessions',) in tables:
                    print("\n=== user_sessions表数据 ===")
                    cursor.execute("SELECT id, session_id, user_id, expires_at, is_active FROM user_sessions")
                    sessions = cursor.fetchall()
                    print(f"会话数量: {len(sessions)}")
                    for session in sessions:
                        print(f"  ID: {session[0]}, 会话ID: {session[1]}, 用户ID: {session[2]}, 过期: {session[3]}, 激活: {session[4]}")
                
                conn.close()
                
            except Exception as e:
                print(f"数据库连接错误: {e}")
        else:
            print("数据库文件不存在")
    else:
        print("非SQLite数据库，跳过文件检查")

def test_registration_logic():
    """测试注册逻辑"""
    print("\n=== 注册逻辑测试 ===")
    
    # 模拟注册过程
    test_username = "test_debug_user"
    test_password = "test123456"
    test_email = "test@example.com"
    
    print(f"测试注册: {test_username}")
    
    # 模拟密码哈希
    password_hash = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"密码哈希: {password_hash}")
    
    # 检查数据库中是否已存在
    if "sqlite:///" in app_config.database_url:
        db_path = app_config.database_url.replace("sqlite:///", "")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查用户是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"用户 {test_username} 已存在，ID: {existing[0]}")
                # 删除测试用户
                cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
                conn.commit()
                print("已删除现有测试用户")
            
            # 模拟注册过程
            current_time = time.time()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, is_active, is_admin, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (test_username, password_hash, test_email, True, False, current_time, None))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            print(f"用户插入成功，ID: {user_id}")
            
            # 验证用户是否存在
            cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if user:
                print(f"验证成功 - 用户存在: ID={user[0]}, 用户名={user[1]}, 邮箱={user[2]}")
            else:
                print("验证失败 - 用户不存在")
            
            # 清理测试数据
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            print("清理测试数据完成")
            
            conn.close()
            
        except Exception as e:
            print(f"注册逻辑测试出错: {e}")
            import traceback
            traceback.print_exc()

def check_fastapi_routes():
    """检查FastAPI路由配置"""
    print("\n=== FastAPI路由检查 ===")
    
    # 检查auth/routes.py文件
    routes_file = "src/landppt/auth/routes.py"
    if os.path.exists(routes_file):
        print(f"找到路由文件: {routes_file}")
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找注册相关的路由
        if "/api/auth/register" in content:
            print("找到 /api/auth/register 路由")
            
            # 查找注册逻辑
            if "register_user" in content:
                print("找到 register_user 调用")
            
            # 查找返回逻辑
            if "RedirectResponse" in content:
                print("找到 RedirectResponse 使用")
                
            if 'status_code=302' in content:
                print("找到 302 状态码设置")
                
            # 查找失败返回逻辑
            if 'return {' in content and '"success": False' in content:
                print("找到失败返回逻辑")
        else:
            print("未找到 /api/auth/register 路由")
    else:
        print(f"路由文件不存在: {routes_file}")

if __name__ == "__main__":
    print("开始简化版调试...")
    
    # 检查数据库
    check_database()
    
    # 测试注册逻辑
    test_registration_logic()
    
    # 检查路由配置
    check_fastapi_routes()
    
    print("\n简化版调试完成。")