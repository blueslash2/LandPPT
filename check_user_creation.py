#!/usr/bin/env python3
"""
检查用户创建情况的数据库调试脚本
"""

import sys
import os
import logging
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database():
    """检查数据库中的用户情况"""
    
    try:
        # 导入数据库模块
        from src.landppt.database.database import get_db, engine
        from src.landppt.database.models import User, Base
        
        logger.info("开始检查数据库...")
        
        # 检查数据库连接
        logger.info("测试数据库连接...")
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return
        
        # 获取数据库会话
        logger.info("获取数据库会话...")
        db = next(get_db())
        
        try:
            # 检查用户表是否存在
            logger.info("检查用户表结构...")
            try:
                user_count = db.query(User).count()
                logger.info(f"用户表存在，当前用户总数: {user_count}")
            except Exception as e:
                logger.error(f"查询用户表失败: {e}")
                logger.info("尝试创建用户表...")
                Base.metadata.create_all(engine)
                user_count = db.query(User).count()
                logger.info(f"用户表创建成功，当前用户总数: {user_count}")
            
            # 列出所有用户
            logger.info("列出所有用户...")
            users = db.query(User).all()
            
            if users:
                logger.info("找到以下用户:")
                for user in users:
                    logger.info(f"  ID: {user.id}")
                    logger.info(f"  用户名: {user.username}")
                    logger.info(f"  邮箱: {user.email}")
                    logger.info(f"  是否激活: {user.is_active}")
                    logger.info(f"  是否管理员: {user.is_admin}")
                    logger.info(f"  创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.created_at))}")
                    logger.info(f"  最后登录: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.last_login)) if user.last_login else '从未登录'}")
                    logger.info(f"  密码哈希: {user.password_hash[:20]}...")
                    logger.info("-" * 40)
            else:
                logger.info("数据库中没有用户")
            
            # 检查最新的用户
            latest_user = db.query(User).order_by(User.id.desc()).first()
            if latest_user:
                logger.info(f"最新用户: {latest_user.username} (ID: {latest_user.id})")
            
            # 检查用户表结构
            logger.info("检查用户表详细信息...")
            try:
                # 获取表结构信息
                from sqlalchemy import inspect
                inspector = inspect(engine)
                
                if 'users' in inspector.get_table_names():
                    columns = inspector.get_columns('users')
                    logger.info("用户表结构:")
                    for column in columns:
                        logger.info(f"  {column['name']}: {column['type']}")
                else:
                    logger.error("用户表不存在")
                    
            except Exception as e:
                logger.error(f"检查表结构失败: {e}")
            
        finally:
            db.close()
            logger.info("数据库会话已关闭")
            
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        logger.error("请确保在项目根目录下运行此脚本")
    except Exception as e:
        logger.error(f"检查数据库时发生异常: {e}", exc_info=True)

def test_user_creation():
    """测试用户创建过程"""
    
    try:
        from src.landppt.database.database import get_db
        from src.landppt.database.models import User
        from src.landppt.auth.auth_service import AuthService
        
        logger.info("开始测试用户创建过程...")
        
        # 获取数据库会话
        db = next(get_db())
        
        try:
            auth_service = AuthService()
            
            # 测试用户名
            test_username = f"test_user_{int(time.time())}"
            test_password = "test123456"
            test_email = f"{test_username}@example.com"
            
            logger.info(f"测试创建用户: {test_username}")
            
            # 记录创建前的用户数量
            count_before = db.query(User).count()
            logger.info(f"创建前用户数量: {count_before}")
            
            # 创建用户
            result = auth_service.register_user(db, test_username, test_password, test_email)
            
            logger.info(f"注册结果: {result}")
            
            if result["success"]:
                user = result["user"]
                logger.info(f"用户创建成功 - ID: {user.id}, 用户名: {user.username}")
                
                # 验证用户是否真的在数据库中
                verify_user = db.query(User).filter(User.username == test_username).first()
                if verify_user:
                    logger.info(f"用户验证成功 - 数据库中找到用户: {verify_user.username} (ID: {verify_user.id})")
                    
                    # 检查用户数量变化
                    count_after = db.query(User).count()
                    logger.info(f"创建后用户数量: {count_after}")
                    
                    if count_after == count_before + 1:
                        logger.info("用户数量增加正确")
                    else:
                        logger.error(f"用户数量异常 - 期望: {count_before + 1}, 实际: {count_after}")
                else:
                    logger.error("用户验证失败 - 数据库中找不到用户")
            else:
                logger.error(f"用户创建失败: {result['message']}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"测试用户创建时发生异常: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("开始数据库用户检查")
    logger.info("=" * 60)
    
    # 检查数据库
    check_database()
    
    logger.info("\n" + "=" * 60)
    logger.info("开始用户创建测试")
    logger.info("=" * 60)
    
    # 测试用户创建
    test_user_creation()
    
    logger.info("=" * 60)
    logger.info("检查完成")
    logger.info("=" * 60)