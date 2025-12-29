#!/usr/bin/env python3
"""
修复project_slides_editor.html中的剩余API调用问题
"""

import re

def fix_project_slides_editor():
    """修复project_slides_editor.html中的API调用"""
    filepath = 'src/landppt/web/templates/project_slides_editor.html'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复第6184行的API调用
        content = re.sub(
            r'const response = await fetch\(`/api/projects/\$\{targetProjectId\}/slides/\$\{currentSlideIndex \+ 1\}/auto-repair-layout`\)',
            r'const response = await fetch(`/landppt/api/projects/${targetProjectId}/slides/${currentSlideIndex + 1}/auto-repair-layout`)',
            content
        )
        
        # 修复第8846行的API调用
        content = re.sub(
            r'fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/slides/\$\{slideIndex \+ 1\}/regenerate`\)',
            r'fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/slides/${slideIndex + 1}/regenerate`)',
            content
        )
        
        # 修复第8586行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/slides/batch-save`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/slides/batch-save`)',
            content
        )
        
        # 修复第8660行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/slides/cleanup`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/slides/cleanup`)',
            content
        )
        
        # 修复第8714行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/slides/\$\{slideIndex\}/save`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/slides/${slideIndex}/save`)',
            content
        )
        
        # 修复第8749行的API调用
        content = re.sub(
            r'triggerFileDownload\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/export/pdf`\)',
            r'triggerFileDownload(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/export/pdf`)',
            content
        )
        
        # 修复第8770行的API调用
        content = re.sub(
            r'// window\.open\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/export/pdf\?fallback=true`, \'_blank\'\)',
            r'// window.open(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/export/pdf?fallback=true`, \'_blank\')',
            content
        )
        
        # 修复第8846行的API调用（重复的，但确保修复）
        content = re.sub(
            r'const downloadUrl = data\.download_url \|\| `\$\{window\.location\.origin\}/api/landppt/tasks/\$\{taskId\}/download`',
            r'const downloadUrl = data.download_url || `${window.location.origin}/api/landppt/tasks/${taskId}/download`',
            content
        )
        
        # 修复第8929行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/export/pptx-images`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/export/pptx-images`)',
            content
        )
        
        # 修复第8981行的API调用
        content = re.sub(
            r'downloadLink\.href = `\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/export/html`',
            r'downloadLink.href = `${window.location.origin}/landppt/api/projects/{{ project.project_id }}/export/html`',
            content
        )
        
        # 修复第9089行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/share/generate`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/share/generate`)',
            content
        )
        
        # 修复第9183行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/share/disable`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/share/disable`)',
            content
        )
        
        # 修复第10544行的return语句
        content = re.sub(
            r'return `\$\{window\.location\.origin\}/api/image/view/\$\{image\.id\}`',
            r'return `${window.location.origin}/landppt/api/image/view/${image.id}`',
            content
        )
        
        # 修复第10549行的return语句
        content = re.sub(
            r'return image\.url\.startsWith\(\'/\'\) \? image\.url : `\$\{window\.location\.origin\}/api/image/view/\$\{image\.url\}`',
            r'return image.url.startsWith(\'/\') ? image.url : `${window.location.origin}/landppt/api/image/view/${image.url}`',
            content
        )
        
        # 修复第10567行的const定义
        content = re.sub(
            r'const apiUrl = `\$\{window\.location\.origin\}/api/image/view/\$\{imageId\}`',
            r'const apiUrl = `${window.location.origin}/landppt/api/image/view/${imageId}`',
            content
        )
        
        # 修复第11270行的return语句
        content = re.sub(
            r'return `\$\{window\.location\.origin\}/api/image/\$\{imageId\}`',
            r'return `${window.location.origin}/landppt/api/image/${imageId}`',
            content
        )
        
        # 修复第11273行的return语句
        content = re.sub(
            r'return `\$\{window\.location\.origin\}/api/image/\$\{imageId\}`',
            r'return `${window.location.origin}/landppt/api/image/${imageId}`',
            content
        )
        
        # 修复第11735行的const定义
        content = re.sub(
            r'const imageUrl = `\$\{window\.location\.origin\}/api/image/view/\$\{image\.image_id\}`',
            r'const imageUrl = `${window.location.origin}/landppt/api/image/view/${image.image_id}`',
            content
        )
        
        # 修复第11826行的url定义
        content = re.sub(
            r'url: `\$\{window\.location\.origin\}/api/image/view/\$\{image\.image_id\}`',
            r'url: `${window.location.origin}/landppt/api/image/view/${image.image_id}`',
            content
        )
        
        # 修复第11874行的absoluteUrl定义
        content = re.sub(
            r'absoluteUrl: `\$\{window\.location\.origin\}/api/image/view/\$\{imageId\}`',
            r'absoluteUrl: `${window.location.origin}/landppt/api/image/view/${imageId}`',
            content
        )
        
        # 修复第13026行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/speech-script/generate`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/speech-script/generate`)',
            content
        )
        
        # 修复第13235行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/speech-script/export`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/speech-script/export`)',
            content
        )
        
        # 修复第13338行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/speech-scripts/slide/\$\{slideIndex\}`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/speech-scripts/slide/${slideIndex}`)',
            content
        )
        
        # 修复第13396行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/speech-script/generate`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/speech-script/generate`)',
            content
        )
        
        # 修复第13669行的API调用
        content = re.sub(
            r'const response = await fetch\(`\$\{window\.location\.origin\}/api/projects/\{\{ project\.project_id \}\}/speech-scripts/slide/\$\{slideIndex\}`\)',
            r'const response = await fetch(`${window.location.origin}/landppt/api/projects/{{ project.project_id }}/speech-scripts/slide/${slideIndex}`)',
            content
        )
        
        changes_made = content != original_content
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, f"修复了{filepath}中的API调用路径"
        
    except Exception as e:
        return False, f"Error processing {filepath}: {str(e)}"

if __name__ == "__main__":
    success, message = fix_project_slides_editor()
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
    exit(0 if success else 1)