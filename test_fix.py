#!/usr/bin/env python3
"""
测试修复后的API端点是否正常工作
"""

import requests
import json

def test_api_endpoints():
    """测试关键的API端点"""
    base_url = "http://localhost:8000/landppt"
    project_id = "91aa8f75-8032-4e05-a165-22c4ce5c6f97"  # 使用日志中的项目ID
    
    endpoints_to_test = [
        f"/api/projects/{project_id}/todo",
        f"/api/projects/{project_id}",
        "/api/health",
        "/api/scenarios"
    ]
    
    print("测试API端点...")
    
    for endpoint in endpoints_to_test:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            print(f"\n测试: {url}")
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('content-type', '未知')}")
            
            if response.status_code == 200:
                try:
                    # 尝试解析为JSON
                    json_data = response.json()
                    print(f"JSON解析: 成功")
                    print(f"数据预览: {str(json_data)[:200]}...")
                except json.JSONDecodeError as e:
                    print(f"JSON解析: 失败 - {e}")
                    print(f"响应内容前200字符: {response.text[:200]}")
            else:
                print(f"错误响应: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
        except Exception as e:
            print(f"意外错误: {e}")

if __name__ == "__main__":
    test_api_endpoints()