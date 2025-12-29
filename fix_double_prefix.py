#!/usr/bin/env python3
"""
修复重复的/landppt/landppt路径问题
"""

import os
import re

def fix_double_prefix_in_file(filepath):
    """修复文件中的重复路径前缀"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复重复的/landppt/landppt路径 -> /landppt/api/...
        content = re.sub(r'/landppt/landppt/api/', r'/landppt/api/', content)
        content = re.sub(r'/landppt/landppt/', r'/landppt/', content)
        
        # 修复其他重复前缀情况
        content = re.sub(r"'/landppt/landppt/api/", r"'/landppt/api/", content)
        content = re.sub(r"`/landppt/landppt/api/", r"`/landppt/api/", content)
        content = re.sub(r"window\.location\.origin\s*\+\s*'/landppt/landppt/api/", r"window.location.origin + '/landppt/api/", content)
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, []
        
    except Exception as e:
        return False, [f"Error processing {filepath}: {str(e)}"]

def main():
    """主函数"""
    print("开始修复重复的/landppt/landppt路径问题...")
    
    # 需要修复的文件列表
    files_to_fix = [
        'src/landppt/web/templates/ai_config.html',
        'src/landppt/web/templates/project_slides_editor.html',
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
            changed, file_errors = fix_double_prefix_in_file(filepath)
            
            if file_errors:
                errors.extend(file_errors)
            elif changed:
                fixed_files += 1
                print(f"✓ 已修复重复路径: {filepath}")
            else:
                print(f"- 无需修复: {filepath}")
        else:
            errors.append(f"文件不存在: {filepath}")
    
    # 输出结果
    print(f"\n=== 修复重复路径结果 ===")
    print(f"处理文件总数: {total_files}")
    print(f"修复完成文件: {fixed_files}")
    print(f"错误数量: {len(errors)}")
    
    if errors:
        print(f"\n=== 错误详情 ===")
        for error in errors:
            print(f"✗ {error}")
    
    print(f"\n=== 总结 ===")
    if len(errors) == 0:
        print("🎉 所有重复路径问题已修复完成！")
        return True
    else:
        print(f"⚠️  还有 {len(errors)} 个错误需要处理")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)