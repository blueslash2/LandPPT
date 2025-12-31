#!/usr/bin/env python3
"""
调试登录API的详细脚本
用于测试/landppt/api/auth/login接口并输出详细信息
"""

import requests
import json
import logging
import sys
import time

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8000"
LOGIN_API_URL = f"{BASE_URL}/landppt/api/auth/login"
REGISTER_API_URL = f"{BASE_URL}/landppt/api/auth/register"
CHECK_AUTH_URL = f"{BASE_URL}/landppt/api/auth/check"

def test_register_user(username, password, email=None):
    """测试注册用户"""
    logger.info(f"开始测试注册用户 - 用户名: {username}")
    
    data = {
        "username": username,
        "password": password
    }
    if email:
        data["email"] = email
    
    try:
        logger.debug(f"注册请求数据: {data}")
        response = requests.post(REGISTER_API_URL, data=data, allow_redirects=False)
        
        logger.info(f"注册响应状态码: {response.status_code}")
        logger.info(f"注册响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            logger.info("注册成功 - 收到302重定向")
            # 获取重定向URL
            redirect_url = response.headers.get('Location')
            logger.info(f"重定向到: {redirect_url}")
            
            # 检查是否有设置cookie
            cookies = response.cookies
            logger.info(f"设置的cookies: {dict(cookies)}")
            
            return True, cookies
        else:
            logger.info(f"注册失败 - 状态码: {response.status_code}")
            try:
                result = response.json()
                logger.info(f"注册失败响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                logger.info(f"注册失败响应文本: {response.text}")
            return False, None
            
    except Exception as e:
        logger.error(f"注册请求异常: {e}")
        return False, None

def test_login_api(username, password):
    """测试登录API并输出详细信息"""
    logger.info(f"开始测试登录API - 用户名: {username}")
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        logger.debug(f"登录请求数据: {data}")
        
        # 首先检查认证状态
        logger.info("检查当前认证状态...")
        check_response = requests.get(CHECK_AUTH_URL)
        logger.info(f"认证检查响应: {check_response.status_code}")
        try:
            check_result = check_response.json()
            logger.info(f"认证检查结果: {json.dumps(check_result, ensure_ascii=False, indent=2)}")
        except:
            logger.info(f"认证检查响应文本: {check_response.text}")
        
        # 发送登录请求，不允许重定向
        logger.info(f"发送登录请求到: {LOGIN_API_URL}")
        response = requests.post(LOGIN_API_URL, data=data, allow_redirects=False)
        
        logger.info(f"登录响应状态码: {response.status_code}")
        logger.info(f"登录响应头: {dict(response.headers)}")
        
        # 分析响应
        if response.status_code == 302:
            logger.info("登录成功 - 收到302重定向响应")
            
            # 获取重定向URL
            redirect_url = response.headers.get('Location')
            logger.info(f"重定向到: {redirect_url}")
            
            # 检查是否有设置cookie
            cookies = response.cookies
            logger.info(f"设置的cookies: {dict(cookies)}")
            
            # 如果有session_id cookie，验证它
            if 'session_id' in cookies:
                session_id = cookies['session_id']
                logger.info(f"获取到session_id: {session_id[:20]}...")
                
                # 使用session_id再次检查认证状态
                logger.info("使用新session_id检查认证状态...")
                auth_check = requests.get(CHECK_AUTH_URL, cookies={'session_id': session_id})
                logger.info(f"使用新session的认证检查响应: {auth_check.status_code}")
                try:
                    auth_result = auth_check.json()
                    logger.info(f"使用新session的认证检查结果: {json.dumps(auth_result, ensure_ascii=False, indent=2)}")
                except:
                    logger.info(f"使用新session的认证检查响应文本: {auth_check.text}")
            
            return True, cookies
            
        elif response.status_code == 200:
            logger.warning("登录失败 - 收到200响应（应该返回302）")
            
            # 尝试解析响应内容
            try:
                result = response.json()
                logger.info(f"登录失败响应JSON: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                logger.info(f"登录失败响应文本: {response.text}")
            
            # 检查是否有错误信息
            if 'error' in response.text.lower():
                logger.error("响应中包含错误信息")
            
            return False, None
            
        elif response.status_code == 401:
            logger.error("登录失败 - 401未授权")
            try:
                result = response.json()
                logger.info(f"401响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                logger.info(f"401响应文本: {response.text}")
            return False, None
            
        else:
            logger.error(f"意外的状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            logger.info(f"响应文本: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"登录请求异常: {e}")
        return False, None
    except Exception as e:
        logger.error(f"登录测试异常: {e}", exc_info=True)
        return False, None

def test_with_existing_session(session_cookies):
    """测试使用已有session的登录请求"""
    logger.info("测试使用已有session的登录请求...")
    
    data = {
        "username": "test_user_with_session",
        "password": "test_password"
    }
    
    try:
        response = requests.post(LOGIN_API_URL, data=data, cookies=session_cookies, allow_redirects=False)
        
        logger.info(f"带session的登录响应状态码: {response.status_code}")
        logger.info(f"带session的登录响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            logger.info("带session的登录请求返回302 - 正常")
        else:
            logger.warning(f"带session的登录请求返回 {response.status_code} - 可能存在问题")
            logger.info(f"响应文本: {response.text}")
            
    except Exception as e:
        logger.error(f"带session的登录测试异常: {e}")

def main():
    """主测试函数"""
    logger.info("=== 开始登录API调试测试 ===")
    
    # 测试用户名和密码
    test_username = "debug_test_user"
    test_password = "debug_test_password"
    test_email = "debug@test.com"
    
    # 第一步：尝试注册新用户
    logger.info("\n--- 第一步：注册新用户 ---")
    register_success, register_cookies = test_register_user(test_username, test_password, test_email)
    
    if register_success:
        logger.info("用户注册成功，使用注册后的session进行后续测试")
        session_cookies = register_cookies
    else:
        logger.info("用户注册失败或已存在，直接测试登录")
        session_cookies = None
    
    # 第二步：测试登录API
    logger.info("\n--- 第二步：测试登录API ---")
    login_success, login_cookies = test_login_api(test_username, test_password)
    
    # 第三步：如果有session，测试带session的登录
    if session_cookies or login_cookies:
        logger.info("\n--- 第三步：测试带已有session的登录 ---")
        cookies_to_use = login_cookies if login_cookies else session_cookies
        test_with_existing_session(cookies_to_use)
    
    # 第四步：测试错误的用户名密码
    logger.info("\n--- 第四步：测试错误的用户名密码 ---")
    test_login_api("wrong_user", "wrong_password")
    
    # 总结
    logger.info("\n=== 测试总结 ===")
    logger.info(f"注册测试: {'成功' if register_success else '失败'}")
    logger.info(f"登录测试: {'成功' if login_success else '失败'}")
    
    if not login_success:
        logger.error("登录API存在问题 - 应该返回302重定向但返回了200")
        logger.error("可能的原因：")
        logger.error("1. 登录接口被错误地放在了需要认证的中间件中")
        logger.error("2. 认证逻辑有误")
        logger.error("3. 用户名密码验证失败")
        sys.exit(1)
    else:
        logger.info("登录API测试通过")

if __name__ == "__main__":
    main()