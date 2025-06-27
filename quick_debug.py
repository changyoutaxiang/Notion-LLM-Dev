#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速调试工具 - 检查标签和文件匹配情况
"""

import os
import sys

def quick_debug():
    """快速调试背景文件问题"""
    print("🔍 快速调试 - 检查标签和文件匹配")
    print("=" * 50)
    
    # 检查knowledge_base目录
    kb_path = "knowledge_base"
    if os.path.exists(kb_path):
        print(f"✅ 本地knowledge_base目录存在")
        files = [f for f in os.listdir(kb_path) if f.endswith('.md')]
        print(f"📁 可用的.md文件:")
        for i, file in enumerate(files, 1):
            filename_without_ext = file[:-3]  # 去掉.md后缀
            print(f"   {i}. 文件名: '{filename_without_ext}'")
            print(f"      完整文件名: '{file}'")
            
            # 显示文件名的字符详情
            chars = [f"'{c}'" if c != ' ' else "'空格'" for c in filename_without_ext]
            print(f"      字符详情: {' + '.join(chars)}")
    else:
        print(f"❌ 本地knowledge_base目录不存在")
    
    # 检查云端版本
    zeabur_kb_path = "zeabur_deploy/knowledge_base"
    if os.path.exists(zeabur_kb_path):
        print(f"\n✅ 云端knowledge_base目录存在")
        files = [f for f in os.listdir(zeabur_kb_path) if f.endswith('.md')]
        print(f"📁 云端可用的.md文件:")
        for i, file in enumerate(files, 1):
            filename_without_ext = file[:-3]
            print(f"   {i}. 文件名: '{filename_without_ext}'")
    else:
        print(f"❌ 云端knowledge_base目录不存在")
    
    print(f"\n💡 请检查:")
    print(f"1. 您在Notion中的'背景'标签是否与上面显示的文件名完全一致")
    print(f"2. 特别注意空格、标点符号等细节")
    print(f"3. 如果标签正确，可能需要等待云端重新部署")
    
    # 测试一些常见的标签变体
    print(f"\n🧪 测试常见标签变体:")
    test_tags = [
        "AI效率中心",
        "AI 效率中心", 
        "业务理解",
        "业务 理解"
    ]
    
    for tag in test_tags:
        safe_tag = tag.replace("/", "_").replace("\\", "_")
        file_path = os.path.join(kb_path, f"{safe_tag}.md")
        exists = "✅" if os.path.exists(file_path) else "❌"
        print(f"   标签 '{tag}' -> 文件 '{safe_tag}.md' {exists}")

if __name__ == "__main__":
    quick_debug() 