#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题诊断脚本 - 帮助确认背景文件加载问题的原因
"""

import os
import sys

def diagnose_knowledge_base_issue():
    """诊断背景文件加载问题"""
    print("🔍 Notion-LLM 背景文件加载问题诊断")
    print("=" * 60)
    
    # 检查1: 当前工作目录
    current_dir = os.getcwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 检查2: 本地knowledge_base目录
    local_kb_path = os.path.join(current_dir, "knowledge_base")
    print(f"\n📚 本地knowledge_base路径: {local_kb_path}")
    print(f"   存在: {'✅' if os.path.exists(local_kb_path) else '❌'}")
    
    if os.path.exists(local_kb_path):
        files = os.listdir(local_kb_path)
        print(f"   文件列表: {files}")
        
        # 检查具体文件
        for filename in ["AI效率中心.md", "业务理解.md"]:
            filepath = os.path.join(local_kb_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   {filename}: ✅ ({len(content)} 字符)")
            else:
                print(f"   {filename}: ❌ 不存在")
    
    # 检查3: zeabur_deploy目录的knowledge_base
    zeabur_kb_path = os.path.join(current_dir, "zeabur_deploy", "knowledge_base")
    print(f"\n📚 云端knowledge_base路径: {zeabur_kb_path}")
    print(f"   存在: {'✅' if os.path.exists(zeabur_kb_path) else '❌'}")
    
    if os.path.exists(zeabur_kb_path):
        files = os.listdir(zeabur_kb_path)
        print(f"   文件列表: {files}")
        
        # 检查具体文件
        for filename in ["AI效率中心.md", "业务理解.md"]:
            filepath = os.path.join(zeabur_kb_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   {filename}: ✅ ({len(content)} 字符)")
            else:
                print(f"   {filename}: ❌ 不存在")
    
    print(f"\n💡 诊断建议:")
    print("1. 如果文件存在但实际运行显示0字符，问题可能是：")
    print("   - Notion中'背景'字段的标签设置不正确")
    print("   - 标签名称不匹配（检查'AI效率中心'、'业务理解'等）")
    print("   - 运行的代码版本不是最新的")
    print()
    print("2. 建议检查步骤：")
    print("   - 在Notion中确认'背景'字段选择了正确的标签")
    print("   - 运行 python debug_context.py 查看详细调试信息")
    print("   - 如果是云端部署，确保最新代码已部署")

if __name__ == "__main__":
    diagnose_knowledge_base_issue() 