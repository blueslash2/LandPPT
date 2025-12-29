#!/usr/bin/env python3
"""
最终修复剩余的API调用和getBasePath问题
"""

import os
import re

def fix_remaining_issues_in_file(filepath):
    """修复文件中的剩余问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        issues_fixed = []
        
        # 1. 修复fetch调用中的baseUrl变量问题
        if 'baseUrl' in content and '/api/' in content:
            # 处理 ${baseUrl}/api/... 这种情况
            content = re.sub(r'\$\{baseUrl\}/api/', r'/landppt/api/', content)
            issues_fixed.append("修复了baseUrl变量中的API路径")
        
        # 2. 修复剩余的简单API路径
        # 处理 fetch('/api/...') 但还没有/landppt前缀的
        content = re.sub(r"fetch\(['\"](/api/[^'\"\)]*)['\"\)]\)(?!\s*#\s*已修复)", r"fetch('/landppt\1')", content)
        
        # 3. 修复模板字符串中的API路径
        content = re.sub(r"fetch\([`]([^`]*)[`]\)", lambda m: f"fetch(`{m.group(1).replace('/api/', '/landppt/api/')}`)", content)
        
        # 4. 修复window.location.origin + '/api/...'
        content = re.sub(r"window\.location\.origin\s*\+\s*['\"](/api/[^'\"\)]*)['\"\)]", r"window.location.origin + '/landppt\1'", content)
        
        # 5. 修复triggerFileDownload调用
        content = re.sub(r"triggerFileDownload\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"triggerFileDownload('/landppt\1')", content)
        
        # 6. 修复字符串中的API路径（不在fetch中）
        content = re.sub(r"['\"](/api/[^'\"\)]*)['\"\)]", lambda m: f"'/landppt{m.group(1)}'" if '/landppt' not in m.group(1) else m.group(0), content)
        
        # 7. 修复url:和absoluteUrl:中的路径
        content = re.sub(r"(url|absoluteUrl):\s*['\"](/api/[^'\"\)]*)['\"\)]", r"\1: '/landppt\2'", content)
        
        # 8. 修复startsWith和includes中的路径
        content = re.sub(r"(startsWith|includes)\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"\1('/landppt\2')", content)
        
        # 9. 修复return语句中的路径
        content = re.sub(r"return\s+['\"](/api/[^'\"\)]*)['\"\)]", r"return '/landppt\1'", content)
        
        # 10. 修复new EventSource中的路径
        content = re.sub(r"new EventSource\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"new EventSource('/landppt\1')", content)
        content = re.sub(r"new EventSource\([`]([^`]*)[`]\)", lambda m: f"new EventSource(`{m.group(1).replace('/api/', '/landppt/api/')}`)", content)
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, issues_fixed
        
    except Exception as e:
        return False, [f"Error processing {filepath}: {str(e)}"]

def remove_getbasepath_and_meta(filepath):
    """移除getBasePath函数和meta标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        issues_fixed = []
        
        # 移除getBasePath函数定义
        getbasepath_pattern = r'<script>\s*//\s*获取基础路径函数\s*function getBasePath\(\) \{[^}]+\}\s*</script>'
        if re.search(getbasepath_pattern, content, re.DOTALL):
            content = re.sub(getbasepath_pattern, '', content, flags=re.DOTALL)
            issues_fixed.append("移除了getBasePath函数定义")
        
        # 移除meta标签
        meta_pattern = r'<meta name="app-base-path"[^>]*>'
        if re.search(meta_pattern, content):
            content = re.sub(meta_pattern, '', content)
            issues_fixed.append("移除了meta标签")
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, issues_fixed
        
    except Exception as e:
        return False, [f"Error processing {filepath}: {str(e)}"]

def main():
    """主函数"""
    print("开始最终修复剩余的API调用和getBasePath问题...")
    
    # 需要修复的文件列表
    files_to_fix = [
        'src/landppt/web/templates/ai_config.html',
        'src/landppt/web/templates/project_dashboard.html',
        'src/landppt/web/templates/project_detail.html',
        'src/landppt/web/templates/project_slides_editor.html',
        'src/landppt/web/templates/projects_list.html',
        'src/landppt/web/templates/research_status.html',
        'src/landppt/web/templates/template_selection.html',
        'src/landppt/web/templates/todo_board.html',
        'src/landppt/web/templates/todo_board_with_editor.html'
    ]
    
    total_files = 0
    fixed_files = 0
    errors = []
    all_issues_fixed = []
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            total_files += 1
            
            # 先修复API调用问题
            api_changed, api_issues = fix_remaining_issues_in_file(filepath)
            
            # 再修复getBasePath和meta标签问题
            gb_changed, gb_issues = remove_getbasepath_and_meta(filepath)
            
            if api_issues:
                all_issues_fixed.extend(api_issues)
            if gb_issues:
                all_issues_fixed.extend(gb_issues)
            
            if api_changed or gb_changed:
                fixed_files += 1
                print(f"✓ 已修复: {filepath}")
                if all_issues_fixed:
                    print(f"  修复内容: {', '.join(all_issues_fixed)}")
            else:
                print(f"- 无需修复: {filepath}")
                
            all_issues_fixed = []  # 重置 for next file
        else:
            errors.append(f"文件不存在: {filepath}")
    
    # 输出结果
    print(f"\n=== 最终修复结果 ===")
    print(f"处理文件总数: {total_files}")
    print(f"修复完成文件: {fixed_files}")
    print(f"错误数量: {len(errors)}")
    
    if errors:
        print(f"\n=== 错误详情 ===")
        for error in errors:
            print(f"✗ {error}")
    
    print(f"\n=== 总结 ===")
    if len(errors) == 0:
        print("🎉 所有剩余问题已修复完成！")
        return True
    else:
        print(f"⚠️  还有 {len(errors)} 个错误需要处理")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)