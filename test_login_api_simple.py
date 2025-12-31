#!/usr/bin/env python3
"""
简化的登录API测试脚本
用于验证/landppt/api/auth/login接口的行为
"""

import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8000"
LOGIN_API_URL = f"{BASE_URL}/landppt/api/auth/login"

def test_login_behavior():
    """测试登录API的行为"""
    logger.info("=== 测试登录API行为 ===")
    
    # 测试数据
    test_cases = [
        {
            "name": "错误的用户名密码",
            "username": "wrong_user",
            "password": "wrong_password",
            "expected_status": 200,  # 失败应该返回200
            "expected_success": False
        },
        {
            "name": "正确的用户名密码（假设）",
            "username": "admin",
            "password": "admin123",
            "expected_status": 302,  # 成功应该返回302
            "expected_success": True
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n--- 测试: {test_case['name']} ---")
        
        data = {
            "username": test_case['username'],
            "password": test_case['password']
        }
        
        try:
            # 发送登录请求，不允许重定向
            response = requests.post(LOGIN_API_URL, data=data, allow_redirects=False)
            
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            # 检查状态码是否符合预期
            if response.status_code == test_case['expected_status']:
                logger.info(f"✓ 状态码符合预期: {response.status_code}")
            else:
                logger.error(f"✗ 状态码不符合预期，期望: {test_case['expected_status']}, 实际: {response.status_code}")
            
            # 分析响应内容
            if response.status_code == 200:
                # 失败情况 - 应该返回JSON错误信息
                try:
                    result = response.json()
                    logger.info(f"失败响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    if 'success' in result and result['success'] == test_case['expected_success']:
                        logger.info("✓ 响应格式符合预期")
                    else:
                        logger.error("✗ 响应格式不符合预期")
                        
                except Exception as e:
                    logger.error(f"✗ 无法解析JSON响应: {e}")
                    logger.info(f"原始响应: {response.text}")
                    
            elif response.status_code == 302:
                # 成功情况 - 应该返回重定向
                redirect_url = response.headers.get('Location')
                logger.info(f"✓ 重定向到: {redirect_url}")
                
                # 检查是否有设置cookie
                cookies = response.cookies
                if 'session_id' in cookies:
                    logger.info(f"✓ 设置了session_id cookie: {cookies['session_id'][:20]}...")
                else:
                    logger.error("✗ 未设置session_id cookie")
                    
            else:
                logger.error(f"✗ 意外的状态码: {response.status_code}")
                logger.info(f"响应文本: {response.text}")
                
        except Exception as e:
            logger.error(f"请求异常: {e}")

def test_login_flow():
    """测试完整的登录流程"""
    logger.info("\n=== 测试完整登录流程 ===")
    
    # 1. 首先测试失败情况
    logger.info("\n--- 1. 测试登录失败 ---")
    data = {"username": "wrong_user", "password": "wrong_password"}
    
    try:
        response = requests.post(LOGIN_API_URL, data=data, allow_redirects=False)
        
        if response.status_code == 200:
            logger.info("✓ 登录失败返回200状态码")
            
            try:
                result = response.json()
                if result.get('success') == False and 'message' in result:
                    logger.info(f"✓ 返回了错误信息: {result['message']}")
                else:
                    logger.error("✗ 错误信息格式不符合预期")
            except:
                logger.error("✗ 无法解析JSON响应")
        else:
            logger.error(f"✗ 登录失败返回了意外的状态码: {response.status_code}")
            
    except Exception as e:
        logger.error(f"登录失败测试异常: {e}")
    
    # 2. 然后测试成功情况（假设使用默认管理员账户）
    logger.info("\n--- 2. 测试登录成功 ---")
    data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(LOGIN_API_URL, data=data, allow_redirects=False)
        
        if response.status_code == 302:
            logger.info("✓ 登录成功返回302重定向")
            
            redirect_url = response.headers.get('Location')
            if redirect_url:
                logger.info(f"✓ 重定向到: {redirect_url}")
            else:
                logger.error("✗ 未找到重定向URL")
                
            # 检查cookie
            if 'session_id' in response.cookies:
                logger.info("✓ 成功设置了session_id cookie")
            else:
                logger.error("✗ 未设置session_id cookie")
                
        else:
            logger.error(f"✗ 登录成功返回了意外的状态码: {response.status_code}")
            
            # 如果是200，可能是密码错误或其他问题
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"错误信息: {result}")
                except:
                    logger.info(f"响应文本: {response.text}")
                    
    except Exception as e:
        logger.error(f"登录成功测试异常: {e}")

if __name__ == "__main__":
    # 测试基本行为
    test_login_behavior()
    
    # 测试完整流程
    test_login_flow()
    
    logger.info("\n=== 测试完成 ===")
    logger.info("预期行为:")
    logger.info("- 登录失败: 返回200状态码 + JSON错误信息")
    logger.info("- 登录成功: 返回302重定向 + 设置session_id cookie")