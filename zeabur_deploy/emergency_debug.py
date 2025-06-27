#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急诊断工具 - 直接在云端环境中运行
"""

import os
import sys

def emergency_debug():
    """紧急诊断云端环境"""
    print("🚨 [紧急诊断] 云端环境检查")
    print("=" * 60)
    
    # 基础环境信息
    print(f"🔍 Python版本: {sys.version}")
    print(f"🔍 当前工作目录: {os.getcwd()}")
    print(f"🔍 当前脚本路径: {__file__}")
    print(f"🔍 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 列出当前目录内容
    try:
        current_files = os.listdir(os.getcwd())
        print(f"🔍 当前工作目录内容: {current_files}")
    except Exception as e:
        print(f"❌ 无法列出当前目录: {e}")
    
    # 列出脚本所在目录内容
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_files = os.listdir(script_dir)
        print(f"🔍 脚本所在目录内容: {script_files}")
    except Exception as e:
        print(f"❌ 无法列出脚本目录: {e}")
    
    # 查找knowledge_base
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base"),
        os.path.join(os.getcwd(), "knowledge_base"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base"),
        "/app/knowledge_base",
        "knowledge_base"
    ]
    
    print(f"\n🔍 测试所有可能的knowledge_base路径:")
    for i, path in enumerate(possible_paths, 1):
        exists = os.path.exists(path)
        is_dir = os.path.isdir(path) if exists else False
        print(f"   {i}. {path}")
        print(f"      存在: {'✅' if exists else '❌'}")
        print(f"      是目录: {'✅' if is_dir else '❌'}")
        
        if is_dir:
            try:
                files = os.listdir(path)
                print(f"      内容: {files}")
            except Exception as e:
                print(f"      无法列出内容: {e}")
    
    # 测试加载NotionHandler
    print(f"\n🔍 测试NotionHandler加载:")
    try:
        from notion_handler import NotionHandler
        config = {"notion": {"api_key": "test", "database_id": "test", 
                           "input_property_name": "输入", "output_property_name": "回复",
                           "template_property_name": "模板选择", "knowledge_base_property_name": "背景",
                           "model_property_name": "模型", "title_property_name": "标题"}}
        handler = NotionHandler(config)
        
        print("✅ NotionHandler加载成功")
        
        # 测试背景文件加载
        print(f"\n🔍 测试背景文件加载:")
        result = handler.get_context_from_knowledge_base(["AI效率中心"])
        print(f"🔍 结果长度: {len(result)} 字符")
        
    except Exception as e:
        print(f"❌ NotionHandler测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    emergency_debug() 