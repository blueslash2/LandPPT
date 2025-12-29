#!/usr/bin/env python3
"""
完全修复所有剩余的API调用问题
"""

import os
import re

def fix_all_remaining_api_calls(filepath):
    """修复文件中所有剩余的API调用"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        issues_fixed = []
        
        # 1. 修复fetch调用中的所有API路径
        # 处理 fetch(`/api/...`) 格式
        content = re.sub(r'fetch\(`([^`]*)`/api/([^`]*)`\)', lambda m: f"fetch(`{m.group(1)}/landppt/api/{m.group(2)}`)", content)
        
        # 2. 修复return语句中的API路径
        content = re.sub(r'return\s+`([^`]*)`/api/([^`]*)`', lambda m: f"return `{m.group(1)}/landppt/api/{m.group(2)}`", content)
        
        # 3. 修复url:和absoluteUrl:中的路径
        content = re.sub(r'(url|absoluteUrl):\s*`([^`]*)`/api/([^`]*)`', r'\1: `\2/landppt/api/\3`', content)
        
        # 4. 修复const定义中的API路径
        content = re.sub(r'const\s+\w+\s*=\s*`([^`]*)`/api/([^`]*)`', lambda m: f"const {m.group(0).split('=')[0].strip()} = `{m.group(1)}/landppt/api/{m.group(2)}`", content)
        
        # 5. 修复triggerFileDownload中的路径
        content = re.sub(r'triggerFileDownload\(`([^`]*)`/api/([^`]*)`\)', lambda m: f"triggerFileDownload(`{m.group(1)}/landppt/api/{m.group(2)}`)", content)
        
        # 6. 修复startsWith和includes中的路径
        content = re.sub(r'(startsWith|includes)\(`([^`]*)`/api/([^`]*)`\)', r'\1(`\2/landppt/api/\3`)', content)
        
        # 7. 修复复杂的模板字符串拼接
        content = re.sub(r'`\$\{([^}]+)\}/api/([^`]*)`', r'`${\1}/landppt/api/\2`', content)
        
        # 8. 修复window.location.origin + 模板字符串
        content = re.sub(r'window\.location\.origin\s*\+\s*`([^`]*)`/api/([^`]*)`', lambda m: f"window.location.origin + `{m.group(1)}/landppt/api/{m.group(2)}`", content)
        
        # 9. 修复fetch中的复杂模板字符串
        content = re.sub(r'fetch\(`\$\{([^}]+)\}/api/([^`]*)`\)', r'fetch(`${\1}/landppt/api/\2`)', content)
        
        # 10. 修复所有其他模板字符串中的/api/
        content = re.sub(r'`([^`]*)`/api/([^`]*)`', lambda m: f"`{m.group(1)}/landppt/api/{m.group(2)}`" if '/landppt' not in m.group(0) else m.group(0), content)
        
        # 11. 修复特殊的landppt/tasks路径（这个应该保持为/api/landppt/）
        content = re.sub(r'/landppt/landppt/tasks/', r'/api/landppt/tasks/', content)
        
        # 12. 修复可能重复添加的/landppt/landppt
        content = re.sub(r'/landppt/landppt/api/', r'/landppt/api/', content)
        content = re.sub(r'/landppt/landppt/', r'/landppt/', content)
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            issues_fixed.append(f"修复了模板字符串中的API路径")
            
        return changes_made, issues_fixed
        
    except Exception as e:
        return False, [f"Error processing {filepath}: {str(e)}"]

def main():
    """主函数"""
    print("开始完全修复所有剩余的API调用问题...")
    
    # 需要修复的文件列表（只包含还有问题的文件）
    files_to_fix = [
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
            changed, issues = fix_all_remaining_api_calls(filepath)
            
            if issues:
                if "Error" in str(issues[0]):
                    errors.extend(issues)
                else:
                    fixed_files += 1
                    print(f"✓ 已修复: {filepath}")
                    if issues:
                        print(f"  修复内容: {', '.join(issues)}")
            elif changed:
                fixed_files += 1
                print(f"✓ 已修复: {filepath}")
            else:
                print(f"- 无需修复: {filepath}")
        else:
            errors.append(f"文件不存在: {filepath}")
    
    # 输出结果
    print(f"\n=== 完全修复结果 ===")
    print(f"处理文件总数: {total_files}")
    print(f"修复完成文件: {fixed_files}")
    print(f"错误数量: {len(errors)}")
    
    if errors:
        print(f"\n=== 错误详情 ===")
        for error in errors:
            print(f"✗ {error}")
    
    print(f"\n=== 总结 ===")
    if len(errors) == 0:
        print("🎉 所有剩余API调用已修复完成！")
        return True
    else:
        print(f"⚠️  还有 {len(errors)} 个错误需要处理")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)