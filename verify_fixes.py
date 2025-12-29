#!/usr/bin/env python3
"""
验证LandPPT URL前缀修复结果
检查是否还有重复前缀问题
"""

import os
import re
from pathlib import Path
from typing import List, Dict

class URLPrefixVerifier:
    def __init__(self, base_path: str = "/landppt"):
        self.base_path = base_path
        self.issues_found = []
        
    def scan_files(self, directory: str, extensions: List[str]) -> List[str]:
        """扫描指定目录中的文件"""
        files = []
        for ext in extensions:
            files.extend(Path(directory).rglob(f"*{ext}"))
        return [str(f) for f in files]
    
    def check_for_duplicate_prefixes(self, content: str, file_path: str) -> List[Dict]:
        """检查重复的前缀问题"""
        issues = []
        lines = content.split('\n')
        
        duplicate_pattern = f"{self.base_path}/{self.base_path}"
        
        for i, line in enumerate(lines, 1):
            if duplicate_pattern in line:
                issues.append({
                    'file': file_path,
                    'line': i,
                    'content': line.strip(),
                    'issue': f'发现重复的前缀: {duplicate_pattern}',
                    'type': 'duplicate_prefix'
                })
        
        return issues
    
    def check_redirect_urls(self, content: str, file_path: str) -> List[Dict]:
        """检查重定向URL是否正确"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查重定向URL
            if 'RedirectResponse(url=' in line or 'redirect(' in line:
                # 应该包含基础路径
                if self.base_path not in line:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'content': line.strip(),
                        'issue': '重定向URL缺少/landppt前缀',
                        'type': 'redirect_missing_prefix'
                    })
                # 检查重复前缀
                elif f'"{self.base_path}/{self.base_path}' in line or f"'{self.base_path}/{self.base_path}" in line:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'content': line.strip(),
                        'issue': '重定向URL有重复的前缀',
                        'type': 'redirect_duplicate_prefix'
                    })
        
        return issues
    
    def check_static_resources(self, content: str, file_path: str) -> List[Dict]:
        """检查静态资源链接"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查静态资源链接
            if ('src=' in line or 'href=' in line) and '/static/' in line:
                # 应该包含基础路径
                if f'{self.base_path}/static/' not in line:
                    # 排除一些特殊情况
                    if not any(skip in line for skip in ['${', 'javascript:', 'http://', 'https://']):
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': '静态资源链接缺少/landppt前缀',
                            'type': 'static_resource_missing_prefix'
                        })
        
        return issues
    
    def verify_file(self, file_path: str) -> List[Dict]:
        """验证单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # 检查重复前缀
            issues.extend(self.check_for_duplicate_prefixes(content, file_path))
            
            # 如果是Python文件，检查重定向URL
            if file_path.endswith('.py'):
                issues.extend(self.check_redirect_urls(content, file_path))
            
            # 如果是HTML文件，检查静态资源
            if file_path.endswith('.html'):
                issues.extend(self.check_static_resources(content, file_path))
            
            return issues
            
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return []
    
    def run_verification(self, project_root: str = ".") -> Dict:
        """运行验证"""
        print(f"开始验证项目: {project_root}")
        print(f"基础路径: {self.base_path}")
        
        # 扫描关键文件
        python_files = self.scan_files(f"{project_root}/src", ['.py'])
        html_files = self.scan_files(f"{project_root}/src", ['.html'])
        js_files = self.scan_files(f"{project_root}/src", ['.js'])
        
        all_issues = []
        
        # 验证Python文件
        print(f"\n验证Python文件 ({len(python_files)}个文件)...")
        for file_path in python_files:
            issues = self.verify_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        # 验证HTML文件
        print(f"\n验证HTML文件 ({len(html_files)}个文件)...")
        for file_path in html_files:
            issues = self.verify_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        # 验证JavaScript文件
        print(f"\n验证JavaScript文件 ({len(js_files)}个文件)...")
        for file_path in js_files:
            issues = self.verify_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        # 生成报告
        report = {
            'total_files_checked': len(python_files) + len(html_files) + len(js_files),
            'total_issues': len(all_issues),
            'issues_by_type': {},
            'issues': all_issues
        }
        
        # 按问题类型分类
        for issue in all_issues:
            issue_type = issue['type']
            if issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue_type] = 0
            report['issues_by_type'][issue_type] += 1
        
        return report
    
    def check_specific_patterns(self) -> Dict:
        """检查特定的URL模式"""
        results = {
            'redirects_with_prefix': [],
            'static_resources_with_prefix': [],
            'api_calls_with_prefix': [],
            'share_urls_with_prefix': []
        }
        
        # 扫描所有Python文件
        python_files = self.scan_files("./src", ['.py'])
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # 检查重定向URL
                    if 'RedirectResponse(url=' in line and self.base_path in line:
                        results['redirects_with_prefix'].append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip()
                        })
                    
                    # 检查分享URL
                    if 'share_url' in line and self.base_path in line:
                        results['share_urls_with_prefix'].append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip()
                        })
                    
                    # 检查API调用
                    if 'fetch(' in line and f'{self.base_path}/api' in line:
                        results['api_calls_with_prefix'].append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip()
                        })
            
            except Exception as e:
                continue
        
        # 扫描HTML文件
        html_files = self.scan_files("./src", ['.html'])
        
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # 检查静态资源
                    if ('src=' in line or 'href=' in line) and f'{self.base_path}/static' in line:
                        results['static_resources_with_prefix'].append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip()
                        })
            
            except Exception as e:
                continue
        
        return results

def main():
    """主函数"""
    print("=" * 60)
    print("LandPPT URL前缀验证工具")
    print("=" * 60)
    
    verifier = URLPrefixVerifier()
    
    # 运行验证
    report = verifier.run_verification()
    
    print(f"\n验证结果:")
    print(f"  检查文件总数: {report['total_files_checked']}")
    print(f"  发现问题总数: {report['total_issues']}")
    
    if report['total_issues'] > 0:
        print(f"\n问题类型分布:")
        for issue_type, count in report['issues_by_type'].items():
            print(f"  {issue_type}: {count} 个")
        
        print(f"\n详细问题列表:")
        for issue in report['issues']:
            print(f"  📍 {issue['file']}:{issue['line']}")
            print(f"     问题: {issue['issue']}")
            print(f"     内容: {issue['content'][:100]}...")
            print()
        
        return False  # 表示发现问题
    else:
        print("✅ 未发现URL前缀问题！")
        
        # 检查特定的正确模式
        print(f"\n检查正确的URL模式...")
        patterns = verifier.check_specific_patterns()
        
        print(f"  重定向URL使用前缀: {len(patterns['redirects_with_prefix'])} 个")
        print(f"  静态资源使用前缀: {len(patterns['static_resources_with_prefix'])} 个")
        print(f"  API调用使用前缀: {len(patterns['api_calls_with_prefix'])} 个")
        print(f"  分享URL使用前缀: {len(patterns['share_urls_with_prefix'])} 个")
        
        if any(patterns.values()):
            print(f"\n示例（正确的URL模式）:")
            if patterns['redirects_with_prefix']:
                print(f"  重定向: {patterns['redirects_with_prefix'][0]['file']}:{patterns['redirects_with_prefix'][0]['line']}")
            if patterns['static_resources_with_prefix']:
                print(f"  静态资源: {patterns['static_resources_with_prefix'][0]['file']}:{patterns['static_resources_with_prefix'][0]['line']}")
        
        return True  # 表示验证通过

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)