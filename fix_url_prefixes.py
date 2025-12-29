#!/usr/bin/env python3
"""
LandPPT URL前缀检查和修复脚本
确保所有URL都使用硬编码的/landppt前缀
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class URLPrefixFixer:
    def __init__(self, base_path: str = "/landppt"):
        self.base_path = base_path
        self.issues_found = []
        self.files_modified = []
        
    def scan_directory(self, directory: str, extensions: List[str]) -> List[str]:
        """扫描指定目录中的文件"""
        files = []
        for ext in extensions:
            files.extend(Path(directory).rglob(f"*{ext}"))
        return [str(f) for f in files]
    
    def check_python_file(self, file_path: str) -> List[Dict]:
        """检查Python文件中的URL问题"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines, 1):
                # 检查重定向URL
                if 'RedirectResponse(url=' in line or 'redirect(' in line:
                    if self.base_path not in line:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': '重定向URL缺少/landppt前缀',
                            'type': 'redirect_missing_prefix'
                        })
                    elif f'"{self.base_path}/{self.base_path}' in line or f"'{self.base_path}/{self.base_path}" in line:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': '重定向URL有重复的前缀',
                            'type': 'redirect_duplicate_prefix'
                        })
                
                # 检查分享链接生成
                if 'share_url' in line and '=' in line:
                    if self.base_path not in line:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': '分享URL缺少/landppt前缀',
                            'type': 'share_url_missing_prefix'
                        })
                    elif f'"{self.base_path}/{self.base_path}' in line or f"'{self.base_path}/{self.base_path}" in line:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': '分享URL有重复的前缀',
                            'type': 'share_url_duplicate_prefix'
                        })
                        
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            
        return issues
    
    def check_javascript_file(self, file_path: str) -> List[Dict]:
        """检查JavaScript文件中的URL问题"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines, 1):
                # 检查fetch调用
                if 'fetch(' in line:
                    # 确保fetch调用使用基础路径
                    if '/landppt/api' not in line and 'getBasePath' not in line:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'issue': 'fetch调用可能缺少/landppt前缀',
                            'type': 'fetch_missing_prefix'
                        })
                        
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            
        return issues
    
    def check_html_file(self, file_path: str) -> List[Dict]:
        """检查HTML文件中的URL问题"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines, 1):
                # 检查href属性
                if 'href=' in line:
                    if '/landppt/' not in line and not line.strip().startswith('<!--'):
                        # 排除外部链接和特殊案例
                        if not any(ext in line for ext in ['http://', 'https://', 'mailto:', 'tel:']):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip(),
                                'issue': 'href属性可能缺少/landppt前缀',
                                'type': 'href_missing_prefix'
                            })
                
                # 检查src属性
                if 'src=' in line:
                    if '/landppt/' not in line and not line.strip().startswith('<!--'):
                        # 排除外部链接和特殊案例
                        if not any(ext in line for ext in ['http://', 'https://', 'data:', 'blob:']):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip(),
                                'issue': 'src属性可能缺少/landppt前缀',
                                'type': 'src_missing_prefix'
                            })
                            
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            
        return issues
    
    def fix_python_file(self, file_path: str) -> bool:
        """修复Python文件中的URL问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 修复重定向URL
            content = re.sub(
                r'RedirectResponse\(url=["\'](?!/landppt)([^"\']+)["\']',
                f'RedirectResponse(url="{self.base_path}\\1"',
                content
            )
            
            content = re.sub(
                r'redirect\(["\'](?!/landppt)([^"\']+)["\']',
                f'redirect("{self.base_path}\\1"',
                content
            )
            
            # 修复分享URL
            content = re.sub(
                r'share_url\s*=\s*["\'](?!/landppt)([^"\']+)["\']',
                f'share_url = "{self.base_path}\\1"',
                content
            )
            
            # 修复重复前缀
            content = re.sub(
                f'{self.base_path}/{self.baseppt}/',
                f'{self.base_path}/',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"修复文件失败 {file_path}: {e}")
            
        return False
    
    def run_full_check(self, project_root: str = ".") -> Dict:
        """运行完整的URL前缀检查"""
        print(f"开始检查项目: {project_root}")
        print(f"基础路径: {self.base_path}")
        
        # 扫描文件
        python_files = self.scan_directory(f"{project_root}/src", ['.py'])
        js_files = self.scan_directory(f"{project_root}/src", ['.js'])
        html_files = self.scan_directory(f"{project_root}/src", ['.html'])
        
        all_issues = []
        
        # 检查Python文件
        print(f"\n检查Python文件 ({len(python_files)}个文件)...")
        for file_path in python_files:
            issues = self.check_python_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        # 检查JavaScript文件
        print(f"\n检查JavaScript文件 ({len(js_files)}个文件)...")
        for file_path in js_files:
            issues = self.check_javascript_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        # 检查HTML文件
        print(f"\n检查HTML文件 ({len(html_files)}个文件)...")
        for file_path in html_files:
            issues = self.check_html_file(file_path)
            all_issues.extend(issues)
            if issues:
                print(f"  ❌ {file_path}: 发现 {len(issues)} 个问题")
            else:
                print(f"  ✅ {file_path}: 无问题")
        
        self.issues_found = all_issues
        
        # 生成报告
        report = {
            'total_files_checked': len(python_files) + len(js_files) + len(html_files),
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
    
    def auto_fix_issues(self) -> Dict:
        """自动修复发现的问题"""
        if not self.issues_found:
            return {'fixed': 0, 'errors': 0, 'details': []}
        
        fixed_count = 0
        error_count = 0
        details = []
        
        # 按文件分组问题
        files_with_issues = {}
        for issue in self.issues_found:
            file_path = issue['file']
            if file_path not in files_with_issues:
                files_with_issues[file_path] = []
            files_with_issues[file_path].append(issue)
        
        # 修复每个文件
        for file_path, issues in files_with_issues.items():
            try:
                if file_path.endswith('.py'):
                    if self.fix_python_file(file_path):
                        fixed_count += len(issues)
                        details.append(f"✅ 已修复 {file_path}: {len(issues)} 个问题")
                        self.files_modified.append(file_path)
                    else:
                        error_count += len(issues)
                        details.append(f"❌ 修复失败 {file_path}")
                else:
                    # 其他文件类型的修复逻辑可以在这里添加
                    error_count += len(issues)
                    details.append(f"⚠️  暂不支持修复 {file_path} 中的问题")
                    
            except Exception as e:
                error_count += len(issues)
                details.append(f"❌ 修复 {file_path} 时出错: {e}")
        
        return {
            'fixed': fixed_count,
            'errors': error_count,
            'details': details,
            'modified_files': self.files_modified
        }

def main():
    """主函数"""
    print("=" * 60)
    print("LandPPT URL前缀检查和修复工具")
    print("=" * 60)
    
    fixer = URLPrefixFixer()
    
    # 运行检查
    report = fixer.run_full_check()
    
    print(f"\n检查结果:")
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
        
        # 询问是否修复
        response = input("是否自动修复这些问题? (y/N): ").strip().lower()
        if response == 'y':
            fix_result = fixer.auto_fix_issues()
            print(f"\n修复结果:")
            print(f"  已修复: {fix_result['fixed']} 个问题")
            print(f"  修复失败: {fix_result['errors']} 个问题")
            
            if fix_result['details']:
                print(f"\n修复详情:")
                for detail in fix_result['details']:
                    print(f"  {detail}")
            
            if fix_result['modified_files']:
                print(f"\n修改的文件:")
                for file_path in fix_result['modified_files']:
                    print(f"  📄 {file_path}")
        else:
            print("跳过自动修复。")
    else:
        print("✅ 未发现URL前缀问题！")
    
    print(f"\n检查完成。")

if __name__ == "__main__":
    main()