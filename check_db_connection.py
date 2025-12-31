#!/usr/bin/env python3
"""
数据库连接检查工具
"""

import sys
import os
import sqlite3
import time

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from landppt.core.config import app_config

def check_database_connection():
    """检查数据库连接和表结构"""
    print("=== 数据库连接检查 ===")
    print(f"数据库URL: {app_config.database_url}")
    
    if "sqlite:///" in app_config.database_url:
        db_path = app_config.database_url.replace("sqlite:///", "")
        print(f"数据库文件路径: {db_path}")
        
        try:
            # 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("数据库连接成功")
            
            # 检查表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            print(f"存在的表: {table_names}")
            
            # 检查users表结构
            if 'users' in table_names:
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                print("\n=== users表结构 ===")
                for col in columns:
                    print(f"  {col[1]}: {col[2]} (主键: {'是' if col[5] else '否'})")
                
                # 检查是否有自增主键
                pk_columns = [col for col in columns if col[5]]  # pk字段
                if pk_columns:
                    pk_col = pk_columns[0]
                    print(f"主键列: {pk_col[1]} ({pk_col[2]})")
                    if 'INTEGER' in pk_col[2].upper():
                        print("✓ 主键是INTEGER类型，支持自增")
                    else:
                        print("⚠ 主键可能不支持自增")
                
                # 检查现有用户
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"\n现有用户数量: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT id, username, email, is_active, is_admin FROM users LIMIT 5")
                    users = cursor.fetchall()
                    print("前5个用户:")
                    for user in users:
                        print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}, 管理员: {user[4]}")
            
            # 检查user_sessions表
            if 'user_sessions' in table_names:
                cursor.execute("SELECT COUNT(*) FROM user_sessions")
                session_count = cursor.fetchone()[0]
                print(f"\n会话数量: {session_count}")
            
            # 测试插入新用户
            print("\n=== 测试用户插入 ===")
            test_username = f"test_user_{int(time.time())}"
            test_password = "test123456"
            test_email = "test@example.com"
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"测试用户 {test_username} 已存在")
            else:
                # 测试插入
                try:
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, email, is_active, is_admin, created_at, last_login)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (test_username, "test_hash", test_email, True, False, time.time(), None))
                    
                    new_user_id = cursor.lastrowid
                    conn.commit()
                    
                    print(f"✓ 测试用户插入成功，ID: {new_user_id}")
                    
                    # 验证插入
                    cursor.execute("SELECT id, username FROM users WHERE id = ?", (new_user_id,))
                    verify_user = cursor.fetchone()
                    if verify_user:
                        print(f"✓ 验证成功: ID={verify_user[0]}, 用户名={verify_user[1]}")
                    else:
                        print("✗ 验证失败: 用户不存在")
                    
                    # 清理测试数据
                    cursor.execute("DELETE FROM users WHERE id = ?", (new_user_id,))
                    conn.commit()
                    print("✓ 测试数据已清理")
                    
                except Exception as e:
                    print(f"✗ 测试插入失败: {e}")
                    conn.rollback()
            
            conn.close()
            print("\n=== 数据库检查完成 ===")
            return True
            
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    else:
        print("非SQLite数据库，跳过连接检查")
        return False

def test_user_model():
    """测试用户模型"""
    print("\n=== 用户模型测试 ===")
    
    try:
        from landppt.database.models import User
        
        # 创建测试用户
        user = User(
            username="test_model_user",
            email="test@model.com",
            is_active=True,
            is_admin=False,
            created_at=time.time()
        )
        
        # 测试密码设置
        test_password = "test123456"
        user.set_password(test_password)
        
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"密码哈希: {user.password_hash}")
        print(f"激活状态: {user.is_active}")
        print(f"管理员: {user.is_admin}")
        
        # 测试密码验证
        if user.check_password(test_password):
            print("✓ 密码验证成功")
        else:
            print("✗ 密码验证失败")
        
        if not user.check_password("wrong_password"):
            print("✓ 错误密码验证成功")
        else:
            print("✗ 错误密码验证失败")
            
        return True
        
    except Exception as e:
        print(f"用户模型测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始数据库连接检查...")
    
    # 检查数据库连接
    db_ok = check_database_connection()
    
    # 测试用户模型
    model_ok = test_user_model()
    
    if db_ok and model_ok:
        print("\n✓ 所有检查通过")
    else:
        print("\n✗ 部分检查失败")
        
    print("\n检查完成。")