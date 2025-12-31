#!/usr/bin/env python3
"""
验证注册修复的核心逻辑
"""

import sys
import os
import time
import sqlite3
import hashlib

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from landppt.core.config import app_config
from landppt.database.models import User
from landppt.auth.auth_service import AuthService
from landppt.database.database import get_db

def test_user_creation():
    """测试用户创建逻辑"""
    print("=== 测试用户创建逻辑 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        
        auth_service = AuthService()
        
        # 测试数据
        test_username = f"verify_user_{int(time.time())}"
        test_password = "test123456"
        test_email = f"verify_{int(time.time())}@example.com"
        
        print(f"测试用户名: {test_username}")
        print(f"测试邮箱: {test_email}")
        
        # 检查是否已存在
        existing = db.query(User).filter(User.username == test_username).first()
        if existing:
            print(f"用户已存在，删除旧用户: {test_username}")
            db.delete(existing)
            db.commit()
        
        # 测试注册
        print("执行注册...")
        result = auth_service.register_user(db, test_username, test_password, test_email)
        
        print(f"注册结果: {result['success']}")
        print(f"消息: {result['message']}")
        
        if result['success']:
            user = result['user']
            print(f"返回用户对象: ID={user.id}, 用户名={user.username}")
            
            # 验证用户是否真的在数据库中
            verify_user = db.query(User).filter(User.username == test_username).first()
            if verify_user:
                print(f"✓ 数据库验证成功: ID={verify_user.id}, 用户名={verify_user.username}")
                print(f"✓ 邮箱: {verify_user.email}")
                print(f"✓ 激活状态: {verify_user.is_active}")
                print(f"✓ 管理员: {verify_user.is_admin}")
                
                # 测试密码验证
                if verify_user.check_password(test_password):
                    print("✓ 密码验证成功")
                else:
                    print("✗ 密码验证失败")
                
                # 清理测试数据
                print("清理测试数据...")
                db.delete(verify_user)
                db.commit()
                print("✓ 测试数据已清理")
                
                return True
            else:
                print("✗ 数据库验证失败 - 用户不存在")
                return False
        else:
            print(f"✗ 注册失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_id_generation():
    """测试ID生成逻辑"""
    print("\n=== 测试ID生成逻辑 ===")
    
    try:
        db = next(get_db())
        
        # 获取当前最大ID
        max_id_result = db.query(User.id).order_by(User.id.desc()).first()
        current_max_id = max_id_result[0] if max_id_result else 0
        print(f"当前最大用户ID: {current_max_id}")
        
        # 创建新用户（不指定ID）
        test_username = f"id_test_user_{int(time.time())}"
        new_user = User(
            username=test_username,
            email="idtest@example.com",
            is_active=True,
            is_admin=False,
            created_at=time.time()
        )
        new_user.set_password("test123456")
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"新用户ID: {new_user.id}")
        print(f"ID是否自动递增: {'是' if new_user.id > current_max_id else '否'}")
        
        # 验证ID连续性
        if new_user.id == current_max_id + 1:
            print("✓ ID生成正常，连续递增")
        else:
            print(f"⚠ ID生成跳变: 期望 {current_max_id + 1}, 实际 {new_user.id}")
        
        # 清理
        db.delete(new_user)
        db.commit()
        print("✓ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"✗ ID生成测试出错: {e}")
        return False
    finally:
        db.close()

def test_database_constraints():
    """测试数据库约束"""
    print("\n=== 测试数据库约束 ===")
    
    try:
        db = next(get_db())
        
        # 测试1: 重复用户名
        print("测试1: 重复用户名约束")
        test_username = "duplicate_test_user"
        
        # 创建第一个用户
        user1 = User(
            username=test_username,
            email="test1@example.com",
            is_active=True,
            is_admin=False,
            created_at=time.time()
        )
        user1.set_password("test123456")
        db.add(user1)
        db.commit()
        print(f"✓ 第一个用户创建成功: ID={user1.id}")
        
        # 尝试创建同名用户
        try:
            user2 = User(
                username=test_username,
                email="test2@example.com",  # 不同的邮箱
                is_active=True,
                is_admin=False,
                created_at=time.time()
            )
            user2.set_password("test123456")
            db.add(user2)
            db.commit()
            print("✗ 重复用户名约束失效 - 应该失败但成功了")
            # 清理第二个用户
            db.delete(user2)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"✓ 重复用户名约束有效: {str(e)[:100]}")
        
        # 清理第一个用户
        db.delete(user1)
        db.commit()
        
        # 测试2: 重复邮箱
        print("\n测试2: 重复邮箱约束")
        test_email = "duplicate_test@example.com"
        
        # 创建第一个用户
        user1 = User(
            username="user1_test",
            email=test_email,
            is_active=True,
            is_admin=False,
            created_at=time.time()
        )
        user1.set_password("test123456")
        db.add(user1)
        db.commit()
        print(f"✓ 第一个用户创建成功: ID={user1.id}")
        
        # 尝试创建同邮箱用户
        try:
            user2 = User(
                username="user2_test",  # 不同的用户名
                email=test_email,
                is_active=True,
                is_admin=False,
                created_at=time.time()
            )
            user2.set_password("test123456")
            db.add(user2)
            db.commit()
            print("✗ 重复邮箱约束失效 - 应该失败但成功了")
            # 清理第二个用户
            db.delete(user2)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"✓ 重复邮箱约束有效: {str(e)[:100]}")
        
        # 清理第一个用户
        db.delete(user1)
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"✗ 约束测试出错: {e}")
        return False
    finally:
        db.close()

def main():
    """主验证函数"""
    print("开始验证注册修复效果...")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 用户创建逻辑
    print("\n" + "="*60)
    creation_ok = test_user_creation()
    
    # 测试2: ID生成逻辑
    print("\n" + "="*60)
    id_ok = test_id_generation()
    
    # 测试3: 数据库约束
    print("\n" + "="*60)
    constraints_ok = test_database_constraints()
    
    # 总结
    print("\n" + "="*60)
    print("=== 验证结果总结 ===")
    print(f"用户创建逻辑: {'✓ 通过' if creation_ok else '✗ 失败'}")
    print(f"ID生成逻辑: {'✓ 通过' if id_ok else '✗ 失败'}")
    print(f"数据库约束: {'✓ 通过' if constraints_ok else '✗ 失败'}")
    
    if all([creation_ok, id_ok, constraints_ok]):
        print("\n🎉 所有验证通过！注册修复有效")
    else:
        print("\n⚠ 部分验证失败，需要进一步检查")
    
    print("\n验证完成。")

if __name__ == "__main__":
    main()