#!/usr/bin/env python3
"""
手动修复LandPPT中的URL前缀问题
只修复真正需要修复的问题
"""

import os
import re

def fix_error_template():
    """修复error.html中的返回首页链接"""
    file_path = "src/landppt/web/templates/error.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复第29行的返回首页链接
        if 'href="/landppt/web"' in content:
            content = content.replace('href="/landppt/web"', 'href="/landppt/home"')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复 {file_path}: 返回首页链接")
            return True
        else:
            print(f"ℹ️  {file_path}: 无需修复")
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

def fix_image_generation_test():
    """修复image_generation_test.html中的静态资源链接"""
    file_path = "src/landppt/web/templates/image_generation_test.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复占位符图片链接
        content = content.replace(
            "this.src='/static/images/placeholder.svg'",
            "this.src='/landppt/static/images/placeholder.svg'"
        )
        
        # 修复历史记录中的图片链接
        content = content.replace(
            "this.src='/static/images/placeholder.svg'",
            "this.src='/landppt/static/images/placeholder.svg'"
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复 {file_path}: 静态资源链接")
            return True
        else:
            print(f"ℹ️  {file_path}: 无需修复")
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

def fix_projects_list():
    """修复projects_list.html中的分页链接"""
    file_path = "src/landppt/web/templates/projects_list.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复分页链接 - 这些链接应该保持相对路径，因为它们在当前页面上下文中工作
        # 实际上这些链接是正确的，因为它们使用相对路径来保持查询参数
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复 {file_path}: 分页链接")
            return True
        else:
            print(f"ℹ️  {file_path}: 无需修复 - 分页链接使用相对路径是正确的")
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

def fix_project_slides_editor():
    """修复project_slides_editor.html中的关键链接"""
    file_path = "src/landppt/web/templates/project_slides_editor.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复导出功能的API端点
        content = content.replace(
            "fetch('/api/projects/",
            "fetch('/landppt/api/projects/"
        )
        
        # 修复图片预览链接
        content = content.replace(
            "img.src = imageUrl;",
            "img.src = imageUrl.startsWith('/') ? '/landppt' + imageUrl : imageUrl;"
        )
        
        # 修复CDN链接（这些不需要修复，因为是外部资源）
        # 修复JavaScript中的正则表达式（这些也不需要修复，因为它们是模式匹配）
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复 {file_path}: API端点和图片链接")
            return True
        else:
            print(f"ℹ️  {file_path}: 无需修复")
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

def fix_todo_board_with_editor():
    """修复todo_board_with_editor.html中的iframe链接"""
    file_path = "src/landppt/web/templates/todo_board_with_editor.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 这个文件中的iframe src是动态设置的，不需要修复
        print(f"ℹ️  {file_path}: 无需修复 - iframe src是动态设置的")
        return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

def main():
    """主函数 - 执行所有修复"""
    print("=" * 60)
    print("LandPPT URL前缀手动修复工具")
    print("=" * 60)
    
    fixes_applied = []
    
    # 执行修复
    if fix_error_template():
        fixes_applied.append("error.html")
    
    if fix_image_generation_test():
        fixes_applied.append("image_generation_test.html")
    
    if fix_projects_list():
        fixes_applied.append("projects_list.html")
    
    if fix_project_slides_editor():
        fixes_applied.append("project_slides_editor.html")
    
    if fix_todo_board_with_editor():
        fixes_applied.append("todo_board_with_editor.html")
    
    # 总结
    print(f"\n修复完成！")
    if fixes_applied:
        print(f"已修复的文件:")
        for file_path in fixes_applied:
            print(f"  📄 {file_path}")
    else:
        print("没有需要修复的文件")
    
    print(f"\n建议：运行验证脚本来确认修复结果")

if __name__ == "__main__":
    main()