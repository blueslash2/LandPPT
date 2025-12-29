#!/usr/bin/env python3
"""
批量修复HTML文件中的API调用路径前缀
"""

import os
import re
import glob

def fix_api_calls_in_file(filepath):
    """修复文件中的API调用路径"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复各种模式的API调用
        # 1. fetch('/api/...') -> fetch('/landppt/api/...')
        content = re.sub(r"fetch\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"fetch('/landppt\1')", content)
        
        # 2. fetch(`/api/...`) -> fetch(`/landppt/api/...`)
        content = re.sub(r"fetch\([`]([^`]*)[`]\)", lambda m: f"fetch(`{m.group(1).replace('/api/', '/landppt/api/')}`)", content)
        
        # 3. new EventSource('/api/...') -> new EventSource('/landppt/api/...')
        content = re.sub(r"new EventSource\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"new EventSource('/landppt\1')", content)
        
        # 4. new EventSource(`/api/...`) -> new EventSource(`/landppt/api/...`)
        content = re.sub(r"new EventSource\([`]([^`]*)[`]\)", lambda m: f"new EventSource(`{m.group(1).replace('/api/', '/landppt/api/')}`)", content)
        
        # 5. 处理window.location.origin + '/api/...' -> window.location.origin + '/landppt/api/...'
        content = re.sub(r"window\.location\.origin\s*\+\s*['\"](/api/[^'\"\)]*)['\"\)]", r"window.location.origin + '/landppt\1'", content)
        
        # 6. 处理triggerFileDownload('/api/...') -> triggerFileDownload('/landppt/api/...')
        content = re.sub(r"triggerFileDownload\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"triggerFileDownload('/landppt\1')", content)
        
        # 7. 处理复杂的模板字符串情况
        content = re.sub(r"url:\s*['\"](/api/[^'\"\)]*)['\"\)]", r"url: '/landppt\1'", content)
        content = re.sub(r"absoluteUrl:\s*['\"](/api/[^'\"\)]*)['\"\)]", r"absoluteUrl: '/landppt\1'", content)
        
        # 8. 处理if条件中的API路径
        content = re.sub(r"startsWith\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"startsWith('/landppt\1')", content)
        
        # 9. 处理includes中的API路径
        content = re.sub(r"includes\(['\"](/api/[^'\"\)]*)['\"\)]\)", r"includes('/landppt\1')", content)
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, []
        
    except Exception as e:
        return False, [f"Error processing {filepath}: {str(e)}"]

def main():
    """主函数"""
    print("开始批量修复API调用路径...")
    
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
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            total_files += 1
            changed, file_errors = fix_api_calls_in_file(filepath)
            
            if file_errors:
                errors.extend(file_errors)
            elif changed:
                fixed_files += 1
                print(f"✓ 已修复: {filepath}")
            else:
                print(f"- 无需修复: {filepath}")
        else:
            errors.append(f"文件不存在: {filepath}")
    
    # 输出结果
    print(f"\n=== 批量修复结果 ===")
    print(f"处理文件总数: {total_files}")
    print(f"修复完成文件: {fixed_files}")
    print(f"错误数量: {len(errors)}")
    
    if errors:
        print(f"\n=== 错误详情 ===")
        for error in errors:
            print(f"✗ {error}")
    
    print(f"\n=== 总结 ===")
    if len(errors) == 0:
        print("🎉 所有API调用路径已修复完成！")
        return True
    else:
        print(f"⚠️  还有 {len(errors)} 个错误需要处理")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)