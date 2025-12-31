#!/usr/bin/env python3
"""
详细的注册功能调试脚本
"""

import sys
import os
import logging
import requests
import json
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_register():
    """测试注册功能"""
    
    # 测试配置
    base_url = "http://localhost:8000"
    test_username = f"testuser_{int(time.time())}"
    test_password = "test123456"
    test_email = f"{test_username}@example.com"
    
    logger.info(f"开始测试注册功能")
    logger.info(f"测试用户名: {test_username}")
    logger.info(f"测试邮箱: {test_email}")
    
    try:
        # 测试数据库连接
        logger.info("测试数据库连接...")
        
        # 发送注册请求
        logger.info("发送注册请求...")
        register_data = {
            'username': test_username,
            'password': test_password,
            'email': test_email
        }
        
        logger.info(f"注册请求数据: {register_data}")
        
        response = requests.post(
            f"{base_url}/api/auth/register",
            data=register_data,
            allow_redirects=False  # 不自动跟随重定向
        )
        
        logger.info(f"注册响应状态码: {response.status_code}")
        logger.info(f"注册响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            logger.info("注册成功 - 收到302重定向响应")
            logger.info(f"重定向地址: {response.headers.get('Location')}")
            
            # 检查是否有Set-Cookie头
            set_cookie = response.headers.get('Set-Cookie')
            if set_cookie:
                logger.info(f"收到Set-Cookie: {set_cookie[:50]}...")
            else:
                logger.warning("未收到Set-Cookie头")
                
            # 尝试跟随重定向获取用户信息
            if 'session_id' in response.cookies:
                logger.info("使用会话Cookie获取用户信息...")
                me_response = requests.get(
                    f"{base_url}/api/auth/me",
                    cookies={'session_id': response.cookies['session_id']}
                )
                
                logger.info(f"获取用户信息响应状态码: {me_response.status_code}")
                if me_response.status_code == 200:
                    user_info = me_response.json()
                    logger.info(f"当前用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
                else:
                    logger.error(f"获取用户信息失败: {me_response.text}")
            else:
                logger.warning("响应中没有session_id cookie")
                
        else:
            logger.error(f"注册失败 - 状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            
            try:
                error_data = response.json()
                logger.error(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.error("无法解析响应为JSON")
        
        # 测试用户是否存在于数据库
        logger.info("检查用户是否存在于数据库...")
        
        # 尝试登录新注册的用户
        logger.info("尝试登录新注册的用户...")
        login_data = {
            'username': test_username,
            'password': test_password
        }
        
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            data=login_data
        )
        
        logger.info(f"登录响应状态码: {login_response.status_code}")
        if login_response.status_code == 200:
            login_result = login_response.json()
            logger.info(f"登录成功: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
        else:
            logger.error(f"登录失败: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到服务器 - 请确保服务正在运行")
        logger.error("尝试连接地址: {}".format(base_url))
    except Exception as e:
        logger.error(f"测试过程中发生异常: {e}", exc_info=True)

def check_server_status():
    """检查服务器状态"""
    base_url = "http://localhost:8000"
    
    try:
        logger.info("检查服务器状态...")
        response = requests.get(f"{base_url}/api/auth/check")
        logger.info(f"服务器状态检查响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"服务器状态: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            logger.error(f"服务器状态检查失败: {response.text}")
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到服务器")
        return False
    except Exception as e:
        logger.error(f"检查服务器状态时发生异常: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("开始详细的注册功能调试")
    logger.info("=" * 60)
    
    # 检查服务器状态
    if not check_server_status():
        logger.error("服务器未运行，请先启动服务")
        sys.exit(1)
    
    # 运行注册测试
    test_register()
    
    logger.info("=" * 60)
    logger.info("调试完成")
    logger.info("=" * 60)