#!/usr/bin/env python3
"""
调试注册问题的测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from landppt.database.models import User, Base
from landppt.auth.auth_service import AuthService
from landppt.core.config import app_config

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        # 创建引擎
        engine = create_engine(
            app_config.database_url,
            echo=True,  # 启用SQL日志
            connect_args={"check_same_thread": False} if "sqlite" in app_config.database_url else {}
        )
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"数据库连接成功: {result.scalar()}")
            
            # 检查表是否存在
            if "sqlite" in app_config.database_url:
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                table_names = [row[0] for row in tables]
                print(f"存在的表: {table_names}")
                
                if 'users' in table_names:
                    # 检查users表结构
                    columns = conn.execute(text("PRAGMA table_info(users)"))
                    print("users表结构:")
                    for col in columns:
                        print(f"  {col[1]}: {col[2]}")
                        
                    # 检查现有用户
                    users = conn.execute(text("SELECT id, username, email, is_active FROM users"))
                    print("现有用户:")
                    for user in users:
                        print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}")
                else:
                    print("users表不存在")
            
        return engine
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def test_user_registration():
    """测试用户注册"""
    print("\n=== 测试用户注册 ===")
    
    engine = test_database_connection()
    if not engine:
        return
    
    # 创建会话
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        auth_service = AuthService()
        
        # 测试注册新用户
        test_username = "test_user_001"
        test_password = "test123456"
        test_email = "test@example.com"
        
        print(f"尝试注册用户: {test_username}")
        
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == test_username).first()
        if existing_user:
            print(f"用户 {test_username} 已存在，先删除")
            db.delete(existing_user)
            db.commit()
        
        # 注册用户
        result = auth_service.register_user(db, test_username, test_password, test_email)
        
        print(f"注册结果: {result}")
        
        if result["success"]:
            print(f"用户注册成功: {result['user'].username}")
            print(f"用户ID: {result['user'].id}")
            print(f"创建时间: {result['user'].created_at}")
            
            # 验证用户是否真的在数据库中
            verify_user = db.query(User).filter(User.username == test_username).first()
            if verify_user:
                print(f"数据库验证 - 用户存在: {verify_user.username}, ID: {verify_user.id}")
            else:
                print("数据库验证失败 - 用户不存在")
                
            # 测试用户登录
            login_user = auth_service.authenticate_user(db, test_username, test_password)
            if login_user:
                print(f"登录测试成功: {login_user.username}")
            else:
                print("登录测试失败")
                
        else:
            print(f"注册失败: {result['message']}")
            
        # 检查数据库中的用户
        all_users = db.query(User).all()
        print(f"数据库中总用户数: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.username} (ID: {user.id}, 激活: {user.is_active})")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def test_session_creation():
    """测试会话创建"""
    print("\n=== 测试会话创建 ===")
    
    engine = create_engine(
        app_config.database_url,
        echo=True,
        connect_args={"check_same_thread": False} if "sqlite" in app_config.database_url else {}
    )
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        auth_service = AuthService()
        
        # 获取测试用户
        test_user = db.query(User).filter(User.username == "test_user_001").first()
        if not test_user:
            print("测试用户不存在，先创建")
            result = auth_service.register_user(db, "test_user_001", "test123456", "test@example.com")
            if result["success"]:
                test_user = result["user"]
            else:
                print("无法创建测试用户")
                return
        
        print(f"为用户 {test_user.username} 创建会话")
        session_id = auth_service.create_session(db, test_user)
        print(f"会话ID: {session_id}")
        
        # 验证会话
        from landppt.database.models import UserSession
        session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
        if session:
            print(f"会话创建成功 - 用户ID: {session.user_id}, 过期时间: {session.expires_at}")
        else:
            print("会话创建失败 - 数据库中找不到会话")
            
    except Exception as e:
        print(f"会话测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始调试注册问题...")
    print(f"数据库URL: {app_config.database_url}")
    
    # 测试数据库连接
    test_database_connection()
    
    # 测试用户注册
    test_user_registration()
    
    # 测试会话创建
    test_session_creation()
    
    print("\n调试完成。")